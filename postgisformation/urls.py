"""
URL configuration for postgisformation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from gis import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from pipedata.views import AreaTileView, PipeTileView, MapTileView, MapLibreView


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('country_buffer_geojson/', views.country_buffer_geojson, name='country_buffer_geojson'),
    path('country_buffer_map/', views.country_buffer_map, name='country_buffer_map'),
    path('city_list_geojson/', views.city_list_geojson, name='city_list_geojson'),
    path('city_list_map/', views.city_list_map, name='city_list_map'),
    path('import_gpx_activity/', views.import_gpx_activity, name='import_gpx_activity'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('', include('gis.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    MapTileView.get_url(prefix="maptileview"),
    path("maplibre/", MapLibreView.as_view(), name="maplibre"),
    
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
