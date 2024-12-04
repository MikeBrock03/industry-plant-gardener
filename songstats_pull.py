import requests
import csv
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional

API_KEY = '862a47cc-cf07-44a1-8849-09eb723cffb4'
BASE_URL = 'https://api.songstats.com/enterprise/v1'
HEADERS = {
    'Accept': 'application/json',
    'Accept-Encoding': '',
    'apikey': API_KEY
}

class SongstatsAPI:
    def __init__(self):
        self.rate_limit_delay = 1

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limiting"""
        time.sleep(self.rate_limit_delay)
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 429:  # Rate limited
            time.sleep(60)
            return self._make_request(url, params)
        return response.json()

    def search_artist(self, name: str) -> Optional[str]:
        """Search for artist and return their Songstats ID"""
        url = f"{BASE_URL}/artists/search"
        params = {
            'q': name,
            'limit': 20,
            'offset': 0
        }
        
        try:
            data = self._make_request(url, params)
            if data.get('results') and len(data['results']) > 0:
                for result in data['results']:
                    if result['name'].lower() == name.lower():
                        return result['songstats_artist_id']
                return data['results'][0]['songstats_artist_id']
            return None
        except Exception as e:
            print(f"Error searching for {name}: {str(e)}")
            return None

    def get_artist_catalog(self, artist_id: str, target_date: str) -> List[Dict]:
        """Get artist catalog for tracks released before target date"""
        url = f"{BASE_URL}/artists/catalog"
        params = {
            'songstats_artist_id': artist_id,
            'limit': 100,
            'offset': 0
        }
        
        all_tracks = []
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        
        while True:
            response = self._make_request(url, params)
            print(f'response is: {response}')
            if not response.get('catalog'):
                break
                
            for track in response['catalog']:
                try:
                    release_date = track.get('release_date')
                    if release_date:
                        release_date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                        if release_date_obj <= target_date_obj:
                            all_tracks.append(track)
                except (ValueError, TypeError) as e:
                    print(f"Error processing release date for track {track.get('title', 'unknown')}: {e}")
                    continue
                
            if not response.get('next_url'):
                break
                
            params['offset'] += params['limit']
            
        return all_tracks

    def get_track_info(self, track_id: str) -> List[str]:
        """Get track info including genres"""
        url = f"{BASE_URL}/tracks/info"
        params = {
            'songstats_track_id': track_id
        }
        
        try:
            response = self._make_request(url, params)
            if response.get('track_info') and response['track_info'].get('genres'):
                return response['track_info']['genres']
            return []
        except Exception as e:
            print(f"Error getting track info: {str(e)}")
            return []

    def get_track_historic_stats(self, track_id: str, artist_id: str, original_date: str) -> Optional[int]:
        """
        Get historic stats for a track, trying each month for up to a year if the original date has no data.
        Returns None if no streaming data is found within a year.
        """
        try:
            # Convert original date to datetime for manipulation
            date_obj = datetime.strptime(original_date, '%Y-%m-%d')
            
            # Try for up to 12 months
            for _ in range(12):
                date_str = date_obj.strftime('%Y-%m-%d')
                url = f"{BASE_URL}/tracks/historic_stats"
                params = {
                    'songstats_track_id': track_id,
                    'songstats_artist_id': artist_id,
                    'source': 'spotify',
                    'start_date': date_str,
                    'end_date': date_str
                }
                
                response = self._make_request(url, params)
                print(f'got response for track. response is {response}')
                if (response.get('stats') and 
                    len(response['stats']) > 0 and 
                    response['stats'][0].get('data') and 
                    response['stats'][0]['data'].get('history')):
                    
                    history = response['stats'][0]['data']['history']
                    for entry in history:
                        streams = entry.get('streams_total')
                        if streams and streams > 0:
                            return streams
                
                # Move to next month
                date_obj = (date_obj.replace(day=1) + timedelta(days=32)).replace(day=1)
            
            # If we've tried 12 months and found nothing, return None
            return None
            
        except Exception as e:
            print(f"Error getting historic stats: {str(e)}")
            return None

def process_artist_data():
    artists_data = [
        ("Tones and I", "2019-11-01"),
        ("Tom Misch", "2018-04-01"),
        ("Boy Pablo", "2018-05-01"),
        ("Yellow Days", "2018-04-01"),
        ("Gus Dapperton", "2017-05-01"),
        ("Crumb", "2017-06-01"),
        ("Summer Salt", "2014-09-01"),
        ("Benee", "2019-11-01"),
        ("Surfaces", "2019-01-06"),
        ("Powfu", "2020-02-01"),
        ("Beach Bunny", "2018-08-01"),
        ("The Marias", "2018-09-01"),
        ("Sales", "2016-04-01"),
        ("Mother Mother", "2008-09-01"),
        ("Nilüfer Yanya", "2020-12-01"),
        ("Eyedress", "2019-12-01"),
        ("Japanese Breakfast", "2021-06-01"),
        ("Mitski", "2018-08-01"),
        ("PinkPantheress", "2021-10-01"),
        ("Magdalena Bay", "2021-10-01"),
        ("Spill Tab", "2020-08-01"),
        ("Wednesday", "2021-08-01"),
        ("Men I Trust", "2016-06-01"),
        ("Steve Lacy", "2022-07-01"),
        ("Ice Spice", "2022-08-01"),
        ("Omar Apollo", "2022-04-01"),
        ("Ethel Cain", "2022-05-01"),
        ("Alex G", "2012-11-05"),
        ("Boygenius", "2023-03-31"),
        ("NewJeans", "2023-01-01"),
        ("d4vd", "2022-07-01"),
        ("Laufey", "2023-05-01"),
        ("Faye Webster", "2019-05-01"),
        ("Holly Humberstone", "2020-01-01"),
        ("Chappell Roan", "2023-09-01"),
        ("The Backseat Lovers", "2019-01-01"),
        ("Lovejoy", "2021-05-01"),
        ("Gotye", "2011-12-01"),
        ("The Lumineers", "2012-04-01"),
        ("Vance Joy", "2014-09-01"),
        ("Hozier", "2014-09-01"),
        ("alt-J", "2012-09-01"),
        ("Mac DeMarco", "2012-10-01"),
        ("ROLE MODEL", "2017-09-01"),
        ("Clairo", "2017-08-01"),
        ("Mxmtoon", "2023-11-01"),
        ("Current Joys", "2018-02-01"),
        ("Cuco", "2017-05-01"),
        ("Snail Mail", "2018-06-01"),
        ("Sidney Gish", "2017-12-01"),
        ("Mk.gee", "2018-05-01"),
        ("Junior Varisty", "2021-03-01"),
        ("TEMPOREX", "2017-01-01"),
        ("Beabadoobee", "2017-11-01"),
        ("Dreamer Isioma", "2020-01-29"),
        ("Dora Jar", "2021-03-05"),
        ("Lewis Del Mar", "2016-01-01"),
        ("Ginger Root", "2019-06-01"),
        ("Hannah Jadagu", "2021-04-01"),
        ("Binki", "2019-10-01"),
        ("MICHELLE", "2018-09-01"),
        ("Dazy", "2021-08-01"),
        ("Wet Leg", "2021-06-01"),
        ("Native Sun", "2018-11-01"),
        ("Indigo De Souza", "2021-08-01"),
        ("Horsegirl", "2022-06-01"),
        ("They Hate Change", "2022-05-01"),
        ("Momma", "2022-06-01"),
        ("Soul Glo", "2022-03-01"),
        ("Jane Remover", "2021-11-01"),
        ("Jockstrap", "2022-09-01"),
        ("Geese", "2021-10-01"),
        ("Bar Italia", "2023-05-01"),
        ("Blondshell", "2023-04-01"),
        ("Militarie Gun", "2023-06-01"),
        ("Scowl", "2023-02-01"),
        ("Pretty Sick", "2022-09-01"),
        ("Lifeguard", "2022-08-05"),
        ("Voodoo Bandits", "2022-08-01"),
        ("Hotline TNT", "2023-11-01"),
        ("Field Medic", "2016-11-01"),
        ("Bellows", "2019-02-22"),
        ("SPY", "2021-09-01"),
        ("Machine Girl", "2014-02-01"),
        ("Fire-Toolz", "2018-08-01"),
        ("Container", "2020-03-01"),
        ("Black Dresses", "2020-04-01"),
        ("Divide and Dissolve", "2021-01-01"),
        ("Floatie", "2021-03-01"),
        ("Horse Lords", "2020-03-01"),
        ("LICE", "2021-01-01"),
        ("Drahla", "2019-05-01"),
        ("Uranium Club", "2019-03-01"),
        ("Lewsberg", "2017-11-01"),
        ("Sam Amidon", "2020-10-23"),
        ("Tenci", "2020-06-01"),
        ("Lomelda", "2020-09-01"),
        ("Julie Byrne", "2023-07-01"),
        ("standards", "2020-08-01"),
        ("Feed Me Jack", "2015-06-01")
    ]
    
    api = SongstatsAPI()
    
    with open('artist_historical_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Artist', 'Song', 'Streams', 'Genre'])
        
        for artist_name, original_date in artists_data:
            print(f"Processing {artist_name}...")
            
            artist_id = api.search_artist(artist_name)
            print(f"Found artist id. Artist ID is: {artist_name}...")
            if not artist_id:
                print(f"Could not find artist: {artist_name}")
                continue
            print(f"Trying to find tracks...")
            tracks = api.get_artist_catalog(artist_id, original_date)
            print(f"Found {len(tracks)} tracks for {artist_name} before {original_date}")
            
            for track in tracks:
                try:
                    # Get streams first - if no streams found, skip this track
                    streams = api.get_track_historic_stats(
                        track['songstats_track_id'],
                        artist_id,
                        original_date
                    )
                    
                    if streams is None:
                        print(f"No streaming data found within a year for track: {track['title']}")
                        continue
                    
                    # If we have streams, get the genres and write to CSV
                    genres = api.get_track_info(track['songstats_track_id'])
                    genre_str = ', '.join(genres) if genres else ''
                    
                    formatted_streams = f"{streams:,}"
                    
                    writer.writerow([
                        artist_name,
                        track['title'],
                        formatted_streams,
                        genre_str
                    ])
                    
                except Exception as e:
                    print(f"Error processing track {track.get('title', 'unknown')}: {str(e)}")

if __name__ == '__main__':
    process_artist_data()