# OTA Download Server

Django 기반의 아주 단순한 OTA 파일 다운로드 서버입니다. 예를 들어 `http://EC2_PUBLIC_IP/ota/ml/`로 요청하면 컨테이너 안의 `/app/ota_files/ml/firmware.bin` 파일을 다운로드합니다.

## 동작 방식

요청 URL의 key를 실제 파일 경로에 매핑합니다.

```text
/ota/ml/  ->  /app/ota_files/ml/firmware.bin
```

매핑은 `OTA_DOWNLOAD_MAP` 환경변수로 설정합니다.

```json
{"ml":"ml/firmware.bin","heater":"heater/firmware.bin"}
```

파일 경로는 항상 `OTA_FILE_ROOT` 아래로만 제한됩니다. 잘못된 key나 없는 파일은 `404`를 반환합니다.

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p ota_files/ml
cp /path/to/firmware.bin ota_files/ml/firmware.bin

export OTA_FILE_ROOT="$(pwd)/ota_files"
export OTA_DOWNLOAD_MAP='{"ml":"ml/firmware.bin"}'
python manage.py runserver 0.0.0.0:8000
```

확인:

```bash
curl -v http://127.0.0.1:8000/healthz/
curl -OJ http://127.0.0.1:8000/ota/ml/
```

## Docker 실행

```bash
mkdir -p ota_files/ml
cp /path/to/firmware.bin ota_files/ml/firmware.bin

docker build -t ota-download-server .
docker run -d \
  --name ota-download-server \
  --restart unless-stopped \
  -p 80:8000 \
  -e DJANGO_DEBUG=false \
  -e DJANGO_ALLOWED_HOSTS='*' \
  -e DJANGO_SECRET_KEY='change-this-secret-key' \
  -e OTA_FILE_ROOT=/app/ota_files \
  -e OTA_DOWNLOAD_MAP='{"ml":"ml/firmware.bin"}' \
  -v "$(pwd)/ota_files:/app/ota_files:ro" \
  ota-download-server
```

Docker Compose를 쓰는 경우:

```bash
docker compose up -d --build
```

EC2에서 호스트의 실제 OTA 폴더가 `/home/ec2-user/ota_was/ota_files`라면:

```bash
HOST_OTA_FILE_ROOT=/home/ec2-user/ota_was/ota_files docker compose up -d --build
```

중요: Docker 컨테이너 안에서는 EC2 호스트 경로가 그대로 보이지 않습니다. 위 설정은 EC2의 `/home/ec2-user/ota_was/ota_files`를 컨테이너 내부 `/app/ota_files`로 마운트하고, Django는 컨테이너 내부 경로인 `/app/ota_files`를 읽습니다.

## AWS EC2 배포 메모

1. EC2 보안 그룹에서 요청하는 서버의 IP에 대해 TCP `80` 포트를 허용합니다.
2. EC2에 Docker와 Docker Compose를 설치합니다.
3. 이 프로젝트를 EC2에 복사하고 `ota_files/ml/firmware.bin`에 실제 OTA 파일을 배치합니다.
4. `compose.yaml`의 `DJANGO_SECRET_KEY`, `OTA_DOWNLOAD_MAP`을 운영 값으로 변경합니다.
5. `HOST_OTA_FILE_ROOT=/home/ec2-user/ota_was/ota_files docker compose up -d --build`로 실행합니다.

요청 예시:

```text
http://EC2_PUBLIC_IP/ota/ml/
```
