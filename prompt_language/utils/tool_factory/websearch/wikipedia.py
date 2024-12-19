import requests
from bs4 import BeautifulSoup

def wikipedia_search(query: str) -> str:
    search_url = "https://zh.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1,
        "srlimit": 1
    }
    
    response = requests.get(search_url, params=search_params)
    data = response.json()
    
    if not data.get("query", {}).get("search"):
        return ""
        
    title = data["query"]["search"][0]["title"]
    
    content_url = "https://zh.wikipedia.org/w/api.php"
    content_params = {
        "action": "parse",
        "format": "json",
        "page": title,
        "prop": "text",
        "utf8": 1
    }
    
    response = requests.get(content_url, params=content_params)
    data = response.json()
    
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
    
    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()
        
    text = soup.get_text(separator="\n", strip=True)
    return text

if __name__ == "__main__":
    result = wikipedia_search("哥白尼")
    print(result)
