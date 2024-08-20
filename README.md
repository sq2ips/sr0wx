# sr0wx
Ten projekt to fork automatycznej radioamatorskiej stacja pogodowej SR0WX autorstwa [@sq6jnx](https://github.com/sq6jnx/sr0wx.py), rozwijanej przez [@sq9atk](https://github.com/sq9atk/sr0wx), który staram się rozwijać i unowocześniać.

Program ten jest wykorzystywany przez Koło Naukowe UMG o nazwie Morski Klub Łączności "SZKUNER" SP2ZIE do obsługi automatycznej stacji pogodowej [SR2WXG](https://www.sp2zie.pl/index.php/stacja-systemu-sr0wx).

## Działanie
Program pobiera różne dane z internetu, np. stan pogody, prognozę pogody, ostrzeżenia imgw, poziom promieniowania i inne, konwertuje je na poszczególne słowa które są samplami audio a następnie odtwarza je. Do komputera podłączone jest radio, które odtwarza komunikat na paśmie amatorskim na częstotliwości 144.950 MHz.

Nagranie komunikatu stacji [SR2WXG](https://github.com/user-attachments/assets/8082e14b-d6fa-4f6d-9ed3-4c9bdd58bf27)

## Trwa pisanie [dokumentacji](../../wiki)

## Lista zmian
- Dodanie modułu wyliczającego wschody i zachody słońca bez połączenia z internetem (calendar_sq2ips.py)
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA (radioactive_sq2ips.py)
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobnego pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej ~~(baltyk_sq2dk.py)~~ (baltyk_sq2ips.py)
- Dodanie modułu ostrzeżeń meteorologicznych z IMGW PIB (meteoalert_sq2ips.py)
- Dodanie modułu stanu pogody z fizycznej stacji pogodowej przez UDP (meteostation_sq2ips.py)
- Dodanie modułu alertów pogody kosmicznej (spaceweather_sq2ips)
- Dodanie modułu pobierającego propagacje oraz poziom zakłuceń z hamqsl.com (propagation_sq2ips.py)
- Dodanie modułu pobierający pogodę z yr.no (meteo_yr_sq2ips.py) (testowy)
- Dodanie modułu informującego o stopniu zagrożenia pożarowego lasów (fires_sq2ips.py)
- Dodanie modułu radaru pogodowego (antistorm_sq2ips.py)
- Napisanie od nowa modułu informującego o stanie wody z wodowskazów ze strony hydro.imgw.pl (imgw_podest_sq2ips.py)
- Przepisanie całej aplikacji z python 2 na 3
- Dodanie generatora sampli napisanego w pythonie i wygenerowanie od nowa wszystkich sampli
- Obsługa wieloprocesowości, wszystkie moduły uruchamiają się jednocześnie
- Niejawne parametry konkretnej stacji (klucze api itp.) są przechowywane w pliku .env
- Zmiana urllib na requests w kilku modułach dla zminimalizowania ilości błędów pobierania.
- Dodanie trybu testowego, moduły są uruchamiane ale nie są odtwarzane sample
- Zmiana biblioteki do pobierania danych z urllib na requests, wielokrotne próby pobierania przy błedzie pobierania
- Dodanie opcji zapisu komunikatu do pliku tekstowego
- Dodanie opcji modułów awaryjnych, gdy jakiś moduł nie działa na jego miejsce zostaje uruchomiony moduł awaryjny
- Wiele zmian w głównym skrypcie sr0wx.py
- Inicjalizacja pygame jako podmodułu
- Dodanie katalogu cache
- przeniesienie wszystkich modułów do katalogu modules/
- Zmiana systemu loggera na coloredlogs
- Dodanie kilku parametrów urucamiania

## Planowane prace
- Napisanie modułu pobierającego dane ze stacji pogodowych przez APRS

## Licencja
LICENSE
