from django.views.generic import TemplateView
from .models import QuickStartStep, FAQSection, Tutorial, SupportCard

class HelpCenterView(TemplateView):
    template_name = "helpcenter/help_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["steps"] = QuickStartStep.objects.order_by("order")
        context["sections"] = FAQSection.objects.order_by("order").prefetch_related("faqs")
        context["tutorials"] = Tutorial.objects.all()
        context["support_cards"] = SupportCard.objects.all()

        return context
