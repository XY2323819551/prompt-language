from typing import List, Union
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

async def article_filter(articles: List[dict] = None, query: str = ""):
    """
    根据查询语句过滤文章列表
    
    Args:
        articles: 文章列表，每篇文章为字典格式，必须包含'content'键
        query: 查询字符串
    
    Returns:
        过滤后的文章列表
    
    Raises:
        Exception: 当输入的文章列表格式无效时
    """
    if not articles or not isinstance(articles, list):
        raise Exception("无效的文章列表")
    
    if not query:
        return articles
        
    # 检查文章格式
    for article in articles:
        if not isinstance(article, dict) or 'content' not in article:
            raise Exception("文章格式错误，必须包含'content'字段")
    
    # 对查询语句分词
    query_words = ' '.join(jieba.cut(query))
    
    # 准备文档列表
    documents = [' '.join(jieba.cut(article['content'])) for article in articles]
    documents.append(query_words)
    
    # 计算TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # 计算相似度
    query_vector = tfidf_matrix[-1]
    similarities = cosine_similarity(query_vector, tfidf_matrix[:-1])[0]
    
    # 过滤文章
    filtered_articles = [
        article for article, similarity in zip(articles, similarities)
        if similarity >= 0.1
    ]
    
    return filtered_articles
