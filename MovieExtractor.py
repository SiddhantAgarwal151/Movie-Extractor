import requests
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai

# Load environment variables for API keys
load_dotenv()

class MediaInfoSystem:
    def __init__(self):
        # API Keys - you'll need to sign up for these services
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.watchmode_api_key = os.getenv('WATCHMODE_API_KEY')
        
        # Configure OpenAI for natural language processing
        openai.api_key = self.openai_api_key

    def search_media(self, query: str, media_type: str = 'multi') -> List[Dict]:
        """
        Search for movies or TV shows using TMDB API
        :param query: Search term
        :param media_type: Type of media (multi, movie, tv)
        :return: List of search results
        """
        base_url = 'https://api.themoviedb.org/3/search/{}'.format(media_type)
        params = {
            'api_key': self.tmdb_api_key,
            'query': query,
            'language': 'en-US'
        }
        
        response = requests.get(base_url, params=params)
        return response.json().get('results', [])

    def get_media_details(self, media_id: int, media_type: str) -> Dict:
        """
        Get detailed information about a specific movie or TV show
        :param media_id: TMDB ID of the media
        :param media_type: Type of media (movie or tv)
        :return: Detailed media information
        """
        base_url = f'https://api.themoviedb.org/3/{media_type}/{media_id}'
        params = {
            'api_key': self.tmdb_api_key,
            'append_to_response': 'credits,watch_providers'
        }
        
        response = requests.get(base_url, params=params)
        return response.json()

    def get_streaming_platforms(self, media_id: int, media_type: str) -> Dict:
        """
        Retrieve streaming platforms using WatchMode API
        :param media_id: TMDB ID of the media
        :param media_type: Type of media
        :return: Dictionary of streaming platforms
        """
        # WatchMode API endpoint for streaming sources
        url = f'https://api.watchmode.com/v1/title/{media_type}-{media_id}/sources/'
        params = {
            'apiKey': self.watchmode_api_key
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def filter_by_genre(self, media_list: List[Dict], genre_names: List[str]) -> List[Dict]:
        """
        Filter media by specified genres
        :param media_list: List of media items
        :param genre_names: List of genre names to filter by
        :return: Filtered list of media
        """
        # Get genre mappings from TMDB
        genres_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={self.tmdb_api_key}'
        genre_response = requests.get(genres_url).json()
        genre_map = {g['name'].lower(): g['id'] for g in genre_response['genres']}
        
        # Convert genre names to IDs
        genre_ids = [genre_map[g.lower()] for g in genre_names if g.lower() in genre_map]
        
        return [
            media for media in media_list 
            if any(genre_id in media.get('genre_ids', []) for genre_id in genre_ids)
        ]

    def generate_recommendation(self, media_details: Dict) -> str:
        """
        Use OpenAI to generate a personalized recommendation
        :param media_details: Detailed media information
        :return: AI-generated recommendation
        """
        prompt = f"""
        Given the following media details, provide a personalized recommendation:
        Title: {media_details.get('title', media_details.get('name', 'Unknown'))}
        Overview: {media_details.get('overview', 'No overview available')}
        Genres: {[genre['name'] for genre in media_details.get('genres', [])]}
        
        Write a compelling recommendation that highlights unique aspects of this media.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie and TV show recommendation expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

def main():
    # Example usage
    system = MediaInfoSystem()
    
    # Search for a movie or TV show
    search_results = system.search_media('Stranger Things')
    
    # Get details of the first result
    if search_results:
        first_result = search_results[0]
        details = system.get_media_details(first_result['id'], first_result['media_type'])
        
        # Get streaming platforms
        platforms = system.get_streaming_platforms(first_result['id'], first_result['media_type'])
        
        # Generate AI recommendation
        recommendation = system.generate_recommendation(details)
        
        print("Media Details:", details)
        print("\nStreaming Platforms:", platforms)
        print("\nAI Recommendation:", recommendation)

if __name__ == "__main__":
    main()