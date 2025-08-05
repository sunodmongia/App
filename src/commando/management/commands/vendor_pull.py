from typing import Any
import helper
from django.conf import settings
from django.core.management.base import BaseCommand


STATICFILES_VENDORS_DIR = getattr(settings, "STATICFILES_VENDORS_DIR")

VENDOR_STATICFILS = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Downloading vendor static files...")
        complete_urls = []
        for name, urls in VENDOR_STATICFILS.items():
            out_path = STATICFILES_VENDORS_DIR / name
            dl_success = helper.download_to_local(urls, out_path)
            print(name, urls)
            if dl_success:
                complete_urls.append(urls)
            else:
                self.stdout.write(self.style.ERROR(f"Failed to download {urls}"))
        if set(complete_urls) == set(VENDOR_STATICFILS.values()):

            self.stdout.write(
                self.style.SUCCESS("Successfully updated vendor static files.")
            )
