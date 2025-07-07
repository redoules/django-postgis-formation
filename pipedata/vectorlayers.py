# in a vector_layers.py file (for example)
from vectortiles import VectorLayer
from pipedata.models import Area, Pipe
from django.contrib.gis.db.models.functions import Centroid

class AreaVectorLayer(VectorLayer):
    model = Area  # your model, as django conventions you can use queryset or get_queryset method instead)
    id = "areas"  # layer id in you vector layer. each class attribute can be defined by get_{attribute} method
    tile_fields = ('geoloc', "sector", "area") # fields to include in tile
    min_zoom = 6 # minimum zoom level to include layer. Take care of this, as it could be a performance issue. Try to not embed data that will no be shown in your style definition.
    # all attributes available in vector layer definition can be defined

class AreaCenterVectorLayer(VectorLayer):
    queryset = Area.objects.annotate(centroid=Centroid("geom"))


class PipeVectorLayer(VectorLayer):
    model = Pipe  # your model, as django conventions you can use queryset or get_queryset method instead)
    id = "pipes"  # layer id in you vector layer. each class attribute can be defined by get_{attribute} method
    tile_fields = ('fluid',) # fields to include in tile
    min_zoom = 6 # minimum zoom level to include layer. Take care of this, as it could be a performance issue. Try to not embed data that will no be shown in your style definition.
    # all attributes available in vector layer definition can be defined