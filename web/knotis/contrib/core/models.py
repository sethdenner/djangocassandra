import django.db.models as models


class KnotisModel(models.Model):
    class Meta:
        abstract = True
        app_label = "knotis"
