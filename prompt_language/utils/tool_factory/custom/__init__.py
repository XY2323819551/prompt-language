from .dir_reader import dir_reader
from .wechatmp_spider import wechatmp_spider
from .save_to_local import save_to_local
from .paper_with_code import paper_with_code_search
from .send_email import send_email

other_tools = {
    "wechatmp_spider":{
        "object":wechatmp_spider,
        "describe":"微信公众号内容搜索器，需要参数{'keyword':搜索的关键词, 'nums':搜索文章数目}",
    },
    "dir_reader":{
        "object":dir_reader,
        "describe":"读取一个文件夹下的全部文件的内容，需要参数{'dirs':待读取的文件夹路径，格式为[dir1, dir22, ...]}",
    },
    "save_to_local":{
    "object":save_to_local,
    "describe":"将文本保存至本地，需要参数{'contents':需要保存的内容,'output_path':输出路径}",
    },
    "paper_with_code_search":{
        "object":paper_with_code_search,
        "describe":"读取paper with code 网站最新的论文，需要参数{'nums':需要读取的论文数目}",
    },
    "send_email": {
        "object":send_email,
        "describe":"发送邮件，需要参数{'subject':邮件主题，'content':邮件内容，'to':收件人邮箱地址}",
    }
}

__all__ = other_tools