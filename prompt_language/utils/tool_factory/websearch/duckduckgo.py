from duckduckgo_search import DDGS
from typing import List, Dict
import aiohttp
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

# 代理配置
PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 更完整的请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def _duckduckgo_search(query: str, max_results: int = 1) -> List[Dict]:
    """文本搜索"""
    with DDGS(proxies=PROXIES, headers=HEADERS) as ddgs:
        # 添加随机延迟
        time.sleep(random.uniform(2, 5))
        try:
            # 使用更保守的参数
            results = ddgs.text(
                query,
                max_results=max_results,
                backend="lite",  # 使用lite后端
                safesearch='off',  # 关闭安全搜索
                timelimit='y'  # 时间限制：过去一年
            )
            return [r for r in results]
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

def search_news(query: str, max_results: int = 5) -> List[Dict]:
    """新闻搜索"""
    with DDGS(proxies=PROXIES, headers=HEADERS) as ddgs:
        time.sleep(random.uniform(2, 5))
        try:
            results = ddgs.news(
                query,
                max_results=max_results,
                backend="lite"
            )
            return [r for r in results]
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

def search_images(query: str, max_results: int = 5) -> List[Dict]:
    """图片搜索"""
    with DDGS(proxies=PROXIES, headers=HEADERS) as ddgs:
        time.sleep(random.uniform(2, 5))
        try:
            results = ddgs.images(
                query,
                max_results=max_results,
                backend="lite"
            )
            return [r for r in results]
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

async def _fetch_full_content(url: str) -> str:
    """获取网页全文内容"""
    if not isinstance(url, str) or not url:
        return ""
    url = "https://zh.wikipedia.org/wiki/尼古拉·哥白尼"
    
    try:
        # 解析并重新构建URL，确保格式正确
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme:
            url = 'http://' + url
        
        # 创建session时配置代理
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

async def duckduckgo_search(query: str) -> List[str]:
    """文本搜索并获取全文内容"""
    search_results = _duckduckgo_search(query)
    results = []
    
    for res in search_results:
        title = res.get('title', '')
        link = res.get('href', '')  
        snippet = res.get('body', '')
        
        # 在获取全文之前添加延迟
        time.sleep(random.uniform(1, 3))
        full_content = await _fetch_full_content(link)
        
        formatted_result = f"""标题: {title}
链接: {link}
摘要: {snippet}
全文: {full_content}"""
        results.append(formatted_result)
    
    return results

if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    
    # # 测试普通搜索
    # print("\n=== 文本搜索测试 ===")
    # results = search_text("哥白尼")  # 减少结果数量
    # pprint(results)
    
    # # 等待一段时间后再进行下一次搜索
    # time.sleep(5)
    
    # 测试带全文的搜索
    async def test_full_content():
        print("\n=== 带全文的搜索测试 ===")
        full_results = await duckduckgo_search("哥白尼")  # 只请求一条结果
        for idx, result in enumerate(full_results, 1):
            print(f"\n--- 结果 {idx} ---")
            print(result)
            print("-" * 50)
    
    asyncio.run(test_full_content())
