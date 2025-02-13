from typing import Dict, Any, Type
import re
from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger
from prompt_language.utils.agent_factory import (
    BamboAgent, 
    PromptBasedAgent, 
    AutoDecisionAgent,
    ExploreAgent
)
import traceback


class AgentBlock(BaseBlock):
    # Agent类型映射
    AGENT_MAPPING = {
        "bambo": BamboAgent,
        "explore": ExploreAgent,
        "prompt-based": PromptBasedAgent,
        "auto-decision": AutoDecisionAgent
    }
    
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行Agent: {statement}")

        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        agent_params = self._parse_agent_params(statement, gv_pool)
        logger.debug(f"Agent参数: {agent_params}")
        agent = await self._create_agent(agent_params, tool_pool)
        logger.debug(f"创建Agent: {agent}")

        agent_result = ""
        async for item in agent.execute(agent_params.get("task", "")):
            agent_result += item
            print(item, end="", flush=True)

        logger.debug(f"Agent执行结果: {agent_result}")
        await self.save_result(res_name, agent_result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {agent_result}")

    def _parse_agent_params(self, statement: str, gv_pool: Dict[str, Any]) -> Dict[str, Any]:
        """解析 agent 参数"""
        try:
            match = re.match(r'@agent\((.*)\)', statement.strip(), re.DOTALL)
            if not match:
                raise ValueError(f"无效的agent语句格式: {statement}")
            
            params_str = match.group(1).strip()
            result = {}
            
            current_key = None
            current_value = ""
            in_triple_quotes = False
            in_raw_text = False
            
            lines = params_str.split('\n')
            for line_num, line in enumerate(lines, 1):
                try:
                    line = line.strip()
                    if not line:
                        if in_triple_quotes or in_raw_text:
                            current_value += '\n'
                        continue
                    
                    # 处理键值对开始
                    if not (in_triple_quotes or in_raw_text) and '=' in line:
                        if current_key:
                            if isinstance(current_value, (dict, list)):  # 检查是否是复合类型
                                result[current_key] = current_value
                            else:
                                result[current_key] = current_value.strip()
                        
                        key, value = line.split('=', 1)
                        current_key = key.strip()
                        current_value = value.strip()
                        
                        # 检查变量引用
                        if current_value.startswith('$'):
                            var_name = current_value[1:]
                            var_value = gv_pool.get(var_name)
                            if var_value is not None:
                                result[current_key] = var_value
                                current_key = None
                                current_value = ""
                                continue
                        
                        # 检查是否是三引号开始
                        if current_value.startswith('"""'):
                            in_triple_quotes = True
                            current_value = current_value[3:]
                            continue
                        
                        # 检查是否是原始文本
                        if not (current_value.startswith('"') or current_value.startswith("'")):
                            # 如果是字典或列表，直接eval
                            if current_value.startswith('{') or current_value.startswith('['):
                                try:
                                    current_value = eval(current_value.rstrip(','))
                                    result[current_key] = current_value
                                    current_key = None
                                    current_value = ""
                                    continue
                                except:
                                    in_raw_text = True
                            else:
                                in_raw_text = True
                            continue
                        
                        # 处理普通值
                        if current_value.endswith(','):
                            current_value = current_value[:-1]
                        if current_value.startswith('"') and current_value.endswith('"'):
                            current_value = current_value[1:-1]
                        elif current_value.startswith('[') or current_value.startswith('{'):
                            current_value = eval(current_value.rstrip(','))
                        result[current_key] = current_value
                        current_key = None
                        current_value = ""
                        in_raw_text = False
                        continue
                    
                    # 处理三引号结束
                    if in_triple_quotes and '"""' in line:
                        in_triple_quotes = False
                        current_value += line.split('"""')[0]
                        result[current_key] = current_value.strip()
                        current_key = None
                        current_value = ""
                        continue
                    
                    # 在三引号或原始文本内，继续累积��
                    if in_triple_quotes or in_raw_text:
                        current_value += line + '\n'
                        continue
                        
                except Exception as e:
                    logger.error(f"解析第 {line_num} 行时出错: {line}\n错误: {str(e)}")
                    raise
            
            # 处理最后一个键值对
            if current_key:
                if current_value.startswith('$'):
                    var_name = current_value[1:]
                    var_value = gv_pool.get(var_name)
                    if var_value is not None:
                        result[current_key] = var_value
                else:
                    if current_value.endswith(','):
                        current_value = current_value[:-1]
                    try:
                        if current_value.startswith('{') or current_value.startswith('['):
                            current_value = eval(current_value)
                        elif current_value.startswith('"') and current_value.endswith('"'):
                            current_value = current_value[1:-1]
                    except:
                        pass
                    
                    if isinstance(current_value, (dict, list)):
                        result[current_key] = current_value
                    else:
                        result[current_key] = current_value.strip()
            
            # 设置默认值
            result.setdefault("type", "auto-decision")
            result.setdefault("task", "")
            result.setdefault("roles", {})
            result.setdefault("tools", [])
            
            return result
            
        except Exception as e:
            logger.error(f"解析agent参数失败:\n输入: {statement}\n错误: {str(e)}\n堆栈: {traceback.format_exc()}")
            raise

    async def _create_agent(self, params, tool_pool) -> Any:
        agent_type = params.get("type", "auto-decision")
        agent_class = self.AGENT_MAPPING.get(agent_type)
        if not agent_class:
            logger.error(f"未知的Agent类型: {agent_type}")
            raise ValueError(f"未知的Agent类型: {agent_type}")
        try:
            if agent_type == "bambo" or agent_type == "explore":
                agent = agent_class(
                    roles=params.get("roles", {}),
                    tools=params.get("tools", []),
                    tool_pool=tool_pool
                )
                await agent.init()
            else:
                agent = agent_class(
                    tools=params.get("tools", []),
                    tool_pool=tool_pool
                )
            logger.info(f"成功创建 {agent_type} Agent")
            return agent
            
        except Exception as e:
            logger.error(e)
            raise


