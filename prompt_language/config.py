from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class GlobalVariablePool:
    """全局变量池类，用于管理全局变量"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
    
    async def init_variables(self, variables: Dict[str, Any]) -> None:
        self.variables = variables
    
    async def update_variables(self, variables: Dict[str, Any]) -> None:
        """
        批量更新全局变量
        
        如果变量名以$开头，会自动去掉$符号再存储
        
        Args:
            variables: 要更新的变量字典
        """
        processed_variables = {}
        for key, value in variables.items():
            # 如果变量名以$开头，去掉$
            if key.startswith('$'):
                processed_variables[key[1:]] = value
            else:
                processed_variables[key] = value
                
        self.variables.update(processed_variables)
    
    async def get_all_variables(self) -> Dict[str, Any]:
        """获取所有全局变量"""
        return self.variables.copy()
    
    async def get_variable(self, name: str) -> Optional[Any]:
        """获取指定的全局变量"""
        return self.variables.get(name)
    
    async def set_variable(self, name: str, value: Any) -> None:
        """
        设置单个全局变量
        
        如果变量名以$开头，会自动去掉$符号再存储
        
        Args:
            name: 变量名
            value: 变量值
        """
        # 如果变量名以$开头，去掉$
        if name.startswith('$'):
            name = name[1:]
        self.variables[name] = value
    
    async def append_variable(self, name: str, value: Any) -> None:
        if name.startswith('$'):
            name = name[1:]
        
        current_value = self.variables.get(name)
        if current_value is None:
            self.variables[name] = [value]
        elif not isinstance(current_value, list):
            self.variables[name] = [current_value, value]
        else:
            current_value.append(value)
    
    async def variable_exists(self, name: str) -> bool:
        """检查变量是否存在"""
        return name in self.variables


@dataclass
class GlobalToolPool:
    def __init__(self):
        self.tools: Dict[str, Any] = {}
    
    async def init_tools(self, tools: Dict[str, Any]) -> None:
        self.tools = tools
    
    async def register_tool(self, name: str, tool: Any) -> None:
        self.tools[name] = tool
    
    async def register_tools(self, tools: Dict[str, Any]) -> None:
        self.tools.update(tools)
    
    async def get_all_tools(self) -> List[Any]:
        return list(self.tools.values())
    
    async def get_tool(self, name: str) -> Optional[Any]:
        return self.tools.get(name)
    
    async def exists(self, name: str) -> bool:
        return name in self.tools


# 创建全局实例
gv_pool = GlobalVariablePool()
tool_pool = GlobalToolPool()

