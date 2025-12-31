from django.contrib import admin
from .models import *


@admin.register(QuickStartStep)
class QuickStartStepAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "order")
    list_editable = ("order",)


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1


@admin.register(FAQSection)
class FAQSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)
    inlines = [FAQItemInline]


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ("display_title", "display_duration", "display_views", "display_thumbnail", "order")
    list_editable = ("order",)

    def display_title(self, obj):
        return obj.display_title

    def display_duration(self, obj):
        return obj.display_duration or "-"

    def display_views(self, obj):
        return obj.display_views or "-"
    
    def display_thumbnail(self, obj):
        return obj.display_thumbnail or "-"

    display_title.short_description = "Title"
    display_duration.short_description = "Duration"
    display_views.short_description = "Views"
    display_thumbnail.short_description = "Thumbnail"


@admin.register(SupportCard)
class SupportCardAdmin(admin.ModelAdmin):
    list_display = ("title", "button_text", "order")
    list_editable = ("order",)
