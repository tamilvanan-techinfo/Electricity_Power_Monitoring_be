from django.db import models

# Create your models here.
class Cycle(models.Model):
    cycle_no = models.CharField(max_length=100,unique=True)
    controller_no = models.CharField(max_length=100,unique=True)

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
    power = models.FloatField(null=True, blank=True, default=0.0)
    voltage = models.FloatField(null=True, blank=True, default=0.0)
    amperage = models.FloatField(null=True, blank=True, default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    total_power = models.FloatField(null=True, blank=True, default=0.0)
    total_voltage = models.FloatField(null=True, blank=True, default=0.0)
    total_amperage = models.FloatField(null=True, blank=True, default=0.0)

    def __str__(self):
        return f"{self.participent.name} - {self.cycle.cycle_no}"


class Grouping(models.Model):
    is_grouping = models.BooleanField(default=False)

    def __str__(self):
        return str(self.is_grouping)

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        ParticipentCycle,
        related_name="groups"
    )

    def __str__(self):
        return self.name