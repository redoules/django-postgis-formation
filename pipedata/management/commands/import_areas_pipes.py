from django.core.management.base import BaseCommand
from pipedata.models import Area
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon
from tqdm import tqdm

class Command(BaseCommand):
    help = "Importe les areas et les pipes depuis une source de données."

    def add_arguments(self, parser):
        parser.add_argument('--areas-file', type=str, help='Chemin du fichier à importer pour les areas')
        parser.add_argument('--pipes-file', type=str, help='Chemin du fichier à importer pour les pipes')

    def handle(self, *args, **options):
        areas_file = options.get('areas_file')
        pipes_file = options.get('pipes_file')
        if areas_file:
            self.import_areas(areas_file)
        if pipes_file:
            self.import_pipes(pipes_file)

    def import_areas(self, file_path, batch_size=500):
        """
        Importe les areas à partir d'un shapefile (.shp) avec insertion par batch.
        :param file_path: chemin du fichier à importer
        :param batch_size: taille du batch pour bulk_create
        """
        ds = DataSource(file_path)
        layer = ds[0]
        # Récupérer les noms de champs du layer (déjà une liste de str)
        field_names = list(layer.fields)
        areas_to_create = []
        total = 0
        # Utiliser tqdm pour la barre de progression
        for feat in tqdm(layer, desc="Import des areas", unit="area"):
            area = feat.get("Area") or ""
            geoloc = feat.get("Geoloc") or ""
            sector = feat.get("Sector") or ""
            geom = feat.geom.geos
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            areas_to_create.append(Area(area=area, geoloc=geoloc, sector=sector, geom=geom))
            if len(areas_to_create) >= batch_size:
                Area.objects.bulk_create(areas_to_create, ignore_conflicts=True)
                total += len(areas_to_create)
                areas_to_create = []
        if areas_to_create:
            Area.objects.bulk_create(areas_to_create, ignore_conflicts=True)
            total += len(areas_to_create)
        self.stdout.write(self.style.SUCCESS(f"{total} areas importés depuis {file_path} (batch size={batch_size})"))

    def import_pipes(self, file_path, batch_size=500):
        """
        Importe les pipes à partir d'un shapefile (.shp) avec insertion par batch.
        :param file_path: chemin du fichier à importer
        :param batch_size: taille du batch pour bulk_create
        """
        from pipedata.models import Pipe
        ds = DataSource(file_path)
        layer = ds[0]
        field_names = list(layer.fields)
        pipes_to_create = []
        total = 0
        skipped = 0
        for feat in tqdm(layer, desc="Import des pipes", unit="pipe"):
            try:
                geom = feat.geom.geos
            except Exception as e:
                skipped += 1
                self.stdout.write(self.style.WARNING(
                    f"Feature ignorée (géométrie invalide ou absente) : {str(e)}"
                ))
                continue
            fluid = feat.get("layer") or ""
            pipes_to_create.append(Pipe(fluid=fluid, geom=geom))
            if len(pipes_to_create) >= batch_size:
                Pipe.objects.bulk_create(pipes_to_create, ignore_conflicts=True)
                total += len(pipes_to_create)
                pipes_to_create = []
        if pipes_to_create:
            Pipe.objects.bulk_create(pipes_to_create, ignore_conflicts=True)
            total += len(pipes_to_create)
        self.stdout.write(self.style.SUCCESS(f"{total} pipes importés depuis {file_path} (batch size={batch_size})"))
        if skipped:
            self.stdout.write(self.style.WARNING(f"{skipped} features ignorées (géométrie invalide ou absente)"))
