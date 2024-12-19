import requests
from bs4 import BeautifulSoup
from typing import Optional

def wikidata_search(query: str) -> Optional[str]:
    """
    搜索Wikidata并返回页面文本内容
    
    Args:
        query: 搜索关键词
    Returns:
        str: 页面文本内容
    """
    # 第一步：搜索实体获取ID
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'zh',
        'search': query,
        'limit': 1
    }
    
    try:
        response = requests.get(search_url, params=search_params)
        data = response.json()
        
        if not data.get('search'):
            return None
            
        # 获取实体ID
        entity_id = data['search'][0]['id']
        
        # 第二步：直接获取Wikidata页面内容
        
        page_url = f"https://www.wikidata.org/wiki/{entity_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除不需要的元素
        for tag in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
            tag.decompose()
        
        # 获取文本内容
        text = soup.get_text(separator='\n', strip=True)
        return text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # 测试代码
    query = "艾伦图灵"
    content = wikidata_search(query)
    if content:
        print(content[:1000])  # 打印前1000个字符
