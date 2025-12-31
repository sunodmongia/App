from django.contrib import admin
from .models import *
from .real_view_count import get_cached_views


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
    list_display = ("title", "duration", "youtube_views", "order")
    list_editable = ("order",)

    def youtube_views(self, obj):
        if not obj.youtube_views:
            return "-"
        return get_cached_views(obj.youtube_views)

    youtube_views.short_description = "Views"


@admin.register(SupportCard)
class SupportCardAdmin(admin.ModelAdmin):
    list_display = ("title", "button_text", "order")
    list_editable = ("order",)
