import json
import requests
import os
from load_local_api_keys import load_local_api_keys

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:10809'

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    bearer_token = load_local_api_keys("twitter_bearer_token")
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

async def twitter_spider(keyword="", nums=5, params_format=False):
    """
    爬取Twitter上的推文内容
    keyword: 搜索关键词
    nums: 搜索推文数目
    """
    if params_format:
        return ['keyword', 'nums']
        
    try:
        # 创建Twitter API客户端
        search_url = "https://api.twitter.com/2/tweets/search/recent"
        params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev','tweet.fields': 'author_id'}
        response = requests.get(search_url, auth=bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return json.dumps(response.json(), indent=4, sort_keys=True)

    except Exception as e:
        raise Exception(f"爬取Twitter内容失败: {str(e)}")
    

if __name__ == '__main__':
    import asyncio
    keyword = "Python"
    nums = 5
    res = asyncio.run(twitter_spider(keyword, nums))
    print(res)