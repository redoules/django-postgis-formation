from rest_framework import viewsets, serializers
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField
from gis.models import City, Country

class CityGeoSerializer(GeoFeatureModelSerializer):
    geom_4326 = GeometryField()
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = City
        geo_field = 'geom_4326'
        fields = ('id', 'name', 'country_name')

    def get_country_name(self, obj):
        return obj.country.name if obj.country else None

class CountryGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Country
        geo_field = 'geom'
        fields = ('id', 'name', 'population')

class CityGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CityGeoSerializer
    pagination_class = GeoJsonPagination
    filter_backends = (DistanceToPointFilter,)


class CountryGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryGeoSerializer
    pagination_class = GeoJsonPagination


