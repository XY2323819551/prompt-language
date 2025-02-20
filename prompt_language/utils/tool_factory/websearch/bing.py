import aiohttp
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import asyncio

# 加载.env文件中的环境变量
load_dotenv()

def _check_credentials():
    """检查必要的环境变量是否设置"""
    subscription_key = os.getenv("BING_SUBSCRIPTION_KEY")
    custom_config_id = os.getenv("BING_CUSTOM_CONFIG_ID")
    if not subscription_key:
        raise ValueError("BING_SUBSCRIPTION_KEY 环境变量未设置。请在.env文件中设置此变量。")
    if not custom_config_id:
        raise ValueError("BING_CUSTOM_CONFIG_ID 环境变量未设置。请在.env文件中设置此变量。")
    
    return subscription_key, custom_config_id

async def _fetch_full_content(session: aiohttp.ClientSession, url: str) -> str:
    """内部函数：获取网页完整内容"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 移除不需要的标签
                for tag in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
                    tag.decompose()
                
                # 获取正文内容
                text = soup.get_text(separator='\n', strip=True)
                
                # 清理空行
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return '\n'.join(lines)
            return ""
    except:
        return ""

async def _raw_bing_search(query: str, limit: int = 5) -> Dict[str, Any]:
    """内部函数：调用Bing API进行搜索"""
    try:
        subscription_key, custom_config_id = _check_credentials()
        
        base_url = "https://api.bing.microsoft.com/v7.0/custom/search"
        
        params = {
            "q": query,
            "customconfig": custom_config_id,
            "count": limit
        }
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    if "webPages" in data:
                        for page in data["webPages"]["value"]:
                            result = {
                                "title": page.get("name", ""),
                                "url": page.get("url", ""),
                                "snippet": page.get("snippet", "")
                            }
                            # 获取完整正文
                            full_text = await _fetch_full_content(session, result["url"])
                            result["full_text"] = full_text
                            results.append(result)
                    
                    return results
                else:
                    error_text = await response.text()
                    print(f"Bing搜索API错误: HTTP {response.status}")
                    print(f"错误详情: {error_text}")
                    return []
    except Exception as e:
        print(f"Bing搜索发生错误: {str(e)}")
        return []

async def bing_search(query: str) -> List[str]:
    """
    使用Bing搜索并返回格式化的结果列表
    
    Args:
        query: 搜索查询词
        limit: 最大返回结果数,默认10
        
    Returns:
        List[str]: 搜索结果列表，每个元素是格式化的字符串
    """
    results = await _raw_bing_search(query)
    formatted_results = []
    
    for result in results:
        # 格式化每条搜索结果
        formatted_result = f"""标题: {result['title']}
链接: {result['url']}
摘要: {result['snippet']}
全文: {result['full_text']}"""
        formatted_results.append(formatted_result)
    return formatted_results




# Test case
async def test_bing():
    query = "哪吒2的票房啥情况了？"
    results = await bing_search(query)
    
    print(f"\n=== Bing搜索结果 ===")
    for idx, result in enumerate(results, 1):
        print(f"\n--- 结果 {idx} ---")
        print(result)
        print("-" * 50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bing()) 