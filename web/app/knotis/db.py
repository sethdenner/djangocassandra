from django.db import models

class KnotisModel(models.Model):
    class Meta:
        abstract = True
        app_label = "app"
