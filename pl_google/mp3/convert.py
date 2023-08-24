import os
import glob
b = 0
a = (glob.glob("/home/sr0wx/sr0wx/pl_google/mp3/*.mp3")) 
c = len(a)
while b < len(a):
    print(str(b/len(a)*100) + "%")
    wyj = a[b].replace('.mp3', '') + ".ogg"
    print("--- konwertowanie " + a[b] + " na " + wyj)
    os.system("ffmpeg -y -i " + a[b] + " -ar 32000  -ab 48000 -acodec libvorbis " + wyj)
    b = b + 1
os.system("cp *.ogg ..")
os.system("mv *.ogg old")
