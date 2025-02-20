import os
import aiohttp
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import asyncio

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# 代理配置
PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 完整的请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

async def _fetch_full_content(url: str) -> str:
    """获取网页全文内容"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=HEADERS,
                proxy=PROXIES['http'],
                ssl=False,
                timeout=30
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for tag in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
                        tag.decompose()
                    
                    text = soup.get_text(separator='\n', strip=True)
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    return '\n'.join(lines)
    except Exception as e:
        print(f"Error fetching content: {str(e)}")
    return ""

async def _google_search_async(query: str, num_results: int = 3) -> dict:
    """异步方式调用Google搜索API"""
    url = f'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': num_results
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            params=params,
            headers=HEADERS,
            proxy=PROXIES['http'],
            ssl=False,
            timeout=30
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f'Error: {response.status} - {error_text}')

async def google_search(query: str) -> List[str]:
    """主函数：执行搜索并获取全文"""
    try:
        raw_results = await _google_search_async(query)
        results = []
        
        if 'items' in raw_results:
            for item in raw_results['items']:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                full_content = await _fetch_full_content(item.get('link', ''))
                results.append(f"""标题: {title}
摘要: {snippet}
全文: {full_content}""")
        
        return results
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

if __name__ == "__main__":
    async def test():
        results = await google_search("李鸿章")
        for idx, result in enumerate(results, 1):
            print(f"\n--- 结果 {idx} ---")
            print(result)
            print("-" * 50)
    
    asyncio.run(test())

