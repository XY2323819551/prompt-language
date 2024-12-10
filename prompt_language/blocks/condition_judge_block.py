from dataclasses import dataclass
from typing import List, Union
from .base_block import BaseBlock
from prompt_language.utils.model_factory import get_model_response
from prompt_language.utils.prompt_logger import logger


@dataclass
class ConditionJudge:
    """条件判断的解析结果"""
    content: str         # 要判断的内容
    categories: List[str]  # 判断类别列表


class ConditionJudgeBlock(BaseBlock):
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行条件判断: {statement}")
        
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        
        logger.debug(f"解析结果: {parser_res}")
        condition = await self._parse_condition(statement)
        logger.debug(f"条件解析: {condition}")
        
        result = await self._classify_content(condition)
        logger.debug(f"分类结果: {result}")
        
        await self.save_result(res_name, result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {result}")

    
    async def _parse_condition(self, statement: str) -> ConditionJudge:
        """
        解析条件判断语句
        
        Args:
            statement: 形如 @condition_judge(下雪了好冷呀, ["晴天", "雨天", "阴天"]) 的语句
            
        Returns:
            ConditionJudge: 包含判断内容和类别的数据类
        """
        # 提取括号内的内容
        content = statement.strip()
        if not content.startswith('@condition_judge(') or not content.endswith(')'):
            raise ValueError(f"无效的条件判断语句: {content}")
            
        params_str = content[16:-1].strip()  # 去掉 @condition_judge( 和 )
        
        # 分割内容和类别
        content_part, categories_part = [p.strip() for p in params_str.split(',', 1)]
        
        # 处理类别列表
        categories = []
        if categories_part.startswith('[') and categories_part.endswith(']'):
            # 提取并清理类别
            for cat in categories_part[1:-1].split(','):
                cat = cat.strip().strip('"\'')  # 去除引号
                if cat:
                    categories.append(cat)
        
        return ConditionJudge(content=content_part, categories=categories)
    
    async def _classify_content(self, condition: ConditionJudge) -> str:
        """
        使用大模型对内容进行分类
        
        Args:
            condition: 包含待分类内容和类别列表的数据类
            
        Returns:
            str: 分类结果（从类别列表中选择一个）
        """
        messages = [
            {
                "role": "system",
                "content": f"""你是一个精确的文本分类器。
你的任务是将给定的内容准确分类到指定的类别中。
你只需要从提供的类别列表中选择一个最合适的，直接返回该类别即可，不要返回任何其他内容。

可选的类别有：{', '.join(condition.categories)}

规则：
1. 只返回类别列表中的一个类别
2. 不要解释原因
3. 不要返回其他任何内容"""
            },
            {
                "role": "user",
                "content": f"请对以下内容进行分类：{condition.content}"
            }
        ]
        
        result = await get_model_response(
            messages=messages,
            temperature=0
        )
        
        # 确保结果在类别列表中
        result = result.choices[0].message.content.strip()
        if result in condition.categories:
            return result
        return "no_answer"  # 如果结果不在类别列表中，返回第一个类别

