import sys
import os
import django
import xml.etree.ElementTree as ET
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postgisformation.settings')
django.setup()

from gis.models import Activity
from django.contrib.gis.geos import LineString


def import_gpx(filepath, name=None, activity_date=None):
    print(f"Import du fichier : {filepath}")
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
    points = []
    for trk in root.findall('default:trk', ns):
        for trkseg in trk.findall('default:trkseg', ns):
            for trkpt in trkseg.findall('default:trkpt', ns):
                lat = trkpt.attrib.get('lat')
                lon = trkpt.attrib.get('lon')
                ele = None
                ele_elem = trkpt.find('default:ele', ns)
                if ele_elem is not None:
                    try:
                        ele = float(ele_elem.text)
                    except Exception:
                        ele = None
                if lat and lon:
                    if ele is not None:
                        points.append((float(lon), float(lat), ele))
                    else:
                        points.append((float(lon), float(lat)))
    if not points:
        print("Aucun point GPS trouvé dans le fichier GPX.")
        return
    route = LineString(points, srid=4326)
    route.transform(3857)
    if not name:
        name = os.path.basename(filepath)
    if not activity_date:
        activity_date = date.today()
    activity = Activity.objects.create(
        name=name,
        date=activity_date,
        route=route
    )
    print(f"Activité créée : {activity}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python import_gpx.py <fichier.gpx> [nom] [date:YYYY-MM-DD]")
        sys.exit(1)
    filepath = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    activity_date = sys.argv[3] if len(sys.argv) > 3 else None
    if activity_date:
        activity_date = date.fromisoformat(activity_date)
    import_gpx(filepath, name, activity_date)
