import os
from typing import List, Dict, Any
from .meta_prompt import meta_prompt
from .benchmark import benchmark
from .badcase_analyzer import analyze_badcase
from .prompt_optimizer import prompt_optimizer
from .add_few_shot import add_few_shot
from .log2excelpic import log2excelpic


class CoreLogic:
    def __init__(self, task: str, dataset: str, metrics: List[str], output_dir: str = "output/promptor/"):
        """
        初始化核心逻辑类
        
        Args:
            task: 任务描述
            dataset: 数据集名称
            metrics: 评估指标列表
            output_dir: 输出目录
        """
        self.task = task
        self.dataset = dataset
        self.metrics = metrics
        self.output_dir = output_dir
        self.prompts = []
        self.acc_results = []
        self.acc_results_fluency = []
        self.acc_results_consistency = []
        self.suggestions = []
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

    async def optimize(self, max_iterations: int = 5, target_acc: float = 0.9) -> Dict[str, Any]:
        """
        执行prompt优化流程
        
        Args:
            max_iterations: 最大迭代次数
            target_acc: 目标准确率
            
        Returns:
            优化结果字典
        """
        # 1. 使用meta_prompt生成初始prompt
        log_file = os.path.join(self.output_dir, f"1iteration.xlsx")
        current_prompt = self.task
        acc, fluency_acc, consistency_acc = await benchmark(
            prompt_template=current_prompt,
            dataset_name=self.dataset,
            metrics=self.metrics,
            log_file_path=log_file
        )
        self.acc_results.append(acc)
        self.acc_results_fluency.append(fluency_acc)
        self.acc_results_consistency.append(consistency_acc)
        print("============= (benchmark)准确率 =============")
        print(acc)
        self.prompts.append(current_prompt)
        self.suggestions.append("init")

        await log2excelpic(
            prompts=self.prompts,
            acc=self.acc_results,
            fluency_acc=self.acc_results_fluency,
            consistency_acc=self.acc_results_consistency,
            suggestions=self.suggestions
        )


        initial_meta_prompt = await meta_prompt(self.task)
        self.prompts.append(initial_meta_prompt)
        print("============= initial_meta_prompt =============")
        print(initial_meta_prompt)

        # 2. 开始迭代优化
        for i in range(max_iterations + 1):
            # 2.1 评估当前prompt
            current_prompt = self.prompts[-1]
            log_file = os.path.join(self.output_dir, f"{i+2}iteration.xlsx")
            acc, fluency_acc, consistency_acc = await benchmark(
                prompt_template=current_prompt,
                dataset_name=self.dataset,
                metrics=self.metrics,
                log_file_path=log_file
            )
            self.acc_results.append(acc)
            self.acc_results_fluency.append(fluency_acc)
            self.acc_results_consistency.append(consistency_acc)
            print("============= (benchmark)准确率 =============")
            print(acc)
            
            
            # 2.2 记录当前状态
            await log2excelpic(
                prompts=self.prompts,
                acc=self.acc_results,
                fluency_acc=self.acc_results_fluency,
                consistency_acc=self.acc_results_consistency,
                suggestions=self.suggestions
            )
            # 2.3 检查是否达到目标
            if acc >= target_acc or i == max_iterations + 1:
                return {
                    "status": "success",
                    "iterations": i + 1,
                    "final_acc": acc,
                    "final_prompt": current_prompt
                }
            if i == max_iterations:
                break
            
            # 2.4 分析错误案例
            suggestion = await analyze_badcase(
                prompt_template=current_prompt,
                log_file_path=log_file
            )
            self.suggestions.append(suggestion)
            
            # 2.5 优化prompt
            new_prompt = await prompt_optimizer(
                prompt_template=current_prompt,
                ans=suggestion
            )
            self.prompts.append(new_prompt)
        
        # 3. 如果达到最大迭代次数仍未达标,尝试few-shot
        if self.acc_results[-1] < target_acc:
            few_shot_prompt = await add_few_shot(
                prompts=self.prompts,
                acc=self.acc_results,
                log_file_path=self.output_dir
            )
            self.prompts.append(few_shot_prompt)
            
            # 评估few-shot效果
            final_acc, fluency_acc, consistency_acc = await benchmark(
                prompt_template=few_shot_prompt,
                dataset_name=self.dataset,
                metrics=self.metrics,
                log_file_path=os.path.join(self.output_dir, "few_shot_iteration.xlsx")
            )
            self.acc_results.append(final_acc)
            self.acc_results_fluency.append(fluency_acc)
            self.acc_results_consistency.append(consistency_acc)
            
            # 记录最终状态
            await log2excelpic(
                prompts=self.prompts,
                acc=self.acc_results,
                fluency_acc=self.acc_results_fluency,
                consistency_acc=self.acc_results_consistency,
                suggestions=self.suggestions
            )
            
            return {
                "status": "few_shot_applied",
                "iterations": max_iterations + 1,
                "final_acc": final_acc,
                "final_prompt": few_shot_prompt
            }
        
        return {
            "status": "max_iterations_reached",
            "iterations": max_iterations,
            "final_acc": self.acc_results[-1],
            "final_prompt": self.prompts[-1]
        }


async def test_core_logic():
    # 测试配置
    task = """
    问题：{{query}}
    参考信息：{{content}}
    用中文根据参考信息回答问题。
    """
    # dataset = "user_search_test100"
    # metrics = ["acc", "fluency", "consistency"]
    # output_dir = "output/test_promptor/"


    task = """
    根据历史对话信息，对当前问题的指代和主语进行补充完善，给出完善后的query，完善后的query尽量简短。
    当前问题：{{query}}
    历史对话信息：{{history_message}}
    完善后的问题是：
    """

    dataset = "query_rewrite_test100"
    metrics = ["acc", "fluency", "consistency"]
    output_dir = "output/query_rewrite_promptor/"
    


    # 初始化CoreLogic实例
    core = CoreLogic(
        task=task,
        dataset=dataset,
        metrics=metrics,
        output_dir=output_dir
    )
    
    # 执行优化流程
    result = await core.optimize(max_iterations=3, target_acc=0.9)
    
    # 打印优化结果
    print("\n============= 优化结果 =============")
    print(f"状态: {result['status']}")
    print(f"迭代次数: {result['iterations']}")
    print(f"最终准确率: {result['final_acc']}")
    print("\n最终Prompt:")
    print(result['final_prompt'])
    
    # 打印优化过程
    print("\n============= 优化过程 =============")
    print("准确率变化:", core.acc_results)
    print("\nPrompt变化:")
    for i, prompt in enumerate(core.prompts):
        print(f"\n----- 第{i+1}次prompt -----")
        print(prompt)
    
    return result


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_core_logic())



