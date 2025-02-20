from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from lxml import etree
import os

def load_txt_files(folder_path):
    # 存储所有文本内容
    all_content = []
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为txt文件
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            try:
                # 使用 with 语句安全地打开和读取文件
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    all_content.append(content)
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {str(e)}")
    
    # 将所有内容合并为一个字符串，使用换行符分隔
    return '\n'.join(all_content)
class WeixinCrawler:
    def __init__(self, output_dir, nums):
        self.res_list = []
        self.output_dir = output_dir
        self.nums = nums

    def search(self, input_text):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get("https://weixin.sogou.com/")
        time.sleep(1)
        search_input = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/div[2]/div[2]/form/div/span[1]/input[2]")))
        search_input.send_keys(input_text)
        time.sleep(2)
        search_button = self.driver.find_element(By.XPATH,
            "/html/body/div/div[2]/div[2]/div[2]/form/div/span[2]/input")
        search_button.click()
        time.sleep(3)

    def extract_content(self):
        current_count = 0  # 当前已爬取的文章数量
        while current_count < self.nums:
            # 获取当前页面的HTML
            page = etree.HTML(self.driver.page_source)
            # 获取当前页的文章数量
            articles = page.xpath('/html/body/div[2]/div[1]/div[3]/ul/li')
            for i in range(len(articles)):
                if current_count >= self.nums:
                    break  # 如果已经爬取足够数量的文章，则退出

                # 提取基本信息
                url = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a/@href')
                if len(url) > 0:
                    url = url[0]
                else:
                    url = []

                title = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a/text()')
                if len(title) > 0:
                    title = title[0]
                else:
                    title = ""

                time_str = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/div/span[2]/text()')
                if len(time_str) > 0:
                    time_str = time_str[0]
                else:
                    time_str = ""

                abstract = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/p/text()')
                if len(abstract) > 0:
                    abstract = abstract[0]
                else:
                    abstract = ""

                user_id = page.xpath(f'/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/div/span[1]/text()')
                if len(user_id) > 0:
                    user_id = user_id[0]
                else:
                    user_id = ""

                title = title.replace('\\', ' ').replace('/', ' ')[:15]

                # 点击链接打开新页面
                article_link = self.driver.find_element(By.XPATH,
                    f"/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a")
                article_link.click()
                time.sleep(2)

                # 切换到新窗口
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(2)

                # 提取正文内容
                try:
                    content_element = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]")))
                    content = content_element.text
                except:
                    content = ""

                # 保存结果
                result = {
                    'url': url,
                    'title': title,
                    'time': time_str,
                    'abstract': abstract,
                    'user_id': user_id,
                    'content': content
                }
                self.res_list.append(result)
                self.save_single_result(result)
                current_count += 1

                # 关闭当前窗口，切回主窗口
                self.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(self.driver.window_handles[0])

            # 如果当前页的文章数量不足，点击下一页
            if current_count < self.nums:
                try:
                    next_button = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div[1]/div[3]/div/a[text()='下一页']")))
                    next_button.click()
                    time.sleep(3)  # 等待下一页加载
                except:
                    print("没有更多页面了")
                    break
            else:
                break

    def save_single_result(self, result):
        # 创建输出目录
        output_dir = os.path.join(self.output_dir, self.search_keyword)
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存单个结果到文件
        file_path = os.path.join(output_dir, f"{result['user_id']}.txt")
        # print("file_path:", file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            for key, value in result.items():
                f.write(f"{key}: {value}\n")
        # print(f"成功保存文件至{file_path}")

    def run(self, input_text):
        try:
            self.search_keyword = input_text  # 保存搜索关键词
            self.search(input_text)
            self.extract_content()
        finally:
            self.driver.quit()

async def wechatmp_spider(keyword="", nums=3, params_format=False):
    if params_format:
        return ['keywords', 'nums']
    
    # return [f'/Users/liubaoyang/Documents/YoungL/logs/orca/output/wechatmp/{keyword}']

    all_path = []
    output_dir = 'article'
    crawler = WeixinCrawler(output_dir, nums)
    crawler.run(keyword)
    res_dir = os.path.join(output_dir, keyword)
    all_path.append(res_dir)
    return all_path

async def wechatmp_spider_keywords(keywords="", nums=3, params_format=False):
    if params_format:
        return ['keywords', 'nums']
    all_path = []
    output_dir = 'article'
    crawler = WeixinCrawler(output_dir, nums)
    for keyword in keywords:
        crawler.run(keyword)
        res_dir = os.path.join(output_dir, keyword)
        all_path.append(res_dir)
    return all_path
    

def ut(keywords=[], nums=100, params_format=False):
    if params_format:
        return ['keywords']
    all_path = []
    output_dir = 'article'
    for keyword in keywords:
        crawler = WeixinCrawler(output_dir, nums)
        crawler.run(keyword)
        res_dir = os.path.join(output_dir, keyword)
        print(f"关键词“{keyword}”的搜索结果保存在：{res_dir}目录下。")
        all_path.append(res_dir)
    return all_path


def summary(query):
    res = ut(keywords=[query], nums=5, params_format=False)
    content = load_txt_files(res[0])
    return content[:30000]
print(summary("python"))
    


"""
"wechatmp_spider":{
    "object":wechatmp_spider,
    "describe":"微信公众号内容搜索器，需要参数{'keywords':搜索的关键词列表，格式为[keyword1, keyword2, ...]}",
}
"""
