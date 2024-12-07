import requests
import csv
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
from functools import wraps

API_KEY = '9f8d71ec-e5dd-4cd0-a005-68064d3504e4'
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
        """Make API request with rate limiting and timeout checking"""
        time.sleep(self.rate_limit_delay)
        start_time = time.time()
        
        while True:
            try:
                response = requests.get(url, headers=HEADERS, params=params)
                if response.status_code == 429:  # Rate limited
                    time.sleep(60)
                    if time.time() - start_time > 120:  # 2 minutes timeout
                        return None
                    continue
                return response.json()
            except Exception as e:
                if time.time() - start_time > 120:  # 2 minutes timeout
                    return None
                time.sleep(10)
                continue

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
        """
        Get artist catalog for tracks released:
        - Before: 11 months prior to target date
        - After: any time in the past
        """
        url = f"{BASE_URL}/artists/catalog"
        params = {
            'songstats_artist_id': artist_id,
            'limit': 100,
            'offset': 0
        }
        
        all_tracks = []
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        upper_bound = target_date_obj - timedelta(days=11*30)  # 11 months before target date
        
        print(f"Including tracks released before {upper_bound.strftime('%Y-%m-%d')}")
        
        while True:
            start_time = time.time()
            response = self._make_request(url, params)
            
            if not response or not response.get('catalog'):
                break
                
            for track in response['catalog']:
                try:
                    release_date = track.get('release_date')
                    if release_date:
                        release_date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                        # Only include tracks released BEFORE the upper bound
                        if release_date_obj <= upper_bound:
                            all_tracks.append(track)
                except (ValueError, TypeError) as e:
                    print(f"Error processing release date for track {track.get('title', 'unknown')}: {e}")
                    continue
                
            if not response.get('next_url') or time.time() - start_time > 120:
                break
                
            params['offset'] += params['limit']
            
        return all_tracks

    def get_track_historic_stats(self, track_id: str, artist_id: str, target_date: str) -> Optional[int]:
        """
        Get historic stats for a track on target date.
        If target date has no streams, find earliest non-zero stream count.
        """
        try:
            url = f"{BASE_URL}/tracks/historic_stats"
            params = {
                'songstats_track_id': track_id,
                'songstats_artist_id': artist_id,
                'source': 'spotify'
            }
            
            response = self._make_request(url, params)
            if (response and response.get('stats') and 
                len(response['stats']) > 0 and 
                response['stats'][0].get('data') and 
                response['stats'][0]['data'].get('history')):
                
                history = response['stats'][0]['data']['history']
                
                # First check target date specifically
                target_streams = None
                for entry in history:
                    if entry.get('date') == target_date:
                        target_streams = entry.get('streams_total')
                        if target_streams and target_streams > 0:
                            return target_streams
                
                # If target date had no streams, find earliest non-zero value
                history = sorted(history, key=lambda x: x.get('date', ''))
                for entry in history:
                    streams = entry.get('streams_total')
                    if streams and streams > 0:
                        return streams
            
            return None
                
        except Exception as e:
            print(f"Error getting historic stats: {str(e)}")
            return None

def process_artist_data():
    artists_data = [
        ("Boygenius", "2024-03-31"),
        ("NewJeans", "2024-01-01"),
        ("d4vd", "2023-07-01"),
        ("Laufey", "2024-05-01"),
        ("Faye Webster", "2020-05-01"),
        ("Holly Humberstone", "2021-01-01"),
        ("Chappell Roan", "2024-09-01"),
        ("The Backseat Lovers", "2020-01-01"),
        ("Lovejoy", "2022-05-01"),
        ("Gotye", "2012-12-01"),
        ("The Lumineers", "2013-04-01"),
        ("Vance Joy", "2015-09-01"),
        ("Hozier", "2015-09-01"),
        ("alt-J", "2013-09-01"),
        ("Mac DeMarco", "2013-10-01"),
        ("ROLE MODEL", "2018-09-01"),
        ("Clairo", "2018-08-01"),
        ("Mxmtoon", "2024-11-01"),
        ("Current Joys", "2019-02-01"),
        ("Cuco", "2018-05-01"),
        ("Snail Mail", "2019-06-01"),
        ("Sidney Gish", "2018-12-01"),
        ("Mk.gee", "2019-05-01"),
        ("Junior Varisty", "2022-03-01"),
        ("TEMPOREX", "2018-01-01"),
        ("Beabadoobee", "2018-11-01"),
        ("Dreamer Isioma", "2021-01-29"),
        ("Dora Jar", "2022-03-05"),
        ("Lewis Del Mar", "2017-01-01"),
        ("Ginger Root", "2020-06-01"),
        ("Hannah Jadagu", "2022-04-01"),
        ("Binki", "2020-10-01"),
        ("MICHELLE", "2019-09-01"),
        ("Dazy", "2022-08-01"),
        ("Wet Leg", "2022-06-01"),
        ("Native Sun", "2019-11-01"),
        ("Indigo De Souza", "2022-08-01"),
        ("Horsegirl", "2023-06-01"),
        ("They Hate Change", "2023-05-01"),
        ("Momma", "2023-06-01"),
        ("Soul Glo", "2023-03-01"),
        ("Jane Remover", "2022-11-01"),
        ("Jockstrap", "2023-09-01"),
        ("Geese", "2022-10-01"),
        ("Bar Italia", "2024-05-01"),
        ("Blondshell", "2024-04-01"),
        ("Militarie Gun", "2024-06-01"),
        ("Scowl", "2024-02-01"),
        ("Pretty Sick", "2024-09-01"),
        ("Lifeguard", "2023-08-05"),
        ("Voodoo Bandits", "2023-08-01"),
        ("Hotline TNT", "2024-11-01"),
        ("Field Medic", "2017-11-01"),
        ("Bellows", "2020-02-22"),
        ("SPY", "2022-09-01"),
        ("Machine Girl", "2015-02-01"),
        ("Fire-Toolz", "2019-08-01"),
        ("Container", "2021-03-01"),
        ("Black Dresses", "2021-04-01"),
        ("Divide and Dissolve", "2022-01-01"),
        ("Floatie", "2022-03-01"),
        ("Horse Lords", "2021-03-01"),
        ("LICE", "2022-01-01"),
        ("Drahla", "2020-05-01"),
        ("Uranium Club", "2020-03-01"),
        ("Lewsberg", "2018-11-01"),
        ("Sam Amidon", "2021-10-23"),
        ("Tenci", "2021-06-01"),
        ("Lomelda", "2021-09-01"),
        ("Julie Byrne", "2024-07-01"),
        ("standards", "2021-08-01"),
        ("Feed Me Jack", "2016-06-01")
    ]
    
    api = SongstatsAPI()
    csv_file = open('artist_historical_data.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(['Artist', 'Song', 'Streams', 'Genre'])
    
    try:
        for artist_name, original_date in artists_data:
            print(f"Processing {artist_name}...")
            
            start_time = time.time()
            artist_id = api.search_artist(artist_name)
            
            if time.time() - start_time > 120 or not artist_id:  
                print(f"Timeout while searching for artist {artist_name}")
                continue
                
            if not artist_id:
                print(f"Could not find artist: {artist_name}")
                continue
                
            print(f"Found artist id. Artist ID is: {artist_name}...")
            print(f"Trying to find tracks...")
            
            tracks = api.get_artist_catalog(artist_id, original_date)
            
            if time.time() - start_time > 120:
                print(f"Timeout while getting catalog for {artist_name}")
                continue
                
            print(f"Found {len(tracks)} tracks for {artist_name} before {original_date}")
            
            for track in tracks:
                try:
                    track_start_time = time.time()
                    
                    # Get streams first - if no streams found, skip this track
                    streams = api.get_track_historic_stats(
                        track['songstats_track_id'],
                        artist_id,
                        original_date
                    )
                    
                    if time.time() - track_start_time > 120:
                        print(f"Timeout while getting stats for track {track.get('title', 'unknown')}")
                        continue
                    
                    if streams is None:
                        print(f"No streaming data found for track: {track['title']}")
                        continue
                    
                    # If we have streams, get the genres
                    genre_str = '' 
                    formatted_streams = f"{streams:,}"
                    
                    writer.writerow([
                        artist_name,
                        track['title'],
                        formatted_streams,
                        genre_str
                    ])
                    
                    # Flush the CSV after each write to ensure data is saved
                    csv_file.flush()
                    
                except Exception as e:
                    print(f"Error processing track {track.get('title', 'unknown')}: {str(e)}")
                    continue

    except Exception as e:
        print(f"Major error encountered: {str(e)}")

    finally:
        # Make sure we always close the CSV file
        csv_file.close()

if __name__ == '__main__':
    process_artist_data()