from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from lxml import etree

class WeixinCrawler:
    def __init__(self, ouput_dir, nums):
        # 初始化浏览器驱动

        self.res_list = []
        self.output_dir = ouput_dir
        self.nums = nums

    def search(self, input_text):
        self.driver = webdriver.Chrome()
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 启用无头模式
        # options.add_argument('--disable-gpu')  # 禁用GPU加速
        # options.add_argument('--no-sandbox')  # 在Linux中运行时常用的选项
        # self.driver = webdriver.Chrome(options=options)  # 使用带options的webdriver
        self.wait = WebDriverWait(self.driver, 10)

        # 打开搜索页面
        self.driver.get("https://weixin.sogou.com/")
        time.sleep(1)
        # 定位搜索框并输入内容
        search_input = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/div[2]/div[2]/form/div/span[1]/input[2]")))
        search_input.send_keys(input_text)
        time.sleep(2)
        # 点击搜索按钮
        search_button = self.driver.find_element(By.XPATH, 
            "/html/body/div/div[2]/div[2]/div[2]/form/div/span[2]/input")
        search_button.click()
        
        # 等待搜索结果加载
        time.sleep(3)

    def extract_content(self):
        for i in range(self.nums):
            # 获取当前页面的HTML
            page = etree.HTML(self.driver.page_source)
            
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
            # 点击链接打开新页面s
            article_link = self.driver.find_element(By.XPATH, 
                f"/html/body/div[2]/div[1]/div[3]/ul/li[{i+1}]/div[2]/h3/a")
            article_link.click()
            time.sleep(2)
            # 切换到新窗口
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            # 等待内容加载
            try:
                content_element = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]")))
                content = content_element.text
            except:
                continue
            time.sleep(2)
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
            # 关闭当前窗口，切回主窗口
            self.driver.close()
            time.sleep(2)
            self.driver.switch_to.window(self.driver.window_handles[0])

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
    all_path = []
    output_dir = './output'
    crawler = WeixinCrawler(output_dir, nums)
    crawler.run(keyword)
    res_dir = os.path.join(output_dir, keyword)
    all_path.append(res_dir)
    return all_path

async def wechatmp_spider_keywords(keywords="", nums=3, params_format=False):
    if params_format:
        return ['keywords', 'nums']
    all_path = []
    output_dir = './output'
    crawler = WeixinCrawler(output_dir, nums)
    for keyword in keywords:
        crawler.run(keyword)
        res_dir = os.path.join(output_dir, keyword)
        all_path.append(res_dir)
    return all_path
    

def ut(keywords=[], nums=3, params_format=False):
    if params_format:
        return ['keywords']
    all_path = []
    output_dir = './output'
    for keyword in keywords:
        crawler = WeixinCrawler(output_dir, nums)
        crawler.run(keyword)
        res_dir = os.path.join(output_dir, keyword)
        print(f"关键词“{keyword}”的搜索结果保存在：{res_dir}目录下。")
        all_path.append(res_dir)
    return all_path


if __name__ == '__main__':
    res = ut(keywords=['openai'], nums=3, params_format=False)
    print(res)


"""
"wechatmp_spider":{
    "object":wechatmp_spider,
    "describe":"微信公众号内容搜索器，需要参数{'keywords':搜索的关键词列表，格式为[keyword1, keyword2, ...]}",
}
"""