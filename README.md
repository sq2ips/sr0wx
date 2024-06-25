# sr0wx
Ten projekt to fork automatycznej radioamatorskiej stacja pogodowej SR0WX autorstwa [@sq6jnx](https://github.com/sq6jnx/sr0wx.py), rozwijanej przez [@sq9atk](https://github.com/sq9atk/sr0wx), który staram się rozwijać i unowocześniać.

Program ten jest wykorzystywany przez Koło Naukowe UMG o nazwie Morski Klub Łączności "SZKUNER" SP2ZIE do obsługi automatycznej stacji pogodowej [SR2WXG](https://www.sp2zie.pl/index.php/stacja-systemu-sr0wx).

## Działanie
Program pobiera różne dane z internetu, np. stan pogody, prognozę pogody, ostrzeżenia imgw, poziom promieniowania i inne, konwertuje je na poszczególne słowa które są samplami audio a następnie odtwarza je. Do komputera podłączone jest radio, które odtwarza komunikat na paśmie amatorskim na częstotliwości 144.950 MHz.

## Lista zmian
- Dodanie modułu wyliczającego wschody i zachody słońca bez połączenia z internetem (calendar_sq2ips.py)
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA (radioactive_sq2ips.py)
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobnego pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej (baltyk_sq2dk.py)
- Dodanie modułu ostrzeżeń meteorologicznych z IMGW PIB (meteoalert_sq2ips.py)
- Dodanie modułu stanu pogody z fizycznej stacji pogodowej przez UDP (meteostation_sq2ips.py)
- Dodanie modułu alertów pogody kosmicznej (spaceweather_sq2ips)
- Dodanie modułu pobierającego propagacje oraz poziom zakłuceń z hamqsl.com (propagation_sq2ips.py)
- Przepisanie całej aplikacji z python 2 na 3
- Dodanie generatora sampli napisanego w pythonie
- Obsługa wieloprocesowości, wszystkie moduły uruchamiają się jednocześnie
- Niejawne parametry konkretnej stacji (klucze api itp.) są przechowywane w pliku .env
- Zmiana urllib na requests w kilku modułach dla zminimalizowania ilości błędów pobierania.
- Dodanie trybu testowego, moduły są uruchamiane ale nie są odtwarzane sample
- Zmiana biblioteki do pobierania danych z urllib na requests, wielokrotne próby pobierania przy błedzie pobierania

## W toku
- Praca nad modułuem pobierającym pogodę z yr.no

## Licencja
LICENSE

## instalacja
Zakładamy, że mamy menedżer pakietów apt.

Przechodzimy do pustego katalogu w którym chcemy umieścić program, np.:\
`cd ~/sr0wx`\
Jest to ważne ponieważ w tym katalogu domyślnie będzie się znajdować katalog z programem jaki i logiem.\
Tworzymy katalog logu:\
`mkdir ./logs`\
Aktualizujemy listy pakietów:\
`sudo apt-get update`\
Instalujemy potrzebne pakiety:\
`sudo apt-get install git curl php7.0 php-curl php-xml ffmpeg python3 python3-pip python3-dotenv`\
Teraz klonujemy repozytorium:\
`git clone https://github.com/sq2ips/sr0wx.git`\
Wchodzimy do niego:\
`cd sr0wx`\
Jeżeli system 
Instalujemy potrzebne biblioteki:\
`pip3 install -r requirements.txt`\
Lub jeżeli jesteśmy na Raspberry pi i chcemy korzystać z ptt przez gpio:\
`pip3 install -r requirements-rpi.txt`\
Wchodzimy do podkatalogu pyliczba i instalujemy moduł\
`cd pyliczba; sudo python3 setup.py install; cd ..`

Teraz kopiujemy przykładowy plik .env:
`cp .env.example .env`

Uruchamiamy:
`python3 sr0wx.py`

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
Id trzeba ustawić w sekcji modułu meteoalert_sq2ips.py w pliku config.py w zmiennej city_id.\

Wyszukiwanie id regionu ostrzeżeń hydrologicznych jest analogiczne, trzeba uruchomić skrypt `meteoalert_hydro_getid.py`. Id trzeba ustawić w zmiennej `hydronames`, jest to tablica aby możba było ustawić kilka regionów na raz.

## TODO
- Dokumentacja

## Planowanie zmiany
- Dodanie modułu pobierającego dane ze stacji pogodowych przez APRS
