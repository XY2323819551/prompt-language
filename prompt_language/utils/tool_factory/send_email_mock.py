from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailResult:
    """邮件发送结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class EmailTool(BaseTool):
    """模拟发送邮件的工具类"""
    
    def __init__(self):
        """初始化邮件工具"""
        super().__init__()
    
    def send(self, email: str, content: str) -> EmailResult:
        """
        模拟发送邮件。

        Args:
            email (str): 收件人邮箱地址
            content (str): 邮件内容

        Returns:
            EmailResult: 邮件发送结果数据类实例
        """
        try:
            logger.info(f"发送邮件到: {email}")
            return EmailResult(
                success=True,
                message="邮件发送成功",
                content=f"成功发送到{email}"
            )
        except Exception as e:
            logger.error(f"发送邮件时出错: {str(e)}")
            return EmailResult(
                success=False,
                message=f"发送邮件时出错: {str(e)}"
            )

def send_email(email: str, content: str) -> str:
    """
    模拟发送邮件并返回结果。

    这个函数模拟发送邮件的过程，并返回发送结果。

    Args:
        email (str): 收件人邮箱地址，例如 "example@example.com"
        content (str): 邮件内容

    Returns:
        str: 发送结果字符串。如果成功，将返回"成功发送到xxx@xxx.com"；
            如果失败，将返回错误信息。

    Examples:
        >>> result = send_email("test@example.com", "Hello World")
        >>> print(result)
        成功发送到test@example.com

    Note:
        - 这是一个mock工具
        - 不会真实发送邮件
        - 永远返回成功结果
    """
    tool = EmailTool()
    result = tool.send(email, content)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    email = "test@example.com"
    content = "Hello World"
    print(f"Testing send email to: {email}")
    print("-" * 80)
    result = send_email(email, content)
    print(result) 