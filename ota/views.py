import mimetypes
import logging
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.utils.http import http_date
from django.views.decorators.http import require_safe


logger = logging.getLogger(__name__)


@require_safe
def health_check(request):
    return JsonResponse({"status": "ok"})


@require_safe
def download_ota_file(request, ota_key):
    route_key = ota_key.strip("/")
    relative_file = settings.OTA_DOWNLOAD_MAP.get(route_key)
    if relative_file is None:
        logger.warning("Unknown OTA route requested: route=%s", route_key)
        raise Http404("Unknown OTA route.")

    file_path = resolve_ota_file(relative_file)
    if not file_path.is_file():
        logger.warning(
            "OTA file does not exist: route=%s relative_file=%s resolved_path=%s ota_root=%s",
            route_key,
            relative_file,
            file_path,
            settings.OTA_FILE_ROOT,
        )
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
        logger.warning(
            "Blocked OTA file outside root: relative_file=%s resolved_path=%s ota_root=%s",
            relative_file,
            target,
            root,
        )
        raise Http404("OTA file path is outside OTA_FILE_ROOT.") from exc

    return target
