import requests
import sys

url = "https://antistorm.eu/api-v1/szukaj-miasta.php"

city_id = requests.post(url, data={"miasto":sys.argv[1].capitalize()}).text

print(city_id)