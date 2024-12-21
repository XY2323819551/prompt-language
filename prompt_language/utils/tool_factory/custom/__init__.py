from .wechatmp_spider import wechatmp_spider
from .paper_with_code import paper_with_code_search
from .send_email import send_email

other_tools = {
    "wechatmp_spider":{
        "object":wechatmp_spider,
        "describe":"微信公众号内容搜索器，需要参数{'keyword':搜索的关键词, 'nums':搜索文章数目}",
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