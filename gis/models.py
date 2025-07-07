from django.contrib.gis.db import models
from django.db.models import Func, F
class Country(models.Model):
    name = models.CharField(max_length=100)
    geom = models.MultiPolygonField(srid=3857) # Pseudo-Mercator projection
    area_generated = models.GeneratedField(
        expression=Func(F('geom'), function='ST_Area'),
        output_field=models.FloatField(),
        db_persist=True
    )
    population = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    geom = models.PointField(srid=3857)
    country = models.ForeignKey('Country', null=True, blank=True, on_delete=models.SET_NULL, related_name='cities')
    geom_4326 = models.GeneratedField(
        expression=Func(F('geom'), function='ST_Transform', template='%(function)s(%(expressions)s, 4326)'),
        output_field=models.PointField(srid=4326),
        db_persist=True
    )

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    route = models.LineStringField(srid=3857, dim=3)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ['-date', 'name']

    def __str__(self):
        return f"{self.name} ({self.date})"