from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from collections import deque
import os
import asyncio


@dataclass
class Block:
    """代码块的数据类"""
    block_type: str
    statement: str


class GlobalParser:
    """全局解析器，用于解析整个文件并将其分解为代码块"""
    
    def __init__(self):
        self.blocks = asyncio.Queue()
        self.current_block = []
        
    def _is_block_start(self, line: str) -> tuple[bool, str]:
        """判断是否是block的开始"""
        line = line.strip()
        
        # 高级语句
        if line.startswith('FOR'):
            return True, 'loop'
        if line.startswith('IF'):
            return True, 'judgment'
            
        # 基础语句（都以@开头）
        if line.startswith('@code('):
            return True, 'code'
        if line.startswith('@condition_judge('):
            return True, 'condition_judge'
        if line.startswith('@exit('):
            return True, 'exit'
        if line.startswith('@agent('):
            return True, 'agent'
        if line.startswith('@'):
            return True, 'function'
            
        # llm语句（不以@开头但包含赋值符号）
        if ('->' in line or '>>' in line) and not line.startswith('@'):
            return True, 'llm'
            
        return False, ''
        
    def _is_advanced_block(self, block_type: str) -> bool:
        """判断是否是高级语句"""
        return block_type in ['loop', 'judgment']
        
    def _is_assignment_line(self, line: str) -> bool:
        """判断是否是赋值语句行"""
        return '->' in line or '>>' in line
        
    def _is_statement_end(self, line: str) -> bool:
        """判断是否是某个语句的结束"""
        line = line.strip()
        return (self._is_assignment_line(line) or  # 基础语句的赋值结束
                line.endswith(')') or  # exit语句结束
                line == 'END' or  # 高级语句结束
                '```' in line)  # code块结束
        
    async def _find_statement_end(self, lines: List[str], start_idx: int, block_type: str) -> Tuple[int, int]:
        """
        异步查找语句的结束位置
        
        Args:
            lines: 所有行
            start_idx: 开始行索引
            block_type: 语句类型
            
        Returns:
            (真正的起始位置, 结束位置)
        """
        if block_type == 'exit':
            # 处理exit语句，查找匹配的右括号
            i = start_idx
            bracket_count = 1  # 已经遇到了第一个左括号
            
            # 从第一个左括号后开始查找
            start_pos = lines[i].find('(') + 1
            # 检查第一行剩余部分
            for char in lines[i][start_pos:]:
                if char == '(':
                    bracket_count += 1
                elif char == ')':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return start_idx, i
            
            # 继续查找后续行
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                for char in line:
                    if char == '(':
                        bracket_count += 1
                    elif char == ')':
                        bracket_count -= 1
                        if bracket_count == 0:
                            return start_idx, i
                i += 1
            return start_idx, start_idx
            
        if block_type == 'code':
            # 处理code block
            i = start_idx
            first_backtick = False
            in_code_block = False
            
            while i < len(lines):
                line = lines[i].strip()
                
                # 如果当前行就包含完整语句
                if i == start_idx and self._is_assignment_line(line):
                    return start_idx, i
                    
                if '```' in line:
                    if not first_backtick:
                        first_backtick = True
                        in_code_block = True
                    else:
                        in_code_block = False
                        # 找到配对的```��，继续找赋值语句
                        if self._is_assignment_line(line):
                            return start_idx, i
                        i += 1
                        while i < len(lines):
                            if self._is_assignment_line(lines[i]):
                                return start_idx, i
                            i += 1
                i += 1
            return start_idx, start_idx
            
        # 处理llm语句（prompt block）
        if block_type == 'llm':
            # 先找到结束位置（包含赋值符号的行）
            end_idx = start_idx
            while end_idx < len(lines):
                if self._is_assignment_line(lines[end_idx]):
                    break
                end_idx += 1
            if end_idx >= len(lines):
                return start_idx, start_idx
            
            # 确定起始位置
            real_start = start_idx
            
            # 如果是文件开头的prompt block，直接从第一行开始
            if await self._is_first_block(lines, start_idx):
                real_start = 0
            # 如果是中间的prompt block，从上一个block的结束位置开始
            elif start_idx > 0:
                # 向上查找上一个block的结束位置
                prev_idx = start_idx - 1
                while prev_idx >= 0:
                    line = lines[prev_idx].strip()
                    if (line.endswith(')') or  # exit语句结束
                        self._is_assignment_line(line) or  # 其他语句的赋值
                        line == 'END' or  # 高级语句结束
                        '```' in line):  # code块结束
                        real_start = prev_idx + 1
                        break
                    prev_idx -= 1
                if prev_idx < 0:  # 如果没找到上一个block的结束，说明是文件开头
                    real_start = 0
                
            return real_start, end_idx
            
        # 其他基础语句，找到赋值语句为止
        i = start_idx
        while i < len(lines):
            if self._is_assignment_line(lines[i]):
                return start_idx, i
            i += 1
        return start_idx, start_idx
        
    def _get_indent_level(self, line: str) -> int:
        """获取缩进级别"""
        indent_level = 0
        for char in line:
            if char == ' ':
                indent_level += 1
            else:
                break
        return indent_level
        
    async def _find_advanced_block_end(self, lines: List[str], start_idx: int) -> int:
        """
        异步查找高级语句块的��束位置
        
        Args:
            lines: 所有行
            start_idx: 开始行索引
            
        Returns:
            结束行索引
        """
        # 获取起始行的缩进级别
        start_line = lines[start_idx]
        start_indent = self._get_indent_level(start_line)
        
        i = start_idx + 1
        while i < len(lines):
            line = lines[i].rstrip()  # 保留左侧空格
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            current_indent = self._get_indent_level(line)
            
            # 如果遇到同级别的END，说明找到了块的结束
            if line.strip() == 'END' and current_indent == start_indent:
                return i
            
            # 如果遇到缩进更少的非空行，说明块结构有误
            if current_indent < start_indent and line.strip():
                return start_idx
            
            i += 1
        
        # 如果没找到对应的END，返回开始位置
        return start_idx
        
    async def _is_first_block(self, lines: List[str], start_idx: int) -> bool:
        """异步判断是否是文件的第一个block"""
        for i in range(start_idx):
            line = lines[i].strip()
            if line and (line.startswith('@') or 
                        self._is_assignment_line(line) or 
                        line == 'END' or 
                        line.startswith('FOR ') or 
                        line.startswith('IF ')):
                return False
        return True

    async def parse(self, content: str) -> asyncio.Queue:
        """异步解析整个文件内容，返回异步队列"""
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            if not line:  # 跳过空行
                i += 1
                continue
            
            # 检查是否是新的block开始
            is_start, block_type = self._is_block_start(line)
            
            if is_start:
                if self._is_advanced_block(block_type):
                    # 处理高级语句块
                    end_idx = await self._find_advanced_block_end(lines, i)
                    if end_idx > i:
                        block = Block(
                            block_type=block_type,
                            statement='\n'.join(lines[i:end_idx + 1])
                        )
                        await self.blocks.put(block)
                        i = end_idx
                else:
                    # 处理基础语句
                    start_idx, end_idx = await self._find_statement_end(lines, i, block_type)
                    if end_idx >= start_idx:
                        statement = '\n'.join(lines[start_idx:end_idx + 1])
                        block = Block(block_type=block_type, statement=statement)
                        await self.blocks.put(block)
                        i = end_idx
            
            i += 1
        
        return self.blocks
