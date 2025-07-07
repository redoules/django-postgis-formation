from django.contrib.gis.db import models


class Area(models.Model):
    area = models.CharField(max_length=250)
    geoloc = models.CharField(max_length=250)
    sector = models.CharField(max_length=250)
    geom = models.MultiPolygonField(srid=4326)


class Pipe(models.Model):
    FLUID_CHOICES = [
        ("gas", "Gas"),
        ("oil", "Oil"),
        ("water", "Water"),
    ]
    fluid = models.CharField(max_length=250, choices=FLUID_CHOICES)
    geom = models.LineStringField(srid=4326)

    class Meta:
        verbose_name = "Pipe"
        verbose_name_plural = "Pipes"


