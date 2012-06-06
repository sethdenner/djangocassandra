from django.db import models

# Create your models here.
class Product(models.Model):
  id = models.CharField(max_length=32, primary_key=True)
  description = models.CharField(max_length=1024)
