
@bing_search(query="从哲学的角度解释：如果一个人长期在光明中，突然处于黑暗世界，他会怎么样？") -> philosophy_result
@bing_search(query="从心理学的角度解释：如果一个人长期在光明中，突然处于黑暗世界，他会怎么样？") -> psychology_result
@bing_search(query="从物理学的角度解释：太阳熄灭，地球会怎么样？") -> physics_result

FOR $item in [$philosophy_result, $psychology_result, $physics_result]:
    根据参考信息，总结出一个最重要的观点！
    参考下信息：
    $item 
    你的开头需要说：从哲学/心理学/物理学的角度来说，xxx 
    回答尽量详细 >> viewpoint
END

你现在有一些不同领域的观点和知识，你需要根据这些知识，写一部短片科幻小说。
领域知识如下：
====
$viewpoint
====

科幻小说的主题为：【如果一个人长期在光明中，突然处于黑暗世界，他会怎么样？】
你需要结合哲学知识、心理学知识、物理学知识，来撰写小说。
小说情节需要跌宕起伏，引人入胜，并且需要有合理的逻辑。-> scific_content

@save2local(content=$scific_content, filename="scific/scific_content.md") -> status
