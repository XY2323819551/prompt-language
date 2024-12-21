@arxiv_search(keyword="agentic") >> papers

FOR $paper in $papers:
    你是一个论文阅读小助手，可以根据论文的标题、摘要以及详细的论文内容，对论文进行总结。
    ===
    论文标题：${paper.title}
    ===
    论文摘要：${paper.abstract}
    ===
    论文内容：${paper.content}
    ===

    请你根据论文的标题、摘要以及论文内容，给出总结。
    总结内容必须包含以下6点：
    （1）基本信息，包括论文标题、作者、发表时间等；
    （2）研究背景，简要介绍；
    （3）研究问题，重点介绍；
    （4）研究方法，重点介绍；
    （5）实验结果，简要介绍；
    （6）最终结论，简要介绍；

    你需要使用markdown格式输出总结，并添加一些emoji，让总结更加生动有趣。 >> paper_summary

    @save2local(content=${paper_summary[-1]}, filename="papers/${paper.title}.md") -> status
END

