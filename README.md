# Movie-Extractor

# Movie and TV Show Information System - Dependencies

## Python Version
Python 3.8+

## Required Libraries
```
requests==2.31.0
python-dotenv==1.0.0
openai==1.3.5
```

## Optional Libraries for Advanced Usage
```
# Data processing and analysis
pandas==2.0.1
numpy==1.24.3

# Web framework (if creating a web interface)
flask==2.3.2
fastapi==0.95.2

# Frontend (if building a web app)
streamlit==1.22.0

# Testing
pytest==7.3.1
```

## API Services (Required)
1. The Movie Database (TMDB)
   - Website: https://www.themoviedb.org/documentation/api
   - Free tier available
   - Provides movie/TV show metadata

2. WatchMode
   - Website: https://api.watchmode.com/
   - Streaming platform information
   - Paid API with limited free tier

3. OpenAI
   - Website: https://openai.com/
   - Used for AI recommendations
   - Requires API key and has usage-based pricing

## Installation Instructions

### 1. Create Virtual Environment
```bash
# Using venv
python3 -m venv movie_info_env
source movie_info_env/bin/activate  # On Windows, use `movie_info_env\Scripts\activate`

# Using conda
conda create -n movie_info python=3.8
conda activate movie_info
```

### 2. Install Dependencies
```bash
# Basic dependencies
pip install -r requirements.txt

# Optional: Install additional libraries
pip install -r requirements-extra.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in your project root:
```
TMDB_API_KEY=your_tmdb_api_key
WATCHMODE_API_KEY=your_watchmode_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

## Deployment Considerations
- Recommended hosting: 
  - Heroku
  - AWS Lambda
  - Google Cloud Run
- Consider containerization with Docker for consistent deployment

## Troubleshooting
- Ensure all API keys are valid
- Check network connectivity
- Verify Python version compatibility
- Monitor API usage and limits
```

### Create Requirements Files
```bash
# requirements.txt
requests==2.31.0
python-dotenv==1.0.0
openai==1.3.5

# requirements-extra.txt
pandas==2.0.1
numpy==1.24.3
flask==2.3.2
streamlit==1.22.0

# requirements-dev.txt
pytest==7.3.1
flake8==6.0.0
black==23.3.0
```

## Contribution Guidelines
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation with significant changes
```