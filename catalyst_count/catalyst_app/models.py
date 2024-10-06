# myapp/models.py
from django.db import models

class Company(models.Model):
    id = models.AutoField(primary_key=True)  # Django automatically adds an ID field if you don't specify one
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    year_founded = models.IntegerField(null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    size_range = models.CharField(max_length=50, null=True, blank=True)
    locality = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    linkedin_url = models.URLField(max_length=500, null=True, blank=True)
    current_employee_estimate = models.CharField(max_length=255, null=True, blank=True)
    total_employee_estimate = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
