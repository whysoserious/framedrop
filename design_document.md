### Specyfikacja Aplikacji: FrameDrop

#### 1. Podsumowanie

Aplikacja "FrameDrop" to narzędzie w języku Python, którego celem jest automatyczne publikowanie postów na platformie Bluesky. Każdy post będzie zawierał losowo wybraną klatkę z pliku wideo, tekst oraz opcjonalnie znacznik czasu (timestamp) tej klatki. Aplikacja będzie mogła działać w trybie jednorazowego uruchomienia lub jako stały proces (demon) publikujący posty według harmonogramu. Całość ma być uruchamiana w środowisku Docker.

#### 2. Główne Funkcjonalności

*   **Ekstrakcja klatek wideo:** Aplikacja musi być w stanie otworzyć plik wideo (obsługiwane formaty: .mp4, .avi, .mkv), odczytać jego długość, wylosować numer klatki, a następnie wyeksportować tę klatkę do formatu obrazu (PNG).
*   **Publikacja na Bluesky:** Aplikacja będzie łączyć się z API Bluesky, aby opublikować post składający się z:
    *   **Obrazu:** Wyekstrahowana klatka wideo.
    *   **Tekstu:** Treść posta podana przez użytkownika.
    *   **Tekstu alternatywnego (Alt Text):** Automatycznie generowany opis, np. "Klatka z filmu [nazwa pliku] z czasu [timestamp]".
*   **Logowanie:** Aplikacja będzie zapisywać logi swojej pracy do standardowego wyjścia, informując o pomyślnych publikacjach lub napotkanych błędach.

#### 3. Architektura i Proponowane Technologie

*   **Język:** Python 3.9+
*   **Obsługa wideo:** `opencv-python-headless`
*   **Komunikacja z Bluesky API:** `atproto`
*   **Obsługa argumentów CLI:** `argparse`
*   **Harmonogram (dla trybu demona):** `schedule`
*   **Zarządzanie zależnościami:** Plik `requirements.txt`.
*   **Konfiguracja:** Dane logowania do Bluesky oraz konfiguracja trybu demona będą zarządzane przez zmienne środowiskowe.

#### 4. Tryby Działania

**Tryb 1: Jednorazowe uruchomienie**

*   **Uruchomienie:** Skrypt uruchamiany z linii poleceń.
*   **Argumenty:**
    *   `--video <ścieżka_do_pliku>` (wymagany): Ścieżka do pliku wideo.
    *   `--text <treść_posta>` (opcjonalny): Tekst do opublikowania.
    *   `--timestamp` (opcjonalny, flaga): Dodaje do treści posta znacznik czasu klatki w formacie `HH:MM:SS`.
*   **Przykład użycia:**
    ```bash
    python main.py --video "moj_film.mp4" --text "Losowa klatka!" --timestamp
    ```

**Tryb 2: Demon (Daemon Mode)**

*   **Działanie:** Skrypt działa w pętli, publikując posty według harmonogramu.
*   **Konfiguracja (przez zmienne środowiskowe):**
    *   `BLUESKY_HANDLE`: Login użytkownika Bluesky.
    *   `BLUESKY_PASSWORD`: Hasło (klucz) do konta.
    *   `VIDEO_PATH`: Ścieżka do pliku wideo, z którego będą losowane klatki.
    *   `SCHEDULE_TIMES`: Lista godzin publikacji, oddzielona przecinkami (np. "10:00,18:30").
    *   `POST_TEXT`: Domyślny tekst posta.
*   **Obsługa błędów:** W przypadku błędu (np. problem z siecią), aplikacja zapisze log i będzie kontynuować pracę, czekając na kolejną zaplanowaną godzinę.

#### 5. Docker

*   Aplikacja będzie spakowana w obraz Docker. `Dockerfile` będzie bazował na obrazie `python:3.11-slim`, zainstaluje zależności i ustawi `main.py` jako domyślny punkt wejścia, uruchamiając tryb demona. Tryb jednorazowy będzie można uruchomić przez nadpisanie komendy `docker run`.
