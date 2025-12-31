from django.db import models
from .real_view_count import *


class QuickStartStep(models.Model):
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    color = models.CharField(
        max_length=50, help_text="Tailwind color name, e.g., blue, pink, green"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Step {self.number}: {self.title}"


# -------------------------
# 2. FAQ Sections + FAQ Items
# -------------------------
class FAQSection(models.Model):
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default="💬")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class FAQItem(models.Model):
    section = models.ForeignKey(
        FAQSection, on_delete=models.CASCADE, related_name="faqs"
    )
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question


# -------------------------
# 3. Video Tutorials
# -------------------------
class Tutorial(models.Model):
    youtube_url = models.URLField(blank=True)
    youtube_id = models.CharField(max_length=20, blank=True)
    # Optional override
    title = models.CharField(max_length=200, blank=True)

    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    @property
    def youtube_data(self):
        if not self.youtube_id:
            return None
        return get_cached_youtube_data(self.youtube_id)

    @property
    def display_title(self):
        if self.title:
            return self.title
        if self.youtube_data:
            return self.youtube_data["title"]
        return "Untitled"
    @property
    def display_views(self):
        return self.youtube_data["views"] if self.youtube_data else None

    @property
    def display_thumbnail(self):
        return self.youtube_data["thumbnail"] if self.youtube_data else None

    @property
    def display_duration(self):
        return self.youtube_data["duration"] if self.youtube_data else None

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


# -------------------------
# 4. Contact Support Cards
# -------------------------
class SupportCard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    button_text = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)
    icon_color = models.CharField(max_length=50, default="blue-500")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
