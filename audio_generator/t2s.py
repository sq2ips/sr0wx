from responsive_voice.voices import PolishPoland

pl = PolishPoland()

slowa = ["Za chwilę zostanie nadany noworoczny obrazek SSTV w trybie PD 120"]
a = 0
print("rozpoczecie generowania:")

while a < len(slowa):
    print("generowanie elementu numer " + str(a) + " tresc " + slowa[a])
    pl.say(slowa[a], slowa[a] + ".mp3")
    a = a + 1

print("koniec generowania")
