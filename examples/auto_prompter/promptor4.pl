@code(```json
{
    "task": "问题：{{query}}\n参考信息：{{content}}\n请根据参考信息回答问题",
    "dataset": "user_search_test2",
    "metrics": ["acc", "fluency", "consistency"]
}
```) -> vars



给定任务描述或现有提示词，生成一个详细的系统提示词，以有效指导语言模型完成任务。\n\n# 指导原则\n- 原始任务中有双括号包裹的变量占位符，请在提示词中使用这些变量占位符，不要删除它们。\n- 理解任务：掌握主要目标、目的、要求、约束条件和预期输出。\n- 最小化改动：如果提供了现有提示词，仅在简单的情况下改进它。对于复杂的提示词，在不改变原始结构的情况下增强清晰度并添加缺失的元素。\n- 推理先于结论：在得出任何结论之前鼓励推理步骤。注意！如果用户提供的示例中推理在结论之后，请颠倒顺序！切勿以结论开始示例！\n    - 推理顺序：指出提示词中的推理部分和结论部分（按具体字段名称）。对于每个部分，确定执行顺序，并判断是否需要颠倒。\n    - 结论、分类或结果应始终放在最后。\n- 清晰简洁：使用清晰、具体的语言。避免不必要的指令或空泛的陈述。\n- 格式化：使用markdown功能提高可读性。除非特别要求，否则不要使用```代码块。\n- 保留用户内容：如果输入任务或提示词包含大量指南或示例，完整保留它们，或尽可能接近原文。如果它们含糊不清，考虑分解成子步骤。保留用户提供的任何细节、指南、示例、变量或占位符。\n- 常量：在提示词中包含常量，因为它们不容易受到提示词注入的影响。比如指南、评分标准和示例。\n- 输出格式：详细说明最合适的输出格式。这应包括长度和语法（如简短句子、段落、JSON等）\n    - 对于输出明确定义或结构化数据（分类、JSON等）的任务，倾向于输出JSON。\n    - 除非明确要求，否则JSON不应该用代码块(```)包装。\n\n你输出的最终提示词应遵循以下结构。不要包含任何额外的评论，只输出完整的系统提示词。特别是不要在提示词的开始或结束处包含任何额外信息。（例如不要加"---"）\n\n[简明描述任务的指令 - 这应该是提示词的第一行，无需章节标题]\n\n[根据需要添加额外细节]\n\n[可选的章节，带标题或要点列出详细步骤]\n\n# 步骤 [可选]\n\n[可选：完成任务所需步骤的详细分解]\n\n# 输出格式\n\n[具体说明输出应如何格式化，无论是响应长度、结构（如JSON、markdown等）] >> prompts
FOR $item in [1, 2, 3, 4, 5]:
    @benchmark(prompt_template=${prompts[-1]}, dataset_name=${vars.dataset}, metrics=${vars.metrics}, log_file_path="output/promptor/$item-iteration.xlsx") >> acc_results
    IF ${acc_results[-1]} >= 0.9:
        @log2excelpic(prompts=$prompts、acc=$acc_results、suggestions=$suggestions) -> status
        @exit(msg="优化完成")
    else:
        @analyze_badcase(prompt_template=${prompts[-1]}, log_file_path="output/promptor/$item-iteration.xlsx") >> suggestions
        @prompt_optimizer(prompt_template=${prompts[-1]}, ans=$suggestions) >> prompts
    END
END

@log2excelpic(prompts=$prompts, acc=$acc_results, suggestions=$suggestions) -> status


IF $item == 5 and ${acc_results[-1]} < 0.9:
    @add_few_shot(prompt_template=${prompts[-1]}, acc=$acc_results, log_file_path="output/promptor/") >> prompts
    @benchmark(prompt_template=${prompts[-1]}, dataset_name=${vars.dataset}, metrics=${vars.metrics}, log_file_path="output/promptor/few_shot_iteration.xlsx") >> acc_results
END

@log2excelpic(prompts=$prompts, acc=$acc_results, suggestions=$suggestions) -> status




