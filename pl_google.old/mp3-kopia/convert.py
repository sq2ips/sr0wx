import os
import glob
b = 0
a = (glob.glob("/home/sr0wx/sr0wx/pl_google/mp3/*.mp3")) 
while b < len(a):
    os.system("ffmpeg -y -i " + a[b] + " -ar 32000  -ab 48000 -acodec libvorbis " + a[b] + ".ogg")
    a = a + 1
