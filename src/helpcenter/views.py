from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *

class HelpCenterView(TemplateView):
    template_name = "help_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["steps"] = QuickStartStep.objects.all()
        context["sections"] = FAQSection.objects.prefetch_related("faqs")
        context["tutorials"] = Tutorial.objects.all()
        context["support_cards"] = SupportCard.objects.all()
        return context