from django.db import models

class matchings(models.Model):
  person_a = models.CharField(max_length=100)
  person_b = models.CharField(max_length=100)
  coefficient = models.FloatField()
  person_a_photo = models.URLField()
  person_b_photo = models.URLField()
  rank = models.IntField()
  fbid = models.IntField()
