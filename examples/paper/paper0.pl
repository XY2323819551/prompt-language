
@paper_with_code_search(nums=5) >> papers
@arxiv_search(keyword="agentic") >> papers

FOR $paper in $papers:
    你的任务是为我推荐阅读论文，我的研究方向是【大语言模型和agent】。
    请你识别论文列表中和我的研究方向相关的文章，输出文章的index即可 >> formatted_papers
END

FOR $paper in $papers:
    请根据文章的标题和文章的摘要，给出一段中文总结, 并将你的中文总结，以键值对的形式添加到原有的结构中，键值可以叫做summary_zh，其他字段保持不变。
    论文信息如下：
    $paper

    注意结构信息非常重要，严格按照结构要求输出 >> formatted_papers
END





