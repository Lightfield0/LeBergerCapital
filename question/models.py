from django.db import models
from django.contrib.auth.models import User

class SurveyResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    profile = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s Survey Result"
    