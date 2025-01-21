@code(```json
{
    "task": "问题：{{query}}\n参考信息：{{content}}\n回答问题",
    "dataset": "user_search_test2"
}
```) -> vars


@meta_prompt(task=${vars.task}) >> prompts
FOR $item in [1, 2, 3, 4, 5]:
    @benchmark(prompt_template=${prompts[-1]}, dataset_name=${vars.dataset}, log_file_path="output/promptor/$item-iteration.xlsx") >> acc_results
    IF ${acc_results[-1]} > 0.99:
        @log2excelpic(prompts=$prompts、acc=$acc_results、suggestions=$suggestions) -> status
        @exit(msg="优化完成")
    else:
        @analyze_badcase(prompt_template=${prompts[-1]}, log_file_path="output/promptor/$item-iteration.xlsx") >> suggestions
        @prompt_optimizer(prompt_template=${prompts[-1]}, ans=$suggestions) >> prompts
    END
END

@log2excelpic(prompts=$prompts, acc=$acc_results, suggestions=$suggestions) -> status
