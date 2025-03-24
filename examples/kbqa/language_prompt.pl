"""
# 图谱schema，可以写一个工具，获取图谱schema，并且根据选择的实体范围来缩小图谱schema本身。
"""

$schema  # 图谱schema
$query  # 用户原始问题
$sub_question_answer

import Agent.zxy-kgrag-recall
import Agent.zxy-doc-recall
import Agent.zxy-nl2ngql-recall


/prompt/你是一个任务规划师，你会根据用户的问题和当前拥有的工具，将用户的复杂问题拆分为尽可能简单的子问题。
你拆分子问题是有依据的，你会根据图谱的kg_schema来对原问题进行拆分，尽可能一个子问题对应一个三元组，通过逐步解决子问题，最终综合得出原始问题的答案；如果原问题不需要拆分，则返回原问题。

用户的问题为：
当前问题为：$query

图谱的kg_schema为：
$kg_schema

输出格式：
严格按照字符串列表的形式返回子问题，你给出的答案中不要返回多余的内容。
例如：["子问题1","子问题2","子问题3"]

Examples:
示例1: xxx所在的组还有谁
分析: 要想知道xxx所在的组还有谁，我们必须先知道xxx在哪个组，然后再查询该组有哪些人。所以应该分为两个查询子问题。先查询xxx在哪个组，再查询该组有哪些人（查询之前需要调用重写工具重写query）

示例2: AnyDATA模型工厂研发部开发、测试和算法分别有多少人
分析：AnyDATA模型工厂研发部有可能是个大部门，所以我们要先知道AnyDATA模型工厂研发部包含了哪些子部门，再知道这些子部门都有谁，最后根据找到的信息回答问题。(回答下一个子问题之前需要根据上下文决定是否调用重写工具）-> sub_questions


$sub_questions.answer -> sub_questions
/for/ $sub_question in $sub_questions:
    /prompt/角色\n你是一个问题重写专家，可以根据历史对话信息，对当前问题的主语和指代进行补充完善，生成一个语义明确、没有指代的问题。\n\n当前问题为：\n【$sub_question】\n\n历史对话信息为：\n【**用户**：根据图谱schema和query，确定问题是否需要拆分成为子问题，如果需要拆分成子问题，则拆分成子问题；如果不需要，则返回原问题。严格按照字符串列表的形式返回子问题，你给出的答案中不要返回多余的内容。**助手**：我给出的子问题列表为：【$sub_questions】。我要依次获取各个子问题的答案。当前子问题解决进度：【$sub_question_answer】\n# 步骤\n步骤1. 如果历史对话信息和当前问题无关，或无法改写，请忽略后续步骤，直接返回：【重写后的问题】{{query}}。\n步骤2. 如果可以改写，则先识别当前问题中的主语和所有的指代，并显示你的答案。\n步骤3. 从历史对话信息中找出步骤2中涉及的主语或指代的具体内容，要忠于原文，不要少任何一个字。显示你的答案\n步骤4. 结合步骤2和步骤3的结果，将你找到的具体的主语或指代替换到当前问题：【$sub_question】中。重写后的问题尽量简短。显示重写后的问题，输出格式为：【重写后的问题】xxx\n\n# 注意事项\n1. 你只需要补充主语和指代信息即可，不要修改问题本身。\n2. 你有足够的时间，请认真思考后回答。\n -> raw_rewrite_query
    /prompt/我给你一段文字，文字中可能包含问题重写的原因和重写后的问题，也可能只包含一个重写后的问题。你需要原封不动的提取出重写后的问题部分，不要返回任何其他多余的解释或者字符。文字内容为：【$raw_rewrite_query】-> rewrite_query
    $rewrite_query.answer -> rewrite_query
    /explore/(tools=["zxy-kgrag-recall","zxy-doc-recall","zxy-nl2ngql-recall"])使用当前query从多个召回源召回相关的信息，然后回答问题。当前query为：【$rewrite_query】。\n你有三个召回工具可以使用，分别是：1. 【zxy-nl2ngql-recall】工具：将自然语言转换为ngql语句，然后从知识图谱中召回相关信息。该工具准确度非常高，只要有答案，基本都是正确的\n2.【zxy-kgrag-recall】工具：从知识图谱中利用retrieval-augmented generation的方式召回相关信息，工具的准确度次于【zxy-nl2ngql-recall】工具\n3. zxy-doc-recall：从文档中召回相关信息，如果前两个工具都没有找到答案或者信息不足，则使用该工具召回信息来增强召回内容。\n\n当你找到足够的信息之后，就可以回答当前问题。回答格式为：针对当前query（$rewrite_query），答案是：xxxx。现在，请开始解决当前问题：【$rewrite_query】。 >> sub_question_answer
/end/

/prompt/用户原始的问题为$query。现在你已经收集到了所有子问题的答案，信息如下：$sub_question_answers。仔细综合已有信息，通过推理准确的给出最终答案。-> final_answer




==============================================================================================
==============================================================================================

import Agent.zxy-kgrag-recall
import Agent.zxy-doc-recall
import Agent.zxy-nl2ngql-recall


/prompt/你是一个任务规划师，你会根据用户的问题和当前拥有的工具，将用户的复杂问题拆分为尽可能简单的子问题。
你拆分子问题是有依据的，你会根据图谱的kg_schema来对原问题进行拆分，尽可能一个子问题对应一个三元组，通过逐步解决子问题，最终综合得出原始问题的答案；如果原问题不需要拆分，则返回原问题。

用户的问题为：
当前问题为：$query

图谱的kg_schema为：
$kg_schema

输出格式：
严格按照字符串列表的形式返回子问题，你给出的答案中不要返回多余的内容。
例如：["子问题1","子问题2","子问题3"]

Examples:
示例1: xxx所在的组还有谁
分析: 要想知道xxx所在的组还有谁，我们必须先知道xxx在哪个组，然后再查询该组有哪些人。所以应该分为两个查询子问题。先查询xxx在哪个组，再查询该组有哪些人（查询之前需要调用重写工具重写query）

示例2: AnyDATA模型工厂研发部开发、测试和算法分别有多少人
分析：AnyDATA模型工厂研发部有可能是个大部门，所以我们要先知道AnyDATA模型工厂研发部包含了哪些子部门，再知道这些子部门都有谁，最后根据找到的信息回答问题。(回答下一个子问题之前需要根据上下文决定是否调用重写工具）-> sub_questions


$sub_questions.answer -> sub_questions
/for/ $sub_question in $sub_questions:
    /prompt/角色\n你是一个问题重写专家，可以根据历史对话信息，对当前问题的主语和指代进行补充完善，生成一个语义明确、没有指代的问题。\n\n当前问题为：\n【$sub_question】\n\n历史对话信息为：\n【**用户**：要回答问题：$query, 需要先回答如下问题：【$sub_questions】。我要依次获取各个子问题的答案。当前子问题解决进度：【$sub_question_answer】\n# 步骤\n步骤1. 如果历史对话信息和当前问题无关，或无法改写，请忽略后续步骤，直接返回：【重写后的问题】$sub_question。\n步骤2. 如果可以改写，则先识别当前问题中的主语和所有的指代，并显示你的答案。\n步骤3. 从历史对话信息中找出步骤2中涉及的主语或指代的具体内容，要忠于原文，不要少任何一个字。显示你的答案\n步骤4. 结合步骤2和步骤3的结果，将你找到的具体的主语或指代替换到当前问题：【$sub_question】中。重写后的问题尽量简短。显示重写后的问题，输出格式为：【重写后的问题】xxx\n\n# 注意事项\n1. 你只需要补充主语和指代信息即可，不要修改问题本身。\n2. 你有足够的时间，请认真思考后回答。\n -> raw_rewrite_query
    /prompt/我给你一段文字，文字中可能包含问题重写的原因和重写后的问题，也可能只包含一个重写后的问题。你需要原封不动的提取出重写后的问题部分，不要返回任何其他多余的解释或者字符。文字内容为：【$raw_rewrite_query】-> rewrite_query
    $raw_rewrite_query.answer -> rewrite_query
    @zxy-nl2ngql-recall(query=$rewrite_query) -> ngql_recall_answer
    @zxy-kgrag-recall(query=$rewrite_query) -> kg_recall_content
    @zxy-doc-recall(query=$rewrite_query) -> doc_recall_content
    /prompt/根据召回内容回答当前用户的问题。当前子问题是：【$sub_question】。\n你有三个参考信息来源，ngql_recall_answer、kg_recall_content和doc_recall_content。其中，ngql_recall_answer是ngql语句的召回结果，该工具准确度非常高，只要有答案，基本都是正确的。\nkg_recall_content是kg召回结果，该信息来源的置信度也非常高。\ndoc_recall_content是doc召回结果。信息来源的置信度略低。\n\n回答当前子问题：【$sub_question】\n三个数据来源的具体内容如下：\nngql_recall_answer：$ngql_recall_answer\nkg_recall_content：$kg_recall_answer\ndoc_recall_content：$doc_recall_answer。仔细综合三个数据来源的信息，通过一定的推理过程来回答用户问题。回答格式为：针对当前query（$rewrite_query），答案是：xxxx。如果无法回答用户问题，则直接回复：抱歉，我不知道。 -> sub_question_answer
/end/

/prompt/用户原始的问题为$query。现在你已经收集到了所有子问题的答案，信息如下：$sub_question_answers。仔细综合已有信息，通过推理准确的给出最终答案。-> final_answer

