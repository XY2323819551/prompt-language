import re
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass


@dataclass
class LoopBlock:
    """循环块的数据类"""
    variable: str  # 循环变量名
    target: str   # 循环目标对象的原始字符串表示
    iteration_target: Any  # 实际的迭代对象
    statement: str  # 循环体语句（原始字符串）


@dataclass
class JudgmentBlock:
    """判断块的数据类"""
    condition_value: str  # 条件成立的值
    statement: str  # 对应的语句块


@dataclass
class Statement:
    """语句的数据类"""
    assign_method: Optional[str]  # 赋值方法 (->, >> 或 None)
    res_name: Optional[str]      # 结果变量名
    statement: Optional[str]     # 语句内容


class LoopParser:
    """循环语句解析器"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*')
        self.complex_variable_pattern = re.compile(r'\${([^}]+)}')
    
    def _normalize_indent(self, content: str) -> str:
        """标准化缩进，保持相对缩进的同时移除公共缩进"""
        lines = content.splitlines()
        if not lines:
            return ""
            
        # 获取最小缩进
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return ""
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        
        # 处理每一行的缩进
        normalized_lines = []
        for line in lines:
            if line.strip():  # 非空行
                if len(line) >= min_indent:
                    normalized_lines.append(line[min_indent:])
                else:
                    normalized_lines.append(line.lstrip())
            else:  # 空行
                normalized_lines.append('')
                
        return '\n'.join(normalized_lines)
    
    def _extract_target(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """
        提取迭代目标表达式，处理多行情况
        
        Args:
            lines: 所有行
            start_idx: 开始行的索引
            
        Returns:
            (处理后的目标表达式, 结束行的索引)
        """
        # 找到第一行中 "in" 后面的内容
        first_line = lines[start_idx]
        in_pos = first_line.find(' in ')
        if in_pos == -1:
            raise ValueError("FOR循环语法错误：缺少 'in' 关键字")
            
        target_start = first_line[in_pos + 4:].strip()
        
        # 如果不是多行列表，直接返回
        if ':' in target_start:
            return target_start.split(':')[0].strip(), start_idx
            
        # 处理多行列表
        if target_start.startswith('['):
            target_parts = [target_start]
            current_idx = start_idx + 1
            
            while current_idx < len(lines):
                line = lines[current_idx].strip()
                if ':' in line:  # 找到列表结束
                    target_parts.append(line.split(':')[0].strip())
                    break
                target_parts.append(line)
                current_idx += 1
                
            # 合并多行并清理格式
            full_target = ' '.join(target_parts)
            # 清理多行的空格和换行
            full_target = re.sub(r'\s+', ' ', full_target)
            return full_target, current_idx
            
        # 处理其他情况（变量引用等）
        if not target_start.endswith(':'):
            current_idx = start_idx + 1
            while current_idx < len(lines):
                line = lines[current_idx].strip()
                if ':' in line:
                    target_start += line.split(':')[0].strip()
                    break
                target_start += line
                current_idx += 1
            return target_start, current_idx
            
        return target_start, start_idx
    
    async def parse(self, content: str, gv_pool: Any = None) -> LoopBlock:
        """
        解析FOR循环块
        
        Args:
            content: 包含完整FOR循环的字符串
            gv_pool: 变量池实例，用于解析迭代目标
            
        Returns:
            LoopBlock: 解析后的循环块数据
        """
        lines = content.strip().split('\n')
        
        # 解析FOR行
        for_line = lines[0].strip()
        if not for_line.startswith('FOR '):
            raise ValueError("不是有效的FOR循环语句")
        
        # 获取循环变量名
        in_pos = for_line.find(' in ')
        if in_pos == -1:
            raise ValueError("FOR循环语法错误：缺少 'in' 关键字")
            
        variable = for_line[4:in_pos].strip()
        if not self.variable_pattern.match(variable):
            raise ValueError(f"无效的循环变量名: {variable}")
        
        # 提取目标表达式
        target, end_idx = self._extract_target(lines, 0)
        
        # 提取循环体并处理缩进
        statement = '\n'.join(lines[end_idx + 1:-1])  # 跳过目标行和END行
        normalized_statement = self._normalize_indent(statement)
        
        # 获取实际的迭代目标
        iteration_target = None
        if gv_pool:
            iteration_target = await self.get_iteration_target(target, gv_pool)
        
        return LoopBlock(
            variable=variable,
            target=target,
            iteration_target=iteration_target,
            statement=normalized_statement
        )
    
    def _is_list_literal(self, target: str) -> bool:
        """判断是否是列表字面量"""
        return target.strip().startswith('[') and target.strip().endswith(']')
    
    def _parse_list_literal(self, target: str) -> List[str]:
        """解析列表字面量"""
        # 移除方括号并分割元素
        content = target.strip()[1:-1]
        elements = [elem.strip().strip('"\'') for elem in content.split(',')]
        return [elem for elem in elements if elem]  # 移除空元素
    
    async def get_iteration_target(self, target: str, gv_pool: Any) -> Any:
        """
        获取循环的目标对象
        
        Args:
            target: 目标字符串
            gv_pool: 变量池实例
            
        Returns:
            可迭代对象
        """
        # 处理列表字面量
        if self._is_list_literal(target):
            return self._parse_list_literal(target)
        
        # 处理复杂变量表达式 ${var.field} 或 ${var[index]}
        complex_match = self.complex_variable_pattern.match(target)
        if complex_match:
            var_expr = complex_match.group(1)
            # 处理字典字段访问
            if '.' in var_expr:
                var_name, field = var_expr.split('.', 1)
                var_obj = await gv_pool.get_variable(var_name.strip('$'))
                return var_obj[field] if var_obj else None
            # 处理列表索引访问
            elif '[' in var_expr and ']' in var_expr:
                var_name = var_expr[:var_expr.find('[')]
                index = int(var_expr[var_expr.find('[')+1:var_expr.find(']')])
                var_obj = await gv_pool.get_variable(var_name.strip('$'))
                return var_obj[index] if var_obj else None
        
        # 处理简单变量 $var
        if target.startswith('$'):
            var_name = target.strip('$')
            return await gv_pool.get_variable(var_name)
        
        return None


class JudgmentParser:
    """判断语句解析器"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*')
        self.complex_variable_pattern = re.compile(r'\${([^}]+)}')
    
    def _normalize_indent(self, content: str) -> str:
        """标准化缩进，保持相对缩进的同时移除公共缩进"""
        lines = content.splitlines()
        if not lines:
            return ""
            
        # 获取最小缩进
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return ""
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        
        # 处理每一行的缩进
        normalized_lines = []
        for line in lines:
            if line.strip():  # 非空行
                if len(line) >= min_indent:
                    normalized_lines.append(line[min_indent:])
                else:
                    normalized_lines.append(line.lstrip())
            else:  # 空行
                normalized_lines.append('')
                
        return '\n'.join(normalized_lines)
    
    def _extract_condition(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """提取条件表达式，处理多行情况"""
        first_line = lines[start_idx].strip()
        
        # 移除IF/elif前缀
        if first_line.startswith('IF '):
            condition = first_line[3:]
        elif first_line.startswith('elif '):
            condition = first_line[5:]
        else:
            return "", start_idx
            
        # 如果当前行包含冒号，直接处理
        if ':' in condition:
            return condition.split(':')[0].strip(), start_idx
            
        # 处理没有冒号的情况
        condition_parts = []
        current_line = condition
        
        # 在当前行中查找语句开始的标记
        for marker in ['@', '->', '>>', ':']:
            if marker in current_line:
                current_line = current_line.split(marker)[0]
                condition_parts.append(current_line.strip())
                return ' '.join(condition_parts), start_idx
                
        condition_parts.append(current_line.strip())
        
        # 处理多行条件
        current_idx = start_idx + 1
        while current_idx < len(lines):
            line = lines[current_idx].strip()
            
            # 如果遇到冒号，结束条件
            if ':' in line:
                condition_parts.append(line.split(':')[0].strip())
                break
                
            # 检查是否遇到语句标记
            found_marker = False
            for marker in ['@', '->', '>>', ':']:
                if marker in line:
                    condition_parts.append(line.split(marker)[0].strip())
                    found_marker = True
                    break
                    
            if found_marker:
                break
                
            # 如果是普通的条件行
            if line and not line.startswith(('IF', 'elif', 'else', 'END')):
                condition_parts.append(line)
                
            current_idx += 1
            
        # 合并并清理条件
        full_condition = ' '.join(condition_parts)
        return full_condition.strip(), current_idx if ':' in lines[current_idx].strip() else start_idx
    
    def _extract_block(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """
        提取语句块，直到遇到END或下一个条件
        
        Args:
            lines: 所有行
            start_idx: 开始行的索引
            
        Returns:
            (语句块内容, 结束行的索引)
        """
        if start_idx >= len(lines):
            return "", start_idx
        
        block_lines = []
        current_idx = start_idx + 1
        start_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        
        while current_idx < len(lines):
            line = lines[current_idx]
            if not line.strip():  # 跳过空行
                current_idx += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            # 如果遇到同级别的END或elif/else，结束当前块
            if line.strip() in ['END', 'else:'] or line.strip().startswith('elif '):
                if current_indent <= start_indent:
                    break
            
            block_lines.append(line)
            current_idx += 1
            
        return '\n'.join(block_lines), current_idx - 1
    
    async def _evaluate_condition(self, condition: str, gv_pool: Any) -> bool:
        """
        评估条件表达式
        
        Args:
            condition: 条件表达式
            gv_pool: 变量池实例
            
        Returns:
            条件是否为真
        """
        # 替换复杂变量引用
        while '${' in condition:
            match = self.complex_variable_pattern.search(condition)
            if not match:
                break
                
            var_expr = match.group(1)
            var_value = None
            
            # 处理嵌套属性
            if '.' in var_expr:
                parts = var_expr.split('.')
                var_obj = await gv_pool.get_variable(parts[0].strip('$'))
                for part in parts[1:]:
                    var_obj = var_obj[part]
                var_value = var_obj
            else:
                var_value = await gv_pool.get_variable(var_expr.strip('$'))
                
            condition = condition.replace(f"${{{var_expr}}}", repr(var_value))
            
        # 替换简单变量引用
        while '$' in condition:
            match = self.variable_pattern.search(condition)
            if not match:
                break
                
            var_name = match.group(0)[1:]  # 移除$前缀
            var_value = await gv_pool.get_variable(var_name)
            condition = condition.replace(f"${var_name}", repr(var_value))
            
        # 评估条件
        try:
            return eval(condition)
        except Exception as e:
            raise ValueError(f"条件表达式评估失败: {str(e)}")
    
    async def parse(self, content: str, gv_pool: Any = None) -> JudgmentBlock:
        """
        解析IF判断块
        
        Args:
            content: 包含完整IF判断的字符串
            gv_pool: 变量池实例
            
        Returns:
            JudgmentBlock: 解析后的判断块数据
        """
        lines = content.strip().split('\n')
        current_idx = 0
        
        while current_idx < len(lines):
            line = lines[current_idx].strip()
            
            if line.startswith('IF '):
                # 提取IF条件
                condition, end_idx = self._extract_condition(lines, current_idx)
                # 提取IF块
                block, block_end = self._extract_block(lines, end_idx)
                
                # 评估IF条件
                if gv_pool and await self._evaluate_condition(condition, gv_pool):
                    return JudgmentBlock(
                        condition_value=condition,
                        statement=self._normalize_indent(block)
                    )
                current_idx = block_end + 1
                continue
                
            elif line.startswith('elif '):
                # 提取elif条件
                condition, end_idx = self._extract_condition(lines, current_idx)
                # 提取elif块
                block, block_end = self._extract_block(lines, end_idx)
                
                # 评估elif条件
                if gv_pool and await self._evaluate_condition(condition, gv_pool):
                    return JudgmentBlock(
                        condition_value=condition,
                        statement=self._normalize_indent(block)
                    )
                current_idx = block_end + 1
                continue
                
            elif line == 'else:':
                # 提取else块
                block, block_end = self._extract_block(lines, current_idx)
                return JudgmentBlock(
                    condition_value="other",
                    statement=self._normalize_indent(block)
                )
            
            current_idx += 1
            
        # 如果没有命中任何条件，返回特定值
        return JudgmentBlock(
            condition_value="other",
            statement="none"
        )


class StatementParser:
    """语句解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.variable_pattern = re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*')
        self.complex_variable_pattern = re.compile(r'\${([^}]+)}')
    
    async def parse(self, content: str, gv_pool: Any = None) -> Statement:
        """
        解析单条语句
        
        Args:
            content: 语句字符串
            gv_pool: 变量池实例，用于解析变量引用
            
        Returns:
            Statement: 解析后的语句数据
        """
        # 处理空内容
        if not content.strip():
            return Statement(None, None, None)
        
        # 查找赋值符号
        assign_method = None
        res_name = None
        statement = content.strip()
        
        if '->' in content:
            assign_method = '->'
            parts = content.split('->')
            statement = parts[0].strip()
            res_name = parts[1].strip()
        elif '>>' in content:
            assign_method = '>>'
            parts = content.split('>>')
            statement = parts[0].strip()
            res_name = parts[1].strip()
        
        # 如果有变量池，处理变量引用
        if gv_pool:
            statement = await self._replace_variables(statement, gv_pool)
        
        return Statement(
            assign_method=assign_method,
            res_name=res_name,
            statement=statement
        )
    
    async def _replace_variables(self, content: str, gv_pool: Any) -> str:
        """
        替换内容中的变量引用
        
        Args:
            content: 包含变量引用的字符串
            gv_pool: 变量池实例
            
        Returns:
            处理后的字符串
        """
        result = content
        
        # 处理复杂变量引用 ${var.field}
        while '${' in result:
            match = self.complex_variable_pattern.search(result)
            if not match:
                break
                
            var_expr = match.group(1)
            var_value = None
            
            # 处理嵌套属性
            if '.' in var_expr:
                parts = var_expr.split('.')
                var_obj = await gv_pool.get_variable(parts[0].strip('$'))
                if var_obj:
                    for part in parts[1:]:
                        var_obj = var_obj[part]
                    var_value = var_obj
            else:
                breakpoint()
                var_value = await gv_pool.get_variable(var_expr.strip('$'))
                
            if var_value is not None:
                result = result.replace(f"${{{var_expr}}}", str(var_value))
            else:
                # 如果变量不存在，保持原样
                break
        
        # 处理简单变量引用 $var
        while '$' in result:
            match = self.variable_pattern.search(result)
            if not match:
                break
                
            var_name = match.group(0)[1:]  # 移除$前缀
            var_value = await gv_pool.get_variable(var_name)
            
            if var_value is not None:
                result = result.replace(f"${var_name}", str(var_value))
            else:
                # 如果变量不存在，保持原样
                break
        
        return result

