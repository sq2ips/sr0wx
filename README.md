# sr0wx
Automatyczna stacja pogodowa sr0wx autorstwa @sq6jnx, z modułami i poprawkami autorstwa @sq9atk oraz moimi zmianami i dodatkami.

Program ten pracjue na stacji klubu Koła Naukowego UMG o nazwie Morski Klub Łączności "SZKUNER" SP2ZIE.

## Lista zmain
- Dodanie modułu wyliczającaego wschody i zachody słońca bez połączenia z internetem (calendar_sq2ips.py)
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA (radioactive_sq2ips.py)
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobngo pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej. Dodatkowo dodany jest katalog z samplami w formacie mp3 które stacja pobiera gdy nie zostały odnalezione (baltyk_sq2dk.py)
- Dodanie modułu ostrzeżeń meteorologicznych
- Przepisanie całej aplikacji na python 2 na 3
- Obsługa wieloprocesowości, wszystkie moduły uruchamiają się jednocześnie

## Licencja
LICENCE.md

## TODO
- Instrukcja instalacji
- Skrypt szukający id stacji i regionu do radioactive_sq2ips.py i meteoalert_sq2ips.py