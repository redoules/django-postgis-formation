# in your view file
from pipedata.vectorlayers import AreaVectorLayer, PipeVectorLayer, AreaCenterVectorLayer
from vectortiles.views import MVTView
from django.views.generic import TemplateView

class AreaTileView(MVTView):
    layer_classes = [AreaVectorLayer]


class PipeTileView(MVTView):
    layer_classes = [PipeVectorLayer]


class MapTileView(MVTView):
    """
    View for serving map tiles using MVT (Mapbox Vector Tiles).
    This view can be used to serve both areas and pipes layers.
    """
    layer_classes = [AreaVectorLayer, PipeVectorLayer, AreaCenterVectorLayer]


class MapLibreView(TemplateView):
    """
    View for serving the MapLibre map.
    This view renders a template that includes the MapLibre map.
    """
    template_name = 'pipedata/area_tile_map.html'
