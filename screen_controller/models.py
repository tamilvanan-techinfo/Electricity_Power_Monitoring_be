from django.db import models

# Create your models here.
class Screen(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='screen_thumbnails/', blank=True, null=True)



class CurrentScreen(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.screen.name