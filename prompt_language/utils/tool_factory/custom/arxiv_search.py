import arxiv
import os
import requests
import PyPDF2
from io import BytesIO

async def extract_pdf_content(pdf_url: str) -> str:
    response = requests.get(pdf_url)
    pdf_file = BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

async def arxiv_search(keyword="", nums=2):
    ## 下载到本地
    # root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    # download_dir = os.path.join(root_dir, "assets", "arxiv")
    # os.makedirs(download_dir, exist_ok=True)
    
    client = arxiv.Client()
    search = arxiv.Search(
        query = keyword,
        max_results = nums,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )
    results = []
    for res in client.results(search):
        # down_load_path = res.download_pdf(download_dir)  # 下载到本地
        content = await extract_pdf_content(res.pdf_url)
        results.append({
            "title": res.title,
            "authors": res.authors,
            "published": res.published,
            "abstract": res.summary,
            "content": content
        })
    return results

if __name__ == "__main__":
    import asyncio
    
    async def test():
        results = await arxiv_search("LLM", nums=1)
        
        for idx, paper in enumerate(results, 1):
            print(f"\n=== 论文 {idx} ===")
            print(f"标题: {paper['title']}")
            print(f"作者: {paper['authors']}")
            print(f"发布时间: {paper['published']}")
            print(f"摘要: {paper['abstract']}")
            print(f"内容预览: {paper['content'][:500]}...")
            print("-" * 50)
    
    asyncio.run(test())

