import sys
import os
import requests
import pandas as pd
from typing import Dict, Any, List
from dotenv import load_dotenv

class AdvancedMediaSearch:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # API Keys
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        self.watchmode_api_key = os.getenv('WATCHMODE_API_KEY')

        # Base URLs
        self.tmdb_base_url = "https://api.themoviedb.org/3"

        # Preload genre mappings
        self.movie_genres = self._get_genre_mappings("movie")
        self.tv_genres = self._get_genre_mappings("tv")
        self.platform_mapping = self._load_platform_mapping()

    def _load_platform_mapping(self) -> Dict:
        """Mapping for streaming platforms using Watchmode IDs."""
        return {
            203: "Netflix",
            119: "Hulu",
            9: "Amazon Prime Video",
            372: "Disney+",
            387: "HBO Max",
            531: "Apple TV+",
            254: "Peacock",
        }

    def _get_genre_mappings(self, media_type: str) -> Dict:
        """Fetch TMDB genre mappings."""
        genre_url = f"{self.tmdb_base_url}/genre/{media_type}/list"
        params = {"api_key": self.tmdb_api_key}

        try:
            response = requests.get(genre_url, params=params)
            genre_data = response.json()
            return {g["name"].lower(): g["id"] for g in genre_data.get("genres", [])}
        except Exception as e:
            print(f"Error fetching {media_type} genres: {e}")
            return {}

    def advanced_search(self, 
                        query: str = "", 
                        media_type: str = "movie", 
                        filters: Dict = None) -> pd.DataFrame:
        """
        Comprehensive media search with multiple filtering options
        :param query: Search query
        :param media_type: Type of media (movie/tv)
        :param filters: Dictionary of additional filters
        :return: DataFrame of search results
        """
        # Normalize filters
        filters = filters or {}
        genre = filters.get('genre')
        release_year = filters.get('release_year')

        # Perform search based on filters
        if genre:
            results = self.fetch_by_genre(genre, media_type, release_year)
        elif release_year:
            results = self.fetch_by_year(release_year, media_type)
        else:
            # Fallback to basic search if no specific filters
            results = self._basic_search(query, media_type)

        return self.convert_results_to_dataframe(results)

    def _basic_search(self, query: str, media_type: str) -> List[Dict]:
        """
        Basic search using TMDB search endpoint
        :param query: Search term
        :param media_type: Type of media
        :return: List of search results
        """
        search_url = f"{self.tmdb_base_url}/search/{media_type}"
        params = {
            "api_key": self.tmdb_api_key,
            "query": query,
            "language": "en-US",
            "page": 1
        }

        try:
            response = requests.get(search_url, params=params)
            return response.json().get("results", [])
        except Exception as e:
            print(f"Error in basic search: {e}")
            return []

    def fetch_by_genre(self, genre: str, media_type: str = "movie", release_year: int = None) -> List[Dict]:
        """Fetch movies or TV shows by genre using TMDB Discover API."""
        genre_map = self.movie_genres if media_type == "movie" else self.tv_genres

        if genre.lower() not in genre_map:
            print(f"Genre '{genre}' not found. Available genres:")
            print("\n".join(sorted(genre_map.keys())))
            return []

        genre_id = genre_map[genre.lower()]
        discover_url = f"{self.tmdb_base_url}/discover/{media_type}"

        params = {
            "api_key": self.tmdb_api_key,
            "with_genres": genre_id,
            "language": "en-US",
            "page": 1
        }

        if release_year:
            # For movies, use primary_release_year
            # For TV shows, use first_air_date_year
            key = "primary_release_year" if media_type == "movie" else "first_air_date_year"
            params[key] = release_year

        try:
            response = requests.get(discover_url, params=params)
            results = response.json().get("results", [])
            return results
        except Exception as e:
            print(f"Error fetching by genre: {e}")
            return []

    def fetch_by_year(self, year: int, media_type: str = "movie") -> List[Dict]:
        """Fetch movies or TV shows by release year."""
        discover_url = f"{self.tmdb_base_url}/discover/{media_type}"

        params = {
            "api_key": self.tmdb_api_key,
            "language": "en-US",
            "page": 1
        }

        # For movies, use primary_release_year
        # For TV shows, use first_air_date_year
        key = "primary_release_year" if media_type == "movie" else "first_air_date_year"
        params[key] = year

        try:
            response = requests.get(discover_url, params=params)
            return response.json().get("results", [])
        except Exception as e:
            print(f"Error fetching by year: {e}")
            return []

    def convert_results_to_dataframe(self, results: List[Dict]) -> pd.DataFrame:
        """Convert API results to a readable DataFrame."""
        search_data = []
        for item in results:
            # Determine title based on media type
            title = item.get('title', item.get('name', 'N/A'))
            
            # Extract release year
            release_date = item.get('release_date') or item.get('first_air_date')
            release_year = int(release_date.split('-')[0]) if release_date else None
            
            search_data.append({
                'title': title,
                'release_year': release_year,
                'overview': item.get('overview', 'No overview'),
                'popularity': item.get('popularity', 0)
            })
        
        return pd.DataFrame(search_data)

class MediaSearchCLI:
    def __init__(self, media_searcher):
        """
        Initialize the CLI with the media search tool
        :param media_searcher: AdvancedMediaSearch instance
        """
        self.searcher = media_searcher
        self.run()

    def print_header(self):
        """Print a decorative header for the application"""
        print("\n" + "="*50)
        print("🎬 Advanced Media Search Tool 🍿".center(50))
        print("="*50)

    def get_user_choice(self) -> int:
        """
        Display menu and get user's choice
        :return: User's menu selection
        """
        print("\nChoose Search Method:")
        print("1. Search by Title")
        print("2. Search by Genre")
        print("3. Search by Year")
        print("4. Advanced Search (Multiple Filters)")
        print("5. Exit")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (1-5): "))
                if 1 <= choice <= 5:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")

    def search_by_title(self):
        """Search media by title"""
        query = input("Enter title to search: ")
        media_type = input("Enter media type (movie/tv, default=movie): ") or "movie"
        
        try:
            results = self.searcher.advanced_search(query, media_type)
            self.display_results(results)
        except Exception as e:
            print(f"Error in search: {e}")

    def search_by_genre(self):
        """Search media by genre"""
        genre = input("Enter genre (e.g., Science Fiction): ")
        media_type = input("Enter media type (movie/tv, default=movie): ") or "movie"
        year = input("Enter release year (optional, press enter to skip): ")
        
        try:
            year = int(year) if year else None
            results = self.searcher.advanced_search(
                media_type=media_type, 
                filters={'genre': genre, 'release_year': year}
            )
            self.display_results(results)
        except Exception as e:
            print(f"Error in search: {e}")

    def advanced_search(self):
        """Perform advanced search with multiple filters"""
        filters: Dict[str, Any] = {}
        
        query = input("Enter search query (optional): ")
        media_type = input("Enter media type (movie/tv, default=movie): ") or "movie"
        
        # Optional genre filter
        genre_filter = input("Enter genre filter (optional): ")
        if genre_filter:
            filters['genre'] = genre_filter
        
        # Optional year filter
        year_filter = input("Enter release year filter (optional): ")
        if year_filter:
            try:
                filters['release_year'] = int(year_filter)
            except ValueError:
                print("Invalid year. Skipping year filter.")
        
        try:
            results = self.searcher.advanced_search(
                query=query, 
                media_type=media_type, 
                filters=filters
            )
            self.display_results(results)
        except Exception as e:
            print(f"Error in advanced search: {e}")

    def display_results(self, results: pd.DataFrame):
        """
        Display search results with pagination
        :param results: DataFrame of search results
        """
        if results.empty:
            print("\n🚫 No results found.")
            return

        # Pagination
        page_size = 5
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size

        current_page = 1
        while True:
            print(f"\n--- Results Page {current_page}/{total_pages} ---")
            
            start_idx = (current_page - 1) * page_size
            end_idx = start_idx + page_size
            page_results = results.iloc[start_idx:end_idx]

            # Print results for current page
            for _, row in page_results.iterrows():
                print("\n" + "-"*50)
                print(f"Title: {row['title']}")
                print(f"Release Year: {row['release_year']}")
                print(f"Overview: {row['overview']}")
                print(f"Popularity: {row['popularity']}")
                print("-"*50)

            # Navigation options
            print("\nNavigation:")
            if current_page > 1:
                print("P - Previous Page", end=" | ")
            if current_page < total_pages:
                print("N - Next Page", end=" | ")
            print("B - Back to Main Menu")

            nav = input("\nChoose an action: ").upper()
            if nav == 'N' and current_page < total_pages:
                current_page += 1
            elif nav == 'P' and current_page > 1:
                current_page -= 1
            elif nav == 'B':
                break
            else:
                print("Invalid navigation choice.")

    def run(self):
        """Main application loop"""
        while True:
            self.print_header()
            
            choice = self.get_user_choice()
            
            if choice == 1:
                self.search_by_title()
            elif choice == 2:
                self.search_by_genre()
            elif choice == 3:
                year = input("Enter release year: ")
                try:
                    results = self.searcher.advanced_search(
                        filters={'release_year': int(year)}
                    )
                    self.display_results(results)
                except Exception as e:
                    print(f"Error in search: {e}")
            elif choice == 4:
                self.advanced_search()
            elif choice == 5:
                print("\nThank you for using Media Search Tool. Goodbye! 👋")
                sys.exit(0)
            
            input("\nPress Enter to continue...")

def main():
    load_dotenv()
    media_searcher = AdvancedMediaSearch()
    MediaSearchCLI(media_searcher)

if __name__ == "__main__":
    main()