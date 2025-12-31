from django.db import models


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
    title = models.CharField(max_length=200)
    description = models.TextField()
    youtube_url = models.URLField()
    youtube_id = models.CharField(max_length=20, blank=True)
    duration = models.CharField(max_length=20)
    gradient_from = models.CharField(max_length=20, default="blue-400")
    gradient_to = models.CharField(max_length=20, default="purple-500")
    order = models.PositiveIntegerField(default=0)

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
