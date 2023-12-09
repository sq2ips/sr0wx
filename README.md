# sr0wx
Automatyczna stacja pogodowa sr0wx autorstwa [@sq6jnx](https://github.com/sq6jnx/sr0wx.py), z modułami i poprawkami autorstwa [@sq9atk](https://github.com/sq9atk/sr0wx) oraz moimi zmianami i dodatkami.

Program ten jest wykorzystywany przez Koło Naukowe UMG o nazwie Morski Klub Łączności "SZKUNER" SP2ZIE do obsługi automatycznej stacji pogodowej sr2wxg.

## Działanie
Program pobiera różne dane z internetu, np. stan pogody, prognozę pogody, ostrzeżenia imgw, poziom promieniowania i inne, konwertuje je na poszczególne słowa które są samplami audio a następnie odtwarza je.

## Lista zmian
- Dodanie modułu wyliczającego wschody i zachody słońca bez połączenia z internetem (calendar_sq2ips.py)
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA (radioactive_sq2ips.py)
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobnego pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej. Dodatkowo dodany jest katalog z samplami w formacie mp3 które stacja pobiera gdy nie zostały odnalezione (baltyk_sq2dk.py)
- Dodanie modułu ostrzeżeń meteorologicznych
- Przepisanie całej aplikacji z python 2 na 3
- Obsługa wieloprocesowości, wszystkie moduły uruchamiają się jednocześnie

## Licencja
LICENCE

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
`sudo apt-get install git curl php7.0 php-curl php-xml ffmpeg python3 python3-pip`\
Teraz klonujemy repozytorium:\
`git clone https://github.com/sq2ips/sr0wx.git`\
Wchodzimy do niego:\
`cd sr0wx`\
Instalujemy potrzebne biblioteki:\
`pip3 install -r requirements.txt`\
Lub jeżeli jesteśmy na Raspberry pi i chcemy korzystać z ptt przez gpio:\
`pip3 install -r requirements-rpi.txt`\
Wchodzimy do podkatalogu pyliczba i instalujemy moduł\
`cd pyliczba; sudo python3 setup.py install; cd ..`

Teraz kopiujemy przykładowy plik konfiguracyjny:
`cp config-example.py config.py`

Uruchamiamy:
`python3 sr0wx.py`

## Konfiguracja

Cała konfiguracja znajduje się w pliku `config.py`.
Znajdują się w nim sekcje dla poszczególnych modułów w których można ustawić różne parametry np. współrzędne do prognozy pogody, numer czujnika do stanu powietrza itp.
Na końcu pliku jest lista `modules` w której można ustawić jakie moduły są włączone.

## TODO
- Skrypt szukający id stacji i regionu do radioactive_sq2ips.py i meteoalert_sq2ips.py


