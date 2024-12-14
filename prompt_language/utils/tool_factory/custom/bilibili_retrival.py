from bilibili_api import search, video, sync
import asyncio
import json
import os

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:80'
os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:80'

async def bilibili_retrival(keyword="", nums=5, params_format=False):
    """
    爬取B站视频字幕
    keyword: 搜索关键词
    nums: 搜索视频数目
    """
    if params_format:
        return ['keyword', 'nums']
        
    try:
        # 搜索视频
        resp = await search.search_by_type(keyword, search_type=search.SearchObjectType.VIDEO, page=1)
        results = []
        # 获取前nums个视频
        for item in resp['result'][:nums]:
            video_id = str(item['bvid'])
            v = video.Video(bvid=video_id)
            
            # 获取字幕
            breakpoint()
            subtitle_list = await v.get_subtitle(item['id'])
            
            if subtitle_list:
                # 提取第一个字幕内容
                subtitle_url = subtitle_list[0]['subtitle_url']
                subtitle_content = await v.get_subtitle_content(subtitle_url)
                
                results.append({
                    'title': item['title'],
                    'subtitle': subtitle_content['body']
                })
                
        return json.dumps(results, ensure_ascii=False)
        
    except Exception as e:
        raise Exception(f"爬取B站视频字幕失败: {str(e)}")
    

if __name__ == '__main__':
    keyword = '李飞飞空间智能'
    nums = 5
    result = asyncio.run(bilibili_retrival(keyword, nums))
    print(result)