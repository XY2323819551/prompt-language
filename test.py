
import requests

# 设置您的API密钥和搜索引擎ID
API_KEY="AIzaSyCZXzc4Mzq68lMPjVv8WCyRDjdq9qGnavI"
CSE_ID="0191900ee6fac46fa"

def google_search(query, num_results=10):
    # 构建请求URL
    url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CSE_ID}&q={query}&num={num_results}'
    
    # 发送GET请求
    response = requests.get(url)
    
    # 检查响应状态
    if response.status_code == 200:
        return response.json()  # 返回JSON格式的响应
    else:
        raise Exception(f'Error: {response.status_code} - {response.text}')

# 示例：搜索"Python编程"
results = google_search("Python编程")
for item in results.get('items', []):
    print(f'Title: {item["title"]}')
    print(f'Link: {item["link"]}')
    print(f'Snippet: {item["snippet"]}\n')

