from django.db import models

class Locker(models.Model):
    locker_id = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=20, choices=(('Available', 'Available'), ('Occupied', 'Occupied')))
    user_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Locker {self.locker_id} - {self.status}"
