from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings


class OtaDownloadTests(TestCase):
    def test_health_check(self):
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_downloads_configured_file(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            firmware = root / "ml" / "firmware.bin"
            firmware.parent.mkdir(parents=True)
            firmware.write_bytes(b"firmware-data")

            with override_settings(
                OTA_FILE_ROOT=root,
                OTA_DOWNLOAD_MAP={"ml": "ml/firmware.bin"},
            ):
                response = self.client.get("/ota/ml/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"firmware-data")
        self.assertEqual(response["Content-Length"], "13")
        self.assertIn("firmware.bin", response["Content-Disposition"])
        self.assertEqual(response["X-OTA-Route"], "ml")

    def test_unknown_route_returns_404(self):
        response = self.client.get("/ota/unknown/")

        self.assertEqual(response.status_code, 404)

    def test_path_traversal_is_blocked(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "ota"
            root.mkdir()

            with override_settings(
                OTA_FILE_ROOT=root,
                OTA_DOWNLOAD_MAP={"bad": "../secret.bin"},
            ):
                response = self.client.get("/ota/bad/")

        self.assertEqual(response.status_code, 404)
