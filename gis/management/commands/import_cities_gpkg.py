from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource, SpatialReference
from gis.models import City
from django.contrib.gis.geos import Point
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Importe les villes (City) depuis un fichier GeoPackage (.gpkg) dans le modèle City.'

    def add_arguments(self, parser):
        parser.add_argument('gpkg', type=str, help='Chemin vers le fichier .gpkg à importer')

    def handle(self, *args, **options):
        gpkg_path = options['gpkg']
        try:
            ds = DataSource(gpkg_path)
        except Exception as e:
            raise CommandError(f"Erreur lors de l'ouverture du fichier gpkg : {e}")
        layer = ds[0]
        cities = []
        batch_size = 100
        batch = []
        for feat in tqdm(layer, desc="Importation des villes"):
            name = feat.get('COMM_NAME') or 'Sans nom'
            try:
                geom = feat.geom.transform(3857,clone=True)
                # Si la géométrie n'a pas de SRS, on la reconstruit explicitement AVANT tout calcul
                if not geom.srs:
                    wkt = geom.wkt
                # Calcul du centroïde pour Polygon ou MultiPolygon
                if geom.geom_type.name in ('Polygon', 'MultiPolygon'):
                    centroid = geom.centroid
                    geos_geom = Point(centroid.x, centroid.y, srid=3857)
                else:
                    continue
                batch.append(City(name=name, geom=geos_geom))
                if len(batch) == batch_size:
                    City.objects.bulk_create(batch)
                    batch = []
            except Exception as e:
                continue
        if batch:
            City.objects.bulk_create(batch)
        self.stdout.write(self.style.SUCCESS(f"Import terminé."))
