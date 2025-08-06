from typing import Any
import helper
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image


STATICFILES_VENDORS_DIR = getattr(settings, "STATICFILES_VENDORS_DIR")

VENDOR_STATICFILS = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
    "flowbit.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js.map"
}

def create_favicon(path):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))  # solid black
    img.save(path, format="ICO")


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Downloading vendor static files...")
        complete_urls = []
        
        # Download vendor static files
        for name, urls in VENDOR_STATICFILS.items():
            out_path = STATICFILES_VENDORS_DIR / name
            dl_success = helper.download_to_local(urls, out_path)
            print(name, urls)
            if dl_success:
                complete_urls.append(urls)
            else:
                self.stdout.write(self.style.ERROR(f"Failed to download {urls}"))
        
        # Creating favicon
        favicon_path = STATICFILES_VENDORS_DIR.parent / "favicon.ico"
        create_favicon(favicon_path)
        self.stdout.write(self.style.SUCCESS(f"Created favicon.ico at {favicon_path}"))
        
        if set(complete_urls) == set(VENDOR_STATICFILS.values()):

            self.stdout.write(
                self.style.SUCCESS("Successfully updated vendor static files.")
            )
