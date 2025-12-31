from django.views.generic import TemplateView
from django.shortcuts import render
from .models import QuickStartStep, FAQSection, Tutorial, SupportCard
from .real_view_count import *


class HelpCenterView(TemplateView):
    template_name = "helpcenter/help_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["steps"] = QuickStartStep.objects.order_by("order")
        context["sections"] = FAQSection.objects.order_by("order").prefetch_related("faqs")
        context["tutorials"] = Tutorial.objects.all()
        context["support_cards"] = SupportCard.objects.all()

        return context
def help_center(request):
    tutorials = Tutorial.objects.all().order_by("order")

    return render(request, "helpcenter/help_center.html", {
        "tutorials": tutorials
    })

