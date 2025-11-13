from django.shortcuts import render
from django.views.generic import TemplateView
from .models import QuickStartStep, FAQSection, HelpTutorial, SupportCard


def help_center(request):
    steps = QuickStartStep.objects.order_by("order")
    sections = FAQSection.objects.order_by("order").prefetch_related("faqs")
    tutorials = HelpTutorial.objects.all()
    support_cards = SupportCard.objects.all()

    return render(
        request,
        "helpcenter/help_center.html",
        {
            "steps": steps,
            "sections": sections,
            "tutorials": tutorials,
            "support_cards": support_cards,
        },
    )
