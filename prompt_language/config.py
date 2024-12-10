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
    
    async def variable_exists(self, name: str) -> bool:
        """检查变量是否存在"""
        return name in self.variables


@dataclass
class GlobalToolPool:
    """全局工具池类，用于管理全局工具"""
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
    
    async def init_tools(self, tools: Dict[str, Any]) -> None:
        """注册单个工具"""
        self.tools = tools
    
    async def register_tool(self, name: str, tool: Any) -> None:
        """注册单个工具"""
        self.tools[name] = tool
    
    async def register_tools(self, tools: Dict[str, Any]) -> None:
        """批量注册工具"""
        self.tools.update(tools)
    
    async def get_all_tools(self) -> Dict[str, Any]:
        """获取所有工具"""
        return self.tools.copy()
    
    async def get_tool(self, name: str) -> Optional[Any]:
        """获取指定的工具"""
        return self.tools.get(name)
    
    async def exists(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self.tools


# 创建全局实例
variable_pool = GlobalVariablePool()
tool_pool = GlobalToolPool()

