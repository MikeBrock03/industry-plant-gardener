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
            if not response.get('catalog'):
                break
                
            # Filter tracks released before target date
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
    artists_data = [
        ("Tones and I", "2019-11-01"),
        # ... rest of the list ...
    ]
    
    api = SongstatsAPI()
    
    with open('artist_historical_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Artist', 'Song', 'Streams', 'Genre'])
        
        for artist_name, original_date in artists_data:
            print(f"Processing {artist_name}...")
            
            # Search for artist ID
            artist_id = api.search_artist(artist_name)
            if not artist_id:
                print(f"Could not find artist: {artist_name}")
                continue
            
            # Get catalog
            tracks = api.get_artist_catalog(artist_id, original_date)
            print(f"Found {len(tracks)} tracks for {artist_name} before {original_date}")
            
            # Process each track
            for track in tracks:
                try:
                    stats = api.get_track_historic_stats(
                        track['songstats_track_id'],
                        artist_id,
                        original_date
                    )
                    
                    if stats.get('stats') and stats['stats'][0].get('data'):
                        streams = stats['stats'][0]['data'].get('plays', 0)
                        formatted_streams = f"{streams:,}"
                        
                        genres = track.get('genres', [''])[0] if track.get('genres') else ''
                        
                        writer.writerow([
                            artist_name,
                            track['title'],
                            formatted_streams,
                            genres
                        ])
                        
                except Exception as e:
                    print(f"Error processing track {track.get('title', 'unknown')}: {str(e)}")

if __name__ == '__main__':
    process_artist_data()