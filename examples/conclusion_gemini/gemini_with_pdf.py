import os
import httpx
import base64
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

def init_gemini(model_name):
    root_dir = Path(__file__).resolve().parent.parent.parent
    env_path = root_dir / '.env'
    load_dotenv(dotenv_path=env_path)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel(model_name)

def fetch_online_pdf(url):
    proxies = {"http://": "http://127.0.0.1:7890", "https://": "http://127.0.0.1:7890"}
    doc_data = base64.standard_b64encode(httpx.get(url, proxies=proxies).content).decode("utf-8")
    return {'mime_type': 'application/pdf', 'data': doc_data}

def read_local_pdf(file_path):
    with open(file_path, "rb") as doc_file:
        doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")
    return {'mime_type': 'application/pdf', 'data': doc_data}

def summarize_pdf(model, pdf_data, prompt="Summarize this document, please: Answer in chinese."):
    breakpoint()
    response = model.generate_content([pdf_data, prompt])
    return response.text

if __name__ == "__main__":
    model_name = "gemini-2.0-flash-exp"
    model = init_gemini(model_name)
    
    # 在线PDF示例
    # url = "https://arxiv.org/pdf/2107.07430"
    # pdf_data = fetch_online_pdf(url)
    # print(summarize_pdf(model, pdf_data))
    
    # 本地PDF示例
    file_path = "/Users/zhangxiaoyu/Downloads/test.pdf"
    pdf_data = read_local_pdf(file_path)
    print(summarize_pdf(model, pdf_data))
