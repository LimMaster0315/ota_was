import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.utils.http import http_date
from django.views.decorators.http import require_safe


@require_safe
def health_check(request):
    return JsonResponse({"status": "ok"})


@require_safe
def download_ota_file(request, ota_key):
    route_key = ota_key.strip("/")
    relative_file = settings.OTA_DOWNLOAD_MAP.get(route_key)
    if relative_file is None:
        raise Http404("Unknown OTA route.")

    file_path = resolve_ota_file(relative_file)
    if not file_path.is_file():
        raise Http404("OTA file does not exist.")

    stat = file_path.stat()
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    response = FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=file_path.name,
        content_type=content_type,
    )
    response["Content-Length"] = str(stat.st_size)
    response["Last-Modified"] = http_date(stat.st_mtime)
    response["X-OTA-Route"] = route_key
    return response


def resolve_ota_file(relative_file):
    root = Path(settings.OTA_FILE_ROOT).resolve()
    target = (root / relative_file).resolve()

    try:
        target.relative_to(root)
    except ValueError as exc:
        raise Http404("OTA file path is outside OTA_FILE_ROOT.") from exc

    return target
