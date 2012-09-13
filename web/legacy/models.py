from django.db.models import Model, IntegerField
from app.models.businesses import Business
from foreignkeynonrel.models import ForeignKeyNonRel


class BusinessIdMap(Model):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_business = ForeignKeyNonRel(Business)
