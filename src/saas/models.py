from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from django.db import models

# Optional: use choices for cleaner data and better UI
COMPANY_SIZE_CHOICES = [
    ("1-10", "1-10"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("201-500", "201-500"),
    ("500+", "500+"),
]

INDUSTRY_CHOICES = [
    ("tech", "Technology"),
    ("finance", "Finance"),
    ("education", "Education"),
    ("health", "Healthcare"),
    ("other", "Other"),
]

TIME_SLOT_CHOICES = [
    ("morning", "Morning"),
    ("afternoon", "Afternoon"),
    ("evening", "Evening"),
]


class TrialSignup(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=150)
    phone = models.CharField(max_length=20) 
    company_size = models.CharField(
        max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True
    )
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    terms_accepted = models.BooleanField()
    newsletter_opt_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"


class DemoSchedule(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20) 
    company = models.CharField(max_length=150)
    job_title = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES)
    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    use_case = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demo for {self.first_name} {self.last_name} on {self.preferred_date} at {self.time_slot}"
    

class ContactMessage(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolve = models.BooleanField(default=False)
    email_history = models.TextField(blank=True, default="")

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.subject}'
    

