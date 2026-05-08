from django.urls import path

from ota.views import download_ota_file, health_check


urlpatterns = [
    path("healthz/", health_check, name="health-check"),
    path("ota/<path:ota_key>/", download_ota_file, name="ota-download"),
    path("ota/<path:ota_key>", download_ota_file, name="ota-download-no-slash"),
]
