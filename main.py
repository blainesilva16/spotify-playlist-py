import re,requests,os,dotenv
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

dotenv.load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
username = os.getenv("USERNAME")

date = input("Which date do you want to travel to? Type the date in the format: YYYY-MM-DD ")
while not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
    print("Invalid format.")
    date = input("Which date do you want to travel to? Type the date in the format: YYYY-MM-DD ")
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) "
                  "Gecko/20100101 Firefox/131.0"
}
url = f"https://www.billboard.com/charts/hot-100/{date}/"


response = requests.get(url,headers=header)

soup = BeautifulSoup(response.text,"html.parser")

# names = soup.find_all(name="h3",id="title-of-a-story",class_="c-title")
all_songs = soup.select(selector='li > ul:first-child > li:first-child > h3:first-child')
titles = [song.getText().strip() for song in all_songs]


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="https://foo.com",
                                               scope="playlist-modify-private",
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               username=username,
                                    ))
user_id = sp.current_user()["id"]
song_uris = []
year = date.split("-")[0]
n = 1
for song in titles:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(n,result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
    n+=1

playlist = sp.user_playlist_create(user=user_id,
                                   name=f"{date.split("-")[2]}/{date.split("-")[1]}/{date.split("-")[0]} - Billboard 100",
                                   public=False,
                                   collaborative=False,
                                   description=f'A playlist with the top 100 songs from Billboard on the day {date.split("-")[2]}/{date.split("-")[1]}/{date.split("-")[0]}.')

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name'])