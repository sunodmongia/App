from django.http import JsonResponse
from saas.telemetry import Telemetry
from saas.trigger import handle_event
from subscriptions.limits import api_calls_last_30_days
from subscriptions.services import get_user_organization


class APICallTelemetryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1) Enforce plan limits BEFORE request executes
        if request.user.is_authenticated and request.path.startswith("/api/"):
            org = get_user_organization(request.user)

            if org and org.subscription:
                limits = getattr(org.subscription, "planlimit", None)
                limit = getattr(limits, "api_calls", None)
                used = api_calls_last_30_days(org)

                if limit is not None and used >= limit:
                    return JsonResponse(
                        {"error": "API limit exceeded. Upgrade plan."}, status=402
                    )

        # 2) Let the API execute
        response = self.get_response(request)

        # 3) Log usage AFTER successful request
        if (
            request.user.is_authenticated
            and request.path.startswith("/api/")
            and response.status_code < 400
        ):
            org = get_user_organization(request.user)
            if org:
                Telemetry.api_call(org)
                handle_event(org, "api_call")

        return response
