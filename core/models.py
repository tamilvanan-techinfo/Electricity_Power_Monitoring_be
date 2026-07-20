from django.db import models

# Create your models here.
class Cycle(models.Model):
    cycle_no = models.CharField(max_length=100)
    controller_no = models.CharField(max_length=100)

    def __str__(self):
        return self.cycle_no
    
class Participent(models.Model):
    name = models.CharField(max_length=100)
    profile = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    dob = models.DateField()
    registered_on = models.DateField(auto_now_add=True)

class ParticipentCycle(models.Model):
    participent = models.ForeignKey(Participent, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    power = models.FloatField()
    voltage = models.FloatField()
    amperage = models.FloatField()

    def __str__(self):
        return f"{self.participent.name} - {self.cycle.cycle_no}"