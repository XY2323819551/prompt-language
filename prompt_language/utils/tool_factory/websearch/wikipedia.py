import aiohttp
from bs4 import BeautifulSoup

# 代理配置
PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

async def wikipedia_search(query: str) -> str:
    search_url = "https://zh.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1,
        "srlimit": 1
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            search_url, 
            params=search_params,
            proxy=PROXIES['http'],
            headers=HEADERS,
            timeout=30
        ) as response:
            data = await response.json()
    
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
            
            async with session.get(
                content_url, 
                params=content_params,
                proxy=PROXIES['http'],
                headers=HEADERS,
                timeout=30
            ) as response:
                data = await response.json()
                
                html = data["parse"]["text"]["*"]
                soup = BeautifulSoup(html, "html.parser")
                
                for tag in soup(["script", "style", "meta", "link"]):
                    tag.decompose()
                    
                text = soup.get_text(separator="\n", strip=True)
                return text

if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await wikipedia_search("openai")
        print(result)
    
    asyncio.run(test())
