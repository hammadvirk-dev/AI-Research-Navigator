```python
import os
import time
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from googlesearch import search
import google.generativeai as genai

# Configuration - Ensure you set your API Key in your environment variables
# export GEMINI_API_KEY='your-key-here'
API_KEY = os.getenv("GEMINI_API_KEY", "")

class AIResearchNavigator:
    """
    An AI-powered tool that automates deep research by fetching web results,
    extracting content, and synthesizing it using the Gemini API.
    """

    def __init__(self, api_key: str):
        if not api_key:
            print("Warning: GEMINI_API_KEY not found. Please set it to use AI features.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    def fetch_search_results(self, query: str, num_results: int = 5) -> List[Dict]:
        """Fetches top search results and attempts to scrape snippets/text."""
        print(f"🔍 Searching for: {query}...")
        results = []
        try:
            # Using googlesearch-python to get URLs
            urls = list(search(query, num_results=num_results))
            
            for url in urls:
                try:
                    response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # Extract main text content (paragraphs)
                        paragraphs = soup.find_all('p')
                        text = " ".join([p.get_text() for p in paragraphs[:5]]) # Get first 5 paragraphs
                        results.append({"url": url, "content": text})
                except Exception as e:
                    print(f"Skipping {url}: {e}")
        except Exception as e:
            print(f"Search error: {e}")
        
        return results

    def synthesize_research(self, topic: str, raw_data: List[Dict]) -> str:
        """Uses Gemini API to synthesize the gathered data into a report."""
        print("🤖 Synthesizing information...")
        
        context_str = "\n\n".join([f"Source: {d['url']}\nContent: {d['content']}" for d in raw_data])
        
        system_prompt = (
            "You are an AI Research Scientist. Create a structured Research Report in Markdown format. "
            "Synthesize the provided information, remove duplicates, highlight conflicting views, "
            "and provide clear citations for all facts."
        )
        
        user_prompt = f"Research Topic: {topic}\n\nGathered Context:\n{context_str}"
        
        # Exponential backoff for API calls
        max_retries = 5
        for i in range(max_retries):
            try:
                response = self.model.generate_content(
                    contents=[{"parts": [{"text": user_prompt}]}],
                    system_instruction={"parts": [{"text": system_prompt}]}
                )
                return response.text
            except Exception as e:
                wait_time = 2 ** i
                print(f"API busy, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        return "Failed to synthesize report after multiple attempts."

    def run(self, topic: str):
        """Execution flow: Search -> Scrape -> AI Synthesis -> Save."""
        start_time = time.time()
        
        raw_data = self.fetch_search_results(topic)
        if not raw_data:
            print("No data found to synthesize.")
            return

        report = self.synthesize_research(topic, raw_data)
        
        filename = f"research_report_{int(time.time())}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
            
        end_time = time.time()
        print(f"\n✅ Research Complete! Report saved to: {filename}")
        print(f"⏱️ Total time: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    navigator = AIResearchNavigator(API_KEY)
    user_topic = input("Enter your Research Topic or Question: ")
    navigator.run(user_topic)

```
  
