import os
import requests
import aiohttp
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import asyncio

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

async def _fetch_full_content(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for tag in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
                        tag.decompose()
                    
                    text = soup.get_text(separator='\n', strip=True)
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    return '\n'.join(lines)
    except:
        return ""
    return ""

def _google_search_sync(query: str, num_results: int = 1) -> dict:
    url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}&num={num_results}'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Error: {response.status_code} - {response.text}')

async def google_search(query: str) -> List[str]:
    raw_results = _google_search_sync(query)
    results = []
    
    if 'items' in raw_results:
        for item in raw_results['items']:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            full_content = await _fetch_full_content(item.get('link', ''))
            results.append(f"{title}\n{snippet}\n{full_content}")
    
    return results

if __name__ == "__main__":
    async def test():
        results = await google_search("Python编程", limit=2)
        for idx, result in enumerate(results, 1):
            print(f"\n--- 结果 {idx} ---")
            print(result)
            print("-" * 50)
    
    asyncio.run(test())

