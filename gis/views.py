from .models import Country, City, Activity
from django import forms
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.gis.db.models.functions import GeomOutputGeoFunc, Transform
from django.urls import reverse
import json
import os
from django.conf import settings
import xml.etree.ElementTree as ET
from django.contrib.gis.gdal import DataSource
from django.core.paginator import Paginator

try:
    from fitparse import FitFile
except ImportError:
    FitFile = None

class BufferGeom(GeomOutputGeoFunc):
    """ST_BUFFER postgis function returning only geometry."""
    function = "ST_BUFFER"
    template = '%(function)s(%(expressions)s)'


def country_buffer_geojson(request):
    # Récupère le premier pays (ou un pays spécifique via un paramètre GET)
    country_id = request.GET.get('id')
    if country_id:
        countries = Country.objects.filter(id=country_id)
    else:
        countries = Country.objects.all()[:1]
    countries = countries.annotate(
        _buffer_geom=Transform(BufferGeom('geom', 25000), 4326),
        _geom_4326=Transform('geom', 4326)
    )
    features = []
    for country in countries:
        buffer_geom = country._buffer_geom.geojson if country._buffer_geom else None
        orig_geom = country._geom_4326.geojson if country._geom_4326 else None
        # Feature pour la géométrie initiale
        features.append({
            "type": "Feature",
            "id": f"{country.id}_original",
            "properties": {"name": country.name, "type": "original"},
            "geometry": json.loads(orig_geom) if orig_geom else None
        })
        # Feature pour le buffer
        features.append({
            "type": "Feature",
            "id": f"{country.id}_buffer",
            "properties": {"name": country.name, "type": "buffer"},
            "geometry": json.loads(buffer_geom) if buffer_geom else None
        })
    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson, safe=False)

def country_buffer_map(request):
    country_id = request.GET.get('id')
    countries = Country.objects.all().order_by('name')
    if country_id:
        country = countries.filter(id=country_id).first()
    else:
        country = countries.first()
    country_name = country.name if country else ""
    return render(request, 'gis/country_buffer_map.html', {
        'country_name': country_name,
        'countries': countries,
        'selected_id': int(country_id) if country_id else (country.id if country else None)
    })

def city_list_geojson(request):
    # Ajout de la pagination/batch
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 500))
    cities_qs = City.objects.all()
    paginator = Paginator(cities_qs, page_size)
    cities = paginator.get_page(page)
    features = []
    for city in cities:
        geom = city.geom_4326.geojson if city.geom_4326 else None
        features.append({
            "type": "Feature",
            "id": city.id,
            "properties": {"name": city.name},
            "geometry": json.loads(geom) if geom else None
        })
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "page": page,
        "num_pages": paginator.num_pages,
        "has_next": cities.has_next(),
        "has_previous": cities.has_previous(),
    }
    return JsonResponse(geojson, safe=False)

def city_list_map(request):
    # On affiche la carte, le chargement des villes se fait désormais en AJAX/batch côté JS
    return render(request, 'gis/city_list_map.html')

def home(request):
    return render(request, 'gis/home.html')


class GpxImportForm(forms.Form):
    name = forms.CharField(max_length=100)
    date = forms.DateField()
    gpx_file = forms.FileField()
    method = forms.ChoiceField(
        choices=[('datasource', 'GDAL DataSource'), ('xml', 'Parseur XML')],
        label="Méthode d'import",
        initial='datasource',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


def import_gpx_activity(request):
    error = None
    if request.method == 'POST':
        form = GpxImportForm(request.POST, request.FILES)
        if form.is_valid():
            gpx_file = request.FILES['gpx_file']
            method = form.cleaned_data['method']
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as tmp:
                    for chunk in gpx_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                points = []
                if method == 'datasource':
                    ds = DataSource(tmp_path)
                    for layer in ds:
                        if layer.name.lower().endswith('track_points') or layer.name.lower() == 'track_points':
                            for feat in layer:
                                geom = feat.geom
                                if geom:
                                    if geom.geom_type.name == 'LineString':
                                        for pt in geom:
                                            if pt.x is not None and pt.y is not None:
                                                if hasattr(pt, 'z') and pt.z is not None and len(pt.coords) == 3:
                                                    points.append((pt.x, pt.y, pt.z))
                                                else:
                                                    points.append((pt.x, pt.y, feat.get("ele")))
                                    elif geom.geom_type.name == 'Point':
                                        if geom.x is not None and geom.y is not None:
                                            if hasattr(geom, 'z') and geom.z is not None:
                                                points.append((geom.x, geom.y, geom.z))
                                            else:
                                                points.append((geom.x, geom.y, feat.get("ele")))
                            break
                elif method == 'xml':
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(tmp_path)
                    root = tree.getroot()
                    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
                    for trk in root.findall('default:trk', ns):
                        for trkseg in trk.findall('default:trkseg', ns):
                            for trkpt in trkseg.findall('default:trkpt', ns):
                                lat = trkpt.attrib.get('lat')
                                lon = trkpt.attrib.get('lon')
                                ele_elem = trkpt.find('default:ele', ns)
                                if lat and lon:
                                    z = float(ele_elem.text) if ele_elem is not None else 0
                                    points.append((float(lon), float(lat), z))
                os.unlink(tmp_path)
                if points:
                    from django.contrib.gis.geos import LineString
                    route = LineString(points, srid=4326)
                    route.transform(3857)
                    Activity.objects.create(
                        name=form.cleaned_data['name'],
                        date=form.cleaned_data['date'],
                        route=route
                    )
                    return HttpResponseRedirect(reverse('admin:my_gis_app_activity_changelist'))
                else:
                    error = "Aucun point GPS trouvé dans le fichier GPX."
            except Exception as e:
                error = f"Erreur lors de la lecture du fichier GPX : {e}"
    else:
        form = GpxImportForm()
    return render(request, 'gis/import_gpx_activity.html', {'form': form, 'error': error})

def activity_list(request):
    activities = Activity.objects.order_by('-date', 'name')
    return render(request, 'gis/activity_list.html', {'activities': activities})

def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    # On transforme la géométrie en GeoJSON (EPSG:4326 pour Leaflet)
    route_4326 = activity.route.transform(4326, clone=True)
    geojson = route_4326.geojson
    # Calcul de la longueur en kilomètres (SRID 2154 = mètres, projection Lambert-93)
    route_2154 = activity.route.transform(2154, clone=True)
    length_km = route_2154.length / 1000

    # Calcul de l'altitude min, max, moyenne à partir du LineString (si Z présent)
    altitude_min = altitude_max = altitude_moy = None
    coords = list(activity.route.coords)
    elevations = [c[2] for c in coords if len(c) > 2 and c[2] is not None]
    if elevations:
        altitude_min = min(elevations)
        altitude_max = max(elevations)
        altitude_moy = sum(elevations) / len(elevations)

    return render(request, 'gis/activity_detail.html', {
        'activity': activity,
        'geojson': geojson,
        'length_km': length_km,
        'altitude_min': altitude_min,
        'altitude_max': altitude_max,
        'altitude_moy': altitude_moy,
    })
