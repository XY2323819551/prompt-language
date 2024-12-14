import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import json

from load_local_api_keys import load_local_api_keys

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:10809'

async def youtube_retrival(keyword="", nums=1, params_format=False):
    """
    爬取YouTube视频字幕和评论
    keyword: 搜索关键词
    nums: 搜索视频数目
    """
    if params_format:
        return ['keyword', 'nums']
        
    try:
        # YouTube API密钥 - 需要替换成你自己的API密钥
        YOUTUBE_API_KEY = load_local_api_keys('google_youtube_api')
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # 搜索视频
        search_response = youtube.search().list(
            q=keyword,
            part='id,snippet',
            maxResults=nums
        ).execute()
        
        results = []
        
        for item in search_response['items']:
            if item['id'].get('videoId'):
                video_id = item['id']['videoId']
                
                # 获取字幕
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    subtitle_text = " ".join([t['text'] for t in transcript])
                except:
                    subtitle_text = "无字幕"
                    
                # 获取评论
                try:
                    comments = []
                    comments_response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=10
                    ).execute()
                    
                    for comment in comments_response['items']:
                        comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        comments.append(comment_text)
                except:
                    comments = ["无评论"]
                
                results.append({
                    'title': item['snippet']['title'],
                    'video_id': video_id, 
                    'subtitle': subtitle_text,
                    'comments': comments
                })
                
        return json.dumps(results, ensure_ascii=False)
        
    except Exception as e:
        raise Exception(f"爬取YouTube视频失败: {str(e)}")
    
if __name__ == "__main__":
    keyword = "Python"
    nums = 5

    res = asyncio.run(youtube_retrival(keyword, nums, params_format=False))
    print(res)