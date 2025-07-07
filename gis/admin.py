from django.contrib.gis import admin
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.db.models.functions import Centroid
from .models import Country, City, Activity
from django.contrib.gis.db.models.functions import GeomOutputGeoFunc
from django.db.models.expressions import RawSQL
from .apps import GisConfig
from django.urls import reverse
from django.utils.safestring import mark_safe

@admin.register(Country)
class CountryAdmin(admin.GISModelAdmin):
    list_display = ('name', 'area_display', 'area_generated_display', 'centroid_display', 'centroidJSON_display')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('centroid_display', 'buffer_display', 'area_generated_display')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si l'utilisateur est sur la liste (changelist), on ne charge pas la géométrie
        return qs.annotate(
            area=Area('geom'),
            centroid=Centroid('geom'),
            buffer_geom=BufferGeom('geom', 25_000)  # Buffer de 25 km (25000 mètres)
        )

    def area_display(self, obj):
        if obj.area is not None:
            return round(obj.area.sq_m / 1_000_000, 2)
        return None
    area_display.short_description = 'Area (km²)'
    area_display.admin_order_field = 'area'

    def centroidJSON_display(self, obj):
        if hasattr(obj, 'centroid') and obj.centroid:
            return obj.centroid.geojson
        return None
    centroidJSON_display.short_description = 'Centroid (geoJSON)'

    def centroid_display(self, obj):
        if hasattr(obj, 'centroid') and obj.centroid:
            return obj.centroid
        return None
    centroid_display.short_description = 'Centroid'

    def buffer_display(self, obj):
        if hasattr(obj, 'buffer_geom') and obj.buffer_geom:
            return obj.buffer_geom
        return None
    buffer_display.short_description = 'Buffer (geoJSON)'

    def area_generated_display(self, obj):
        # Affiche la valeur du champ area_generated (GeneratedField)
        return obj.area_generated*1E-6 if hasattr(obj, 'area_generated') else None
    area_generated_display.short_description = 'Area (generated)'
    area_generated_display.admin_order_field = 'area_generated'


class BufferGeom(GeomOutputGeoFunc):
    """ST_BUFFER postgis function returning only geometry."""
    function = "ST_BUFFER"
    template = '%(function)s(%(expressions)s)'


@admin.register(City)
class CityAdmin(admin.GISModelAdmin):
    list_display = ('name', 'country_link', 'country_display', 'lat', 'lon')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('country',)  # Ajout du filtre par pays

    def lat(self, obj):
        if obj.geom:
            geom_4326 = obj.geom.transform(4326, clone=True)
            return self._to_dms(geom_4326.y, 'lat')
        return None
    lat.short_description = 'Latitude'

    def lon(self, obj):
        if obj.geom:
            geom_4326 = obj.geom.transform(4326, clone=True)
            return self._to_dms(geom_4326.x, 'lon')
        return None
    lon.short_description = 'Longitude'

    def _to_dms(self, value, typ):
        # typ: 'lat' ou 'lon'
        deg = int(abs(value))
        min_ = int((abs(value) - deg) * 60)
        sec = (abs(value) - deg - min_ / 60) * 3600
        direction = ''
        if typ == 'lat':
            direction = 'N' if value >= 0 else 'S'
        else:
            direction = 'E' if value >= 0 else 'W'
        return f"{deg}° {min_}′ {sec:.0f}″ {direction}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        app_label = GisConfig.label
        country_table = f'"{app_label}_country"'
        city_table = f'"{app_label}_city"'
        sql = (
            f'SELECT STRING_AGG(U0."name", \', \') '
            f'FROM {country_table} U0 '
            f'WHERE ST_INTERSECTS(U0."geom", {city_table}."geom")'
        )
        return qs.annotate(
            countries_names=RawSQL(sql, [])
        )

    def country_link(self, obj):
        if obj.country:
            url = reverse("admin:my_gis_app_country_change", args=(obj.country.pk,))
            return mark_safe(f'<a href="{url}">{obj.country.name}</a>')
        return "-"
    country_link.short_description = 'Country'

    def country_display(self, obj):
        if obj.countries_names:
            if isinstance(obj.countries_names, (list, tuple)):
                return ", ".join(obj.countries_names)
            return str(obj.countries_names)
        return "-"
    country_display.short_description = 'Countries (spatial)'


@admin.register(Activity)
class ActivityAdmin(admin.GISModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
    ordering = ('-date', 'name')

