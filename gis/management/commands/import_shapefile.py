from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource
from gis.models import Country
from django.contrib.gis.geos import MultiPolygon

class Command(BaseCommand):
    help = 'Importe les polygones d’un shapefile dans le modèle Country.'

    def add_arguments(self, parser):
        parser.add_argument('shapefile', type=str, help='Chemin vers le fichier .shp à importer')

    def handle(self, *args, **options):
        shapefile_path = options['shapefile']
        try:
            ds = DataSource(shapefile_path)
        except Exception as e:
            raise CommandError(f"Erreur lors de l'ouverture du shapefile : {e}")
        layer = ds[0]
        countries = []
        for feat in layer:
            name = feat.get('NAME') or 'Sans nom'
            population = feat.get('POP2005')
            geom = feat.geom
            print(f"Importation de {name} avec population {population} et géométrie {geom.geom_type.name}")

            try:
                if geom.geom_type.name == 'Polygon':
                    geos_geom = MultiPolygon([geom.geos])
                elif geom.geom_type.name == 'MultiPolygon':
                    geos_geom = geom.geos
                else:
                    self.stderr.write(self.style.WARNING(f"Géométrie ignorée (ni Polygon ni MultiPolygon) pour {name}"))
                    continue
                geos_geom.srid = 4326 
                geos_geom = geos_geom.transform(3857, clone=True)  
                countries.append(Country(name=name, population=population, geom=geos_geom))
                c = Country(name=name, population=population, geom=geos_geom)
                c.save()
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Erreur de géométrie pour {name}: {e}"))
                continue
#        Country.objects.bulk_create(countries)
        self.stdout.write(self.style.SUCCESS(f"{len(countries)} pays importés avec succès."))
