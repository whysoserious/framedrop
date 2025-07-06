To jest szkic planu nowej aplikacji o nazwie __FrameRater__.

Ta aplikacja ma wysyłać posta na konto na Bluesky, które zawiera losową klatkę z podanego pliku video, podaną treść i ewentualnie timestamp klatki.

Tryby działania:
- jednorazowe uruchomienie skryptu wyśle posta na Bluesky. Można podać treść posta z cmdline. Skrypt sam losowo wybierze klatkę z podanego w cmdline filmu avi
- daemon mode: skrypt działa cały czas i wysyła posty o zadanych godzinach. Zaproponować jak to zrobić.\

Oba tryby mają działać w Docker image. 

Język programowania: Python. 

Przygotuj dokładne logi. 
Cały kod, wszystkie komentarze i logi mają być po angielsku.
