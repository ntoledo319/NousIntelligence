import requests
from bs4 import BeautifulSoup
import logging

def scrape_aa_reflection():
    """Scrape the AA Daily Reflection from the official website"""
    try:
        url = "https://www.aa.org/daily-reflection"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.select_one(".article-content")
        
        if not article:
            return "Could not find the daily reflection on the AA website."
            
        # Extract the title, date, and content
        title_elem = article.select_one("h2")
        date_elem = article.select_one(".date")
        
        title = title_elem.get_text(strip=True) if title_elem else "Daily Reflection"
        date = date_elem.get_text(strip=True) if date_elem else ""
        
        # Remove title and date elements to get just the content
        if title_elem:
            title_elem.decompose()
        if date_elem:
            date_elem.decompose()
            
        content = article.get_text("\n").strip()
        
        return f"📖 {title}\n{date}\n\n{content}"
    except Exception as e:
        logging.error(f"Error scraping AA reflection: {str(e)}")
        return f"Error retrieving the AA Daily Reflection: {str(e)}"
