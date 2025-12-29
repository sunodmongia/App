from django.http import JsonResponse
from saas.telemetry import Telemetry
from saas.trigger import handle_event
from subscriptions.limits import api_calls_last_30_days


class APICallTelemetryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1) Enforce plan limits BEFORE request executes
        if request.user.is_authenticated and request.path.startswith("/api/"):
            org = getattr(request.user, "organization", None)

            if org and org.subscription:
                limit = org.subscription.planlimit.api_calls
                used = api_calls_last_30_days(org)

                if used >= limit:
                    return JsonResponse(
                        {"error": "API limit exceeded. Upgrade plan."}, status=402
                    )

        # 2) Let the API execute
        response = self.get_response(request)

        # 3) Log usage AFTER successful request
        if request.user.is_authenticated and request.path.startswith("/api/"):
            org = getattr(request.user, "organization", None)
            if org:
                Telemetry.api_call(org)
                handle_event(org, "api_call")

        return response
