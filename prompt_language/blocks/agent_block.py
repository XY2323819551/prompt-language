from typing import Dict, Any, Type
import re
from .base_block import BaseBlock
from prompt_language.utils.prompt_logger import logger
from prompt_language.utils.agent_factory import (
    BamboAgent, 
    PromptBasedAgent, 
    AutoDecisionAgent, 
    SelfRefineAgent, 
    PlanAndExecuteAgent
)


class AgentBlock(BaseBlock):
    # Agent类型映射
    AGENT_MAPPING = {
        "bambo": BamboAgent,
        "prompt-based": PromptBasedAgent,
        "auto-decision": AutoDecisionAgent,
        "self-refine": SelfRefineAgent,
        "plan-and-execute": PlanAndExecuteAgent
    }
    
    async def execute(self, statement, gv_pool, tool_pool) -> None:
        logger.info(f"执行Agent: {statement}")
        parser_res = await self.statement_parser.parse(statement, gv_pool)
        assign_method, res_name, statement = parser_res.assign_method, parser_res.res_name, parser_res.statement
        agent_params = self._parse_agent_params(statement)
        
        logger.debug(f"Agent参数: {agent_params}")
        agent = await self._create_agent(agent_params, tool_pool)
        logger.debug(f"创建Agent: {agent}")

        
        bambo_agent_result = ""
        async for item in agent.execute(agent_params.get("task", "")):
            bambo_agent_result += item
            print(item, end="", flush=True)

        logger.debug(f"Agent执行结果: {bambo_agent_result}")
        await self.save_result(res_name, bambo_agent_result, assign_method, gv_pool)
        logger.info(f"变量赋值: {res_name} = {bambo_agent_result}")

    def _parse_agent_params(self, statement: str) -> Dict[str, Any]:
        # 提取括号内的内容
        statement = ' '.join(line.strip() for line in statement.split('\n'))  # 将多行压缩成一行
        match = re.match(r'@agent\((.*)\)', statement.strip())
        if not match:
            raise ValueError(f"无效的agent语句格式: {statement}")
            
        params_str = match.group(1)
        
        # 使用正则表达式匹配键值对
        pattern = r'(\w+)\s*=\s*((?:"[^"]*"|\'[^\']*\'|\{[^}]*\}|\[[^\]]*\]))'
        matches = re.findall(pattern, params_str)
        
        # 初始化结果字典（设置默认值）
        result = {
            "type": "auto-decision",  # 默认值
            "task": "",
            "roles": {},
            "tools": []
        }
        
        # 解析每个参数
        for key, value in matches:
            try:
                # 对于字符串值，去除引号
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    result[key] = eval(value)
                # 对于字典和列表，使用eval解析
                elif value.startswith('{') or value.startswith('['):
                    result[key] = eval(value)
                else:
                    result[key] = value
            except Exception as e:
                logger.error(f"解析参数 {key}={value} 时出错: {str(e)}")
                result[key] = value  # 解析失败时保持原值
                
        return result

    async def _create_agent(self, params, tool_pool) -> Any:
        agent_type = params.get("type", "auto-decision")
        
        # 获取对应的Agent类
        agent_class = self.AGENT_MAPPING.get(agent_type)
        if not agent_class:
            logger.error(f"未知的Agent类型: {agent_type}")
            raise ValueError(f"未知的Agent类型: {agent_type}")
        
        try:
            # 根据不同的Agent类型处理参数
            if agent_type == "bambo":
                # Bambo Agent需要roles和tools参数
                agent = agent_class(
                    roles=params.get("roles", {}),
                    tools=params.get("tools", []),
                    tool_pool=tool_pool
                )
                await agent.init()  # 调用异步初始化
            else:
                # 其他Agent统一使用task和tools参数
                agent = agent_class(
                    task=params.get("task", ""),
                    tools=params.get("tools", []),
                    tool_pool=tool_pool
                )
            logger.info(f"成功创建 {agent_type} Agent")
            return agent
            
        except Exception as e:
            logger.error(e)  # 直接传递异常对象
            raise  # 重新抛出异常


