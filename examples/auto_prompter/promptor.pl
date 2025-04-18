@code(```json
{
    "task": "问题：{{query}}\n参考信息：{{content}}\n请根据参考信息回答问题",
    "dataset": "user_search_test2",
    "metrics": ["acc"]
}
```) -> vars


@meta_prompt(task=${vars.task}) >> prompts
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

