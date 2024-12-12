
@agent(
    type="bambo", 
    task="""
1、请首先搜索最新的10篇论文；
2、然后对这些论文进行分类，类别列表为['LLM','RAG','Agent','多模态','音频','计算机视觉','其它']，分类结果按照{论文标题：类别}的形式输出;
3、对分类后的论文按照类别进行总结，并且给出当前类别有哪些文件，总结结果按照{类别1：类别1多篇论文的总结。类别1的所有参考论文标题。}的形式输出；
4、我的研究方向是['LLM','RAG','Agent','多模态'],请根据我的研究方向，推荐一些相关的论文，推荐结果按照{论文标题：类别、论文链接、摘要的总结}的形式输出；
""", 
    roles = {
        "paper_classification_expert": "论文分类专家",
        "paper_summary_expert": "论文总结专家",
        "paper_recommend_expert": "论文推荐专家",
    },
    tools=["code_execute", "paper_search"]
) -> paper_recommend_process

