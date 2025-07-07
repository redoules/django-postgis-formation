from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import CityGeoViewSet, CountryGeoViewSet
from .views_city_map_api import city_map_api

router = DefaultRouter()
router.register(r'cities', CityGeoViewSet, basename='city')
router.register(r'countries', CountryGeoViewSet, basename='country')

urlpatterns = [
    path('api/', include(router.urls)),
    path('city_map_api/', city_map_api, name='city_map_api'),
]
