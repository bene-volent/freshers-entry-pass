from django.db import models

# Create your models here.
from django.db import models

class EntryPass(models.Model):
    pass_id = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=10)
    attended = models.BooleanField(default=False)
    
    # Method to derive the branch based on roll_no
    @property
    def branch(self):
        if 'd1r' in self.roll_no:
            return 'MCA'
        elif 'd2r' in self.roll_no:
            return 'BCA'
        else:
            return 'Unknown'
    
    # Method to derive the year based on the first four characters of roll_no
    @property
    def year(self):
        return self.roll_no[:4]

    def __str__(self):
        return f"{self.name} ({self.roll_no})"



    
    