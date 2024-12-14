"""
中国证券报(官网:www.cs.com.cn)由新华社主办，聚焦股票、债券、基金等金融市场的新闻与分析。
证券时报(官网:www.stcn.com)专注于证券市场和上市公司动态，提供权威的市场资讯。
财新网(官网:www.caixin.com)以深度报道和调查见长，涵盖宏观经济、金融市场、企业动态等领域。
第一财经(官网:www.yicai.com)提供金融市场动态、经济政策解读，以及全球财经资讯。
新浪财经(官网:finance.sina.com.cn)综合性的财经新闻平台，包含股票、基金、外汇、期货等多个频道。
网易财经(官网:money.163.com)提供实时财经新闻、股票行情分析及行业动态。
和讯财经(官网:www.hexun.com)提供财经新闻、理财服务、市场数据分析等内容。
东方财富网(官网:www.eastmoney.com)专注于证券投资和理财，提供股票行情、基金资讯和市场分析。
凤凰财经(官网:finance.ifeng.com)聚焦宏观经济、金融政策、股市行情等，兼具国际财经新闻。
搜狐财经(官网:business.sohu.com)涵盖财经新闻、投资理财及行业观察，内容广泛。
中国经济网(官网:www.ce.cn)由人民日报社主办，报道国内外经济动态、政策解读。
经济观察网(官网:www.eeo.com.cn)提供财经新闻、企业报道和深度经济分析。
21世纪经济报道(官网:www.21jingji.com)以经济新闻和金融市场为主，报道权威、全面。
人民网财经(官网:finance.people.com.cn)涵盖宏观经济、政策解读和市场动态，官方权威平台。
"""

async def finance_news_search(nums=20, params_format=False):
    if params_format:
        return ['nums']
    all_news = []
    