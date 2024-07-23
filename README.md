# sr0wx
Ten projekt to fork automatycznej radioamatorskiej stacja pogodowej SR0WX autorstwa [@sq6jnx](https://github.com/sq6jnx/sr0wx.py), rozwijanej przez [@sq9atk](https://github.com/sq9atk/sr0wx), który staram się rozwijać i unowocześniać.

Program ten jest wykorzystywany przez Koło Naukowe UMG o nazwie Morski Klub Łączności "SZKUNER" SP2ZIE do obsługi automatycznej stacji pogodowej [SR2WXG](https://www.sp2zie.pl/index.php/stacja-systemu-sr0wx).

## Działanie
Program pobiera różne dane z internetu, np. stan pogody, prognozę pogody, ostrzeżenia imgw, poziom promieniowania i inne, konwertuje je na poszczególne słowa które są samplami audio a następnie odtwarza je. Do komputera podłączone jest radio, które odtwarza komunikat na paśmie amatorskim na częstotliwości 144.950 MHz.

Nagranie komunikatu stacji SR2WXG: [SR2WXG](https://github.com/user-attachments/assets/8082e14b-d6fa-4f6d-9ed3-4c9bdd58bf27)

## Trwa pisanie [dokumentacji](../../wiki)

## Lista zmian
- Dodanie modułu wyliczającego wschody i zachody słońca bez połączenia z internetem (calendar_sq2ips.py)
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA (radioactive_sq2ips.py)
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobnego pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej (baltyk_sq2dk.py)
- Dodanie modułu ostrzeżeń meteorologicznych z IMGW PIB (meteoalert_sq2ips.py)
- Dodanie modułu stanu pogody z fizycznej stacji pogodowej przez UDP (meteostation_sq2ips.py)
- Dodanie modułu alertów pogody kosmicznej (spaceweather_sq2ips)
- Dodanie modułu pobierającego propagacje oraz poziom zakłuceń z hamqsl.com (propagation_sq2ips.py)
- Dodanie modułu pobierający pogodę z yr.no (meteo_yr_sq2ips.py) (testowy)
- Dodanie modułu informującego o stopniu zagrożenia pożarowego lasów (fires_sq2ips.py)
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

## Planowane prace
- Napisanie modułu pobierającego dane o burzach z antistorm.eu
- Napisanie modułu pobierającego dane ze stacji pogodowych przez APRS

## Licencja
LICENSE

## instalacja
Zakładamy, że mamy menedżer pakietów apt.

Przechodzimy do pustego katalogu, w którym chcemy umieścić program, np.:\
`cd ~/sr0wx`\
Jest to ważne ponieważ w tym katalogu domyślnie będzie się znajdować katalog z programem jaki i logiem.\
Tworzymy katalog logu:\
`mkdir ./logs`\
Aktualizujemy listy pakietów:\
`sudo apt update & sudo apt upgrade`\
Instalujemy potrzebne pakiety:\
`sudo apt install git curl php7.0 php-curl php-xml ffmpeg python3 python3-pip python3-dotenv`\
Teraz klonujemy repozytorium:\
`git clone https://github.com/sq2ips/sr0wx.git`\
Wchodzimy do niego:\
`cd sr0wx`\
Sprawdzamy czy system zarządza pakietami pythona:\
`pip3 install --upgrade pip`

Jeżeli dostaniemy błąd "error: externally-managed-environment" instalujemy biblioteki z apt:
- `sudo apt install python3-socketio python3-socketio-client python3-websocket python3-websockets python3-urllib3 python3-tqdm python3-tz python3-ephem python3-bs4 python3-pil python3-serial python3-numpy python3-pygame python3-importlib-metadata python3-dotenv`
- Jeżeli chcemy kożystać z PTT przez GPIO w Raspberry Pi: `sudo apt install python3-rpi.gpio`

Jeżeli nie:
- Instalujemy potrzebne biblioteki z pliku za pomocą pip: `pip3 install -r requirements.txt`
- Lub jeżeli jesteśmy na Raspberry Pi i chcemy korzystać z PTT przez GPIO: `pip3 install -r requirements-rpi.txt`

Pobieramy podmoduł: `git submodule update --init --recursive`

Teraz kopiujemy przykładowy plik .env:
`cp .env.example .env`

Uruchamiamy:
`python3 sr0wx.py`

TODO: instrukcja cron.
## Konfiguracja

Cała konfiguracja znajduje się w pliku `config.py`.
Znajdują się w nim sekcje dla poszczególnych modułów w których można ustawić różne parametry np. współrzędne do prognozy pogody, numer czujnika do stanu powietrza itp.
Na końcu pliku jest lista `modules` w której można ustawić jakie moduły są włączone.

Aby wyszukać id regionu ostrzeżeń do meteoalert_sq2ips należy:
`cd id_generator`\
`python meteoalert_getid.py -f <nazwa miasta lub powiatu>`\
np.\
`python meteoalert_getid.py -f gdynia`\
wynik:
Gdynia: 2262\
Id trzeba ustawić w sekcji modułu meteoalert_sq2ips.py w pliku config.py w zmiennej city_id, jest to tablica aby można było ustawić więcej regionów na raz np. city_id = \["2262", "2202"].

Wyszukiwanie id regionu ostrzeżeń hydrologicznych jest analogiczne, trzeba uruchomić skrypt `meteoalert_hydro_getid.py`. Id trzeba ustawić w zmiennej `hydronames`, jest to tablica aby możba było ustawić kilka regionów na raz.
