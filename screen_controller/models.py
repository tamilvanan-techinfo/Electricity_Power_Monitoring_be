from django.db import models

# Create your models here.
class Screen(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='screen_thumbnails/', blank=True, null=True)
    is_live = models.BooleanField(default=False)

