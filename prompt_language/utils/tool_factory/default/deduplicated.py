import ast
import re
from typing import List
from difflib import SequenceMatcher
import jieba
from collections import Counter
import json
import asyncio

async def clean_text(text: str) -> str:
    """清理单个文本中的噪声"""
    text = re.sub(r'[\n\t\r]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    sentences = re.split(r'[。！？.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    seen_sentences = set()
    cleaned_sentences = []
    for sentence in sentences:
        if sentence not in seen_sentences:
            seen_sentences.add(sentence)
            cleaned_sentences.append(sentence)
    
    return '。'.join(cleaned_sentences) + '。'

async def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度"""
    words1 = list(jieba.cut(text1))
    words2 = list(jieba.cut(text2))
    
    counter1 = Counter(words1)
    counter2 = Counter(words2)
    
    all_words = set(counter1.keys()) | set(counter2.keys())
    
    dot_product = sum(counter1.get(word, 0) * counter2.get(word, 0) for word in all_words)
    
    norm1 = sum(count * count for count in counter1.values()) ** 0.5
    norm2 = sum(count * count for count in counter2.values()) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)

async def remove_similar_texts(texts: List[str], similarity_threshold: float = 0.5) -> List[str]:
    """移除相似度高于阈值的文本"""
    if not texts:
        return []
        
    result = [texts[0]]
    
    for text in texts[1:]:
        is_similar = False
        for existing_text in result:
            similarity = await calculate_similarity(text, existing_text)
            if similarity > similarity_threshold:
                is_similar = True
                break
        
        if not is_similar:
            result.append(text)
    
    return result

async def deduplicate(items:List[str]=[""]) -> List[str]:
    """主函数：处理字符串列表并去重"""
    result = []
    
    for item in items:
        if item.startswith('[') and item.endswith(']'):
            try:
                list_items = ast.literal_eval(item)
                result.extend(list_items)
            except:
                result.append(item)
        else:
            result.append(item)
    
    # 使用asyncio.gather并行处理文本清理
    cleaned_texts = await asyncio.gather(*[clean_text(text) for text in result])
    cleaned_texts = [text for text in cleaned_texts if text.strip()]
    
    # 移除相似文本
    final_texts = await remove_similar_texts(cleaned_texts)
    return final_texts

if __name__ == "__main__":
    async def test():
        test_data = [
            "这是一个测试。这是一个测试。今天天气不错。",
            '["重复的内容。重复的内容。", "这是测试内容。这是测试内容。"]',
            "今天的天气真的很不错，适合出门。今天天气不错，很适合出门。",
            '["完全不同的内容。", "这是测试内容。这是测试内容。"]',
            "这是独特的内容。"
        ]
        
        result = await deduplicate(test_data)
        print("原始数据:", test_data)
        print("\n处理后:", result)
    
    asyncio.run(test())
