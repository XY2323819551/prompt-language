# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import random
import os
import platform

def setup_driver():
    """设置Chrome浏览器"""
    print("正在初始化Chrome浏览器...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # 添加代理设置
    proxy = "127.0.0.1:7890"
    print(f"设置代理: {proxy}")
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    
    # 设置UA
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 添加其他设置
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 根据操作系统选择驱动路径
    if platform.system() == 'Darwin':  # macOS
        driver_path = '/usr/local/bin/chromedriver'
    else:  # Linux/Windows
        driver_path = 'chromedriver'
    
    print(f"使用ChromeDriver路径: {driver_path}")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置window.navigator.webdriver为false
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    
    print("Chrome浏览器初始化完成")
    return driver

def fetch_openai_url(url, output_path):
    """
    获取OpenAI文章内容
    :param url: 文章URL
    :param output_path: 输出路径（相对于output目录），例如：'gemini/conclusion.md'
    :return: bool
    """
    print(f"\n开始获取文章: {url}")
    
    # 构建完整的输出路径
    full_output_path = os.path.join('output', output_path)
    output_dir = os.path.dirname(full_output_path)
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # 构建调试文件的路径
    debug_dir = os.path.join(output_dir, 'debug')
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)
    
    debug_html = os.path.join(debug_dir, 'debug.html')
    
    try:
        print("Step 1: 启动浏览器")
        driver = setup_driver()
        
        # 添加随机延迟
        delay = random.uniform(2, 4)
        print(f"Step 2: 等待 {delay:.1f} 秒后开始访问...")
        time.sleep(delay)
        
        # 访问页面
        print("Step 3: 正在访问页面...")
        start_time = time.time()
        driver.get(url)
        print(f"页面加载耗时: {time.time() - start_time:.1f} 秒")
        
        # 等待主要内容加载
        print("Step 4: 等待页面内容加载...")
        wait = WebDriverWait(driver, 20)
        main_content = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        print("页面主要内容加载完成")
        
        # 获取页面源码
        print("Step 5: 获取页面源码...")
        page_source = driver.page_source
        
        # 保存原始HTML以便调试
        print("Step 6: 保存原始HTML...")
        with open(debug_html, 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        # 解析内容
        print("Step 7: 解析页面内容...")
        soup = BeautifulSoup(page_source, 'html.parser')
        main_content = soup.find('main')
        
        if main_content:
            print("Step 8: 提取文本内容...")
            text = main_content.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n+', '\n', text)
            
            print(f"Step 9: 保存文章内容到 {full_output_path}...")
            with open(full_output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print("文章保存成功！")
            return text
        else:
            print("错误: 无法找到主要内容")
            return "错误: 无法找到主要内容"
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False
    finally:
        print("Step 10: 清理资源...")
        try:
            driver.quit()
            print("浏览器已关闭")
        except:
            print("警告: 浏览器关闭失败")
        print("任务结束")

# Test code
if __name__ == "__main__":
    url = "https://openai.com/index/deliberative-alignment/"
    output_path = "openai/deliberative-alignment.md"  # 示例输出路径
    
    print("\n" + "="*50)
    print("开始爬取OpenAI文章")
    print("="*50)
    start_time = time.time()
    result = fetch_openai_url(url, output_path)
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"任务{'成功' if result else '失败'}")
    print(f"总耗时: {total_time:.1f} 秒")
    print("="*50)

