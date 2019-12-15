from django.db import models
from jsonfield import JSONField
# Create your models here.


# class BaseModel(models.Model):
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)



class CoreDetail(models.Model):
    actorname = models.CharField(max_length=255, blank=True)
    actorid = models.CharField(max_length=255, blank=True)
    actorpopularity = models.CharField(max_length=255, blank=True)
    actorprofession = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class Details(models.Model):
    actorid = models.CharField(max_length=255, blank=True)
    actordetails = JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)