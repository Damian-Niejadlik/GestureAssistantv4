# Prywatność

Obraz jest przetwarzany lokalnie. Aplikacja nie nagrywa, nie zapisuje zdjęć ani nie wysyła
klatek do internetu. Kamera uruchamia się dopiero po Start. Stop zleca zwolnienie zasobów.
Zawieszony sterownik może opóźnić zakończenie odczytu.
Tylko ręcznie uruchomiony scripts/download_model.py łączy się z serwerem modelu;
nie przesyła obrazów ani wyników analizy.


## Wyjątek: jawnie włączona akcja screenshot (3B)

system.take_screenshot zapisuje obraz całego pulpitu, nie klatkę kamery, w katalogu domowym
GestureAssistant/Screenshots. Domyślnie nie ma uprawnień do tej akcji i nie jest ona
wykonywana w dry-run. Nie ma automatycznych zrzutów przy uruchamianiu aplikacji.
Pliki mogą zawierać dane prywatne. Aplikacja nie przesyła ich do sieci i nie prowadzi
synchronizacji online. Zewnętrzne oprogramowanie synchronizujące katalogi jest poza jej kontrolą.
Akcja browser.open_url otwiera wyłącznie jawnie skonfigurowany adres HTTPS w przeglądarce;
nie wysyła do niego obrazu z kamery ani zrzutu ekranu.
