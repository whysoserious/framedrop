# Użyj oficjalnego obrazu Pythona
FROM python:3.11-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik z zależnościami
COPY requirements.txt .

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends     libgl1-mesa-glx     libsm6     libxext6     ffmpeg     && rm -rf /var/lib/apt/lists/*

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji
COPY . .

# Ustaw domyślną komendę do uruchomienia aplikacji w trybie demona
CMD ["python", "main.py"]
