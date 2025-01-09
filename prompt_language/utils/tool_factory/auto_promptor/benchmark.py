from .datasets_pool.test_query_rewrite import benchmark_query_rewrte
from .datasets_pool.test_user_search import benchmark_user_search

USER_SEARCH_DATASETS = {
    "agent_res_0.8414",
    "agent_res_test",
    "user_search_test",
    "user_search_test2"
}

QUERY_REWRITE_DATASETS = {
    "rewrite_50v1",
    "context_free_110",
    "query_rewrite_test"
}

async def benchmark(prompt_template: str, dataset_name: str, log_file_path: str = "output/benchmark_result.xlsx"):
    """
    统一的benchmark入口
    
    Args:
        prompt_template: str, 提示词模板
        dataset_name: str, 数据集名称
        log_file_path: str, 日志文件路径
        
    Returns:
        float: 最终的准确率
    """
    if dataset_name in USER_SEARCH_DATASETS:
        return benchmark_user_search(
            prompt_template=prompt_template,
            dataset_name=dataset_name,
            log_file_path=log_file_path
        )
    elif dataset_name in QUERY_REWRITE_DATASETS:
        return benchmark_query_rewrte(
            prompt_template=prompt_template,
            dataset_name=dataset_name,
            log_file_path=log_file_path
        )
    else:
        raise ValueError(f"Dataset {dataset_name} not found in any mapping")


async def main():
    # 测试用户搜索场景
    prompt_template = "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n"
    benchmark(
        prompt_template=prompt_template,
        dataset_name="user_search_test",
        log_file_path="output/benchmark_user_search_result.xlsx"
    )
    
    # # 测试查询改写场景
    # prompt_template = "根据历史信息对问题进行改写，消除指代，补充问题。问题：{{query}}\n历史对话信息：{{history_message}}\n回答格式：【重写后的问题】xxx\n\n改写后的问题是："
    # benchmark(
    #     prompt_template=prompt_template,
    #     dataset_name="query_rewrite_test",
    #     log_file_path="output/benchmark_query_rewrite_result.xlsx"
    # ) 


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
