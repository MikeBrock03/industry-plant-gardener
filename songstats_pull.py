import requests
import csv
import json
from datetime import datetime
import time
from typing import Dict, List, Optional

API_KEY = '862a47cc-cf07-44a1-8849-09eb723cffb4'
BASE_URL = 'https://api.songstats.com/enterprise/v1'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

class SongstatsAPI:
    def __init__(self):
        self.rate_limit_delay = 1  # Delay between API calls to avoid rate limiting

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limiting"""
        time.sleep(self.rate_limit_delay)
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 429:  # Rate limited
            time.sleep(60)  # Wait longer if rate limited
            return self._make_request(url, params)
        return response.json()

    def search_artist(self, name: str) -> Optional[str]:
        """Search for artist and return their Songstats ID"""
        url = f"{BASE_URL}/artists/search"
        params = {'q': name, 'limit': 5}
        
        try:
            data = self._make_request(url, params)
            if data.get('results') and len(data['results']) > 0:
                # Using the correct response structure
                return data['results'][0]['songstats_artist_id']
            return None
        except Exception as e:
            print(f"Error searching for {name}: {str(e)}")
            return None

    def get_artist_catalog(self, artist_id: str) -> List[Dict]:
        """Get complete artist catalog"""
        url = f"{BASE_URL}/artists/catalog"
        params = {
            'songstats_artist_id': artist_id,
            'limit': 100,
            'offset': 0
        }
        
        all_tracks = []
        while True:
            response = self._make_request(url, params)
            if not response.get('catalog'):
                break
                
            all_tracks.extend(response['catalog'])
            
            if not response.get('next_url'):
                break
                
            params['offset'] += params['limit']
            
        return all_tracks

    def get_track_historic_stats(self, track_id: str, artist_id: str, date: str) -> Dict:
        """Get historic stats for a track on a specific date"""
        url = f"{BASE_URL}/tracks/historic_stats"
        params = {
            'songstats_track_id': track_id,
            'songstats_artist_id': artist_id,
            'source': 'spotify',
            'start_date': date,
            'end_date': date
        }
        return self._make_request(url, params)

def process_artist_data():
    # Load artist data (your existing artists_data list here)
    artists_data = [
        ("Tones and I", "2017-11-01"),
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
    
    # Create two files: one for IDs and one for the final data
    with open('artist_ids.json', 'w') as id_file, \
         open('artist_historical_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        
        writer = csv.writer(csv_file)
        writer.writerow(['Artist', 'Track', 'Date', 'Streams', 'Genres'])
        artist_ids = {}
        
        # First pass: get all artist IDs
        print("Phase 1: Collecting artist IDs...")
        for artist_name, date in artists_data:
            print(f"Searching for {artist_name}...")
            artist_id = api.search_artist(artist_name)
            if artist_id:
                artist_ids[artist_name] = artist_id
                print(f"Found ID for {artist_name}: {artist_id}")
            else:
                print(f"Could not find artist: {artist_name}")
        
        # Save artist IDs
        json.dump(artist_ids, id_file, indent=2)
        
        # Second pass: collect historical data
        print("\nPhase 2: Collecting historical data...")
        for artist_name, date in artists_data:
            if artist_name not in artist_ids:
                continue
                
            artist_id = artist_ids[artist_name]
            print(f"Processing {artist_name} ({date})...")
            
            try:
                tracks = api.get_artist_catalog(artist_id)
                for track in tracks:
                    try:
                        stats = api.get_track_historic_stats(
                            track['songstats_track_id'],
                            artist_id,
                            date
                        )
                        
                        if stats.get('stats') and stats['stats'][0].get('data'):
                            streams = stats['stats'][0]['data'].get('plays', 0)
                            genres = ', '.join(track.get('genres', []))
                            
                            writer.writerow([
                                artist_name,
                                track['title'],
                                date,
                                streams,
                                genres
                            ])
                            
                    except Exception as e:
                        print(f"Error processing track {track.get('title', 'unknown')}: {str(e)}")
                        
            except Exception as e:
                print(f"Error processing artist {artist_name}: {str(e)}")

if __name__ == '__main__':
    process_artist_data()