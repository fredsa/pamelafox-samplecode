from django.db import models

class Event(models.Model):
  spreadsheet_key = models.CharField(max_length=120, primary_key=True)
  worksheet_id = models.CharField(max_length=10)
