# 工具类构造规范

## 1. 基本结构

每个工具类文件应包含以下主要部分：

```python
# 1. 导入必要的模块
from typing import Optional
from dataclasses import dataclass
import logging
from .base import BaseTool

# 2. 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. 定义结果数据类
@dataclass
class ToolResult:
    success: bool
    message: str
    content: Optional[Any] = None

# 4. 定义工具类
class SomeTool(BaseTool):
    def __init__(self):
        pass
        
    def main_method(self) -> ToolResult:
        pass

# 5. 提供对外函数接口
def tool_function(param: str) -> str:
    pass

# 6. 测试代码
if __name__ == "__main__":
    pass
```

## 2. 详细规范

### 2.1 数据类（Result Class）
- 使用 `@dataclass` 装饰器
- 必须包含三个基本字段：
  - `success`: 布尔值，表示操作是否成功
  - `message`: 字符串，描述操作结果或错误信息
  - `content`: 可选字段，存储实际结果数据

### 2.2 工具类（Tool Class）
- 继承自 `BaseTool`
- 类名应以 `Tool` 结尾
- 包含完整的文档字符串
- 实现必要的方法：
  ```python
  class XxxTool(BaseTool):
      """工具类的详细描述"""
      
      def __init__(self):
          """初始化方法，设置必要的配置"""
          super().__init__()
          
      def main_method(self, param: str) -> ToolResult:
          """主要功能方法"""
          try:
              logger.info(f"执行操作: {param}")
              result = self._process(param)
              return ToolResult(success=True, message="操作成功", content=result)
          except Exception as e:
              logger.error(f"操作失败: {str(e)}")
              return ToolResult(success=False, message=f"操作失败: {str(e)}")
  ```

### 2.3 对外函数接口
- 函数名应清晰表达功能
- 包含完整的 Google 风格文档字符串：
  - 功能描述
  - 参数说明
  - 返回值说明
  - 异常说明
  - 使用示例
  - 注意事项
- 统一的错误处理和返回格式

### 2.4 日志记录
- 在关键操作处添加日志
- 使用不同的日志级别：
  - `INFO`: 正常操作信息
  - `ERROR`: 错误信息
  - `DEBUG`: 调试信息

### 2.5 错误处理
- 使用 try-except 进行异常捕获
- 返回统一的错误信息格式
- 记录详细的错误日志

## 3. 使用示例

```python
# 定义结果数据类
@dataclass
class SearchResult:
    success: bool
    message: str
    content: Optional[str] = None

# 实现工具类
class SearchTool(BaseTool):
    def search(self, query: str) -> SearchResult:
        try:
            logger.info(f"执行搜索: {query}")
            result = self._do_search(query)
            return SearchResult(success=True, message="搜索成功", content=result)
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return SearchResult(success=False, message=f"搜索失败: {str(e)}")

# 提供对外接口
def search(query: str) -> str:
    """
    执行搜索并返回结果。

    Args:
        query: 搜索查询字符串

    Returns:
        str: 搜索结果或错误信息

    Examples:
        >>> result = search("Python tutorial")
        >>> print(result)
    """
    tool = SearchTool()
    result = tool.search(query)
    return result.content if result.success else result.message
```

## 4. 注意事项

1. 保持一致性：所有工具类都应遵循相同的结构和命名规范
2. 类型提示：使用 typing 模块提供完整的类型提示
3. 错误处理：统一的错误处理和返回格式
4. 文档完整：详细的文档字符串，包括使用示例
5. 测试用例：提供基本的测试代码
