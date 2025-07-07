from django.shortcuts import render

def city_map_api(request):
    return render(request, 'gis/city_map_api.html')
