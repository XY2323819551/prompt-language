import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

from groq import Groq, AsyncGroq
from openai import OpenAI, AsyncOpenAI
from together import Together, AsyncTogether

logging.getLogger("httpx").setLevel(logging.WARNING)


class ModelProvider(Enum):
    """模型提供商枚举"""
    DEEPSEEK = "DeepSeek"
    OPENAI = "OpenAI"
    GROQ = "Groq"
    TOGETHER = "Together"


@dataclass
class APIConfig:
    """API配置数据类"""
    base_url: str
    api_key: str


class ModelRegistry:
    """模型注册表"""
    
    # 模型到提供商的映射
    MODEL_PROVIDER_MAPPING = {
        # DeepSeek Models
        "deepseek-chat": ModelProvider.DEEPSEEK,

        # Groq Models
        "mixtral-8x7b-32768": ModelProvider.GROQ,
        "llama3-70b-8192": ModelProvider.GROQ,
        "llama3-groq-70b-8192-tool-use-preview": ModelProvider.GROQ,
        "llama-3.2-90b-text-preview": ModelProvider.GROQ,
        "llama-3.2-70b-versatile-preview": ModelProvider.GROQ,
        "llama-3.1-70b-versatile": ModelProvider.GROQ,
        "gemma2-9b-it": ModelProvider.GROQ,

        # Together Models
        "Qwen/Qwen2-72B-Instruct": ModelProvider.TOGETHER,
        "codellama/CodeLlama-34b-Python-hf": ModelProvider.TOGETHER,

        # OpenAI Models
        "gpt-4o": ModelProvider.OPENAI,
        "gpt-4o-mini": ModelProvider.OPENAI,
    }
    
    @classmethod
    def get_provider(cls, model_name: str) -> ModelProvider:
        """获取模型对应的提供商"""
        if model_name not in cls.MODEL_PROVIDER_MAPPING:
            raise ValueError(f"未知的模型: {model_name}")
        return cls.MODEL_PROVIDER_MAPPING[model_name]
    
    @classmethod
    def get_all_models(cls) -> List[str]:
        return list(cls.MODEL_PROVIDER_MAPPING.keys())
    
    @classmethod
    def get_provider_models(cls, provider: ModelProvider) -> List[str]:
        return [model for model, p in cls.MODEL_PROVIDER_MAPPING.items() if p == provider]
    
    @classmethod
    def register_models(cls, models: Dict[str, ModelProvider]) -> None:
        for model_name, provider in models.items():
            if not isinstance(provider, ModelProvider):
                raise ValueError(f"提供商必须是ModelProvider类型: {provider}")
            cls.MODEL_PROVIDER_MAPPING[model_name] = provider
    
    @classmethod
    def register_provider(cls, provider_name: str) -> ModelProvider:
        try:
            new_provider = ModelProvider(provider_name)
            return new_provider
        except ValueError:
            new_member = provider_name.upper()
            ModelProvider._member_map_[new_member] = new_member
            ModelProvider._value2member_map_[provider_name] = new_member
            return ModelProvider(provider_name)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        # 获取项目根目录
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.env_path = self.root_dir / '.env'
        
        # 加载环境变量
        load_dotenv(dotenv_path=self.env_path)
        
        # 初始化API配置
        self.api_configs = {
            ModelProvider.DEEPSEEK: APIConfig(
                base_url="https://api.deepseek.com",
                api_key=os.getenv("DEEPSEEK_API_KEY")
            ),
            ModelProvider.OPENAI: APIConfig(
                base_url="https://api.openai.com/v1",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            ModelProvider.GROQ: APIConfig(
                base_url="https://api.groq.com",
                api_key=os.getenv("GROQ_API_KEY")
            ),
            ModelProvider.TOGETHER: APIConfig(
                base_url="https://api.together.xyz/v1",
                api_key=os.getenv("TOGETHER_API_KEY")
            ),
        }
    
    def get_api_config(self, provider: ModelProvider) -> APIConfig:
        """获取指定提供商的API配置"""
        if provider not in self.api_configs:
            raise ValueError(f"未找到提供商 {provider} 的配置")
        return self.api_configs[provider]


class LLMClientFactory:
    """LLM客户端工厂"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def _create_client(self, provider: ModelProvider, config: APIConfig, 
                      is_async: bool = False) -> Union[OpenAI, AsyncOpenAI, Groq, AsyncGroq, Together, AsyncTogether]:
        """创建客户端实例"""
        if provider == ModelProvider.DEEPSEEK or provider == ModelProvider.OPENAI:
            return AsyncOpenAI(base_url=config.base_url, api_key=config.api_key) if is_async \
                else OpenAI(base_url=config.base_url, api_key=config.api_key)
        
        elif provider == ModelProvider.GROQ:
            return AsyncGroq(base_url=config.base_url, api_key=config.api_key) if is_async \
                else Groq(base_url=config.base_url, api_key=config.api_key)
        
        elif provider == ModelProvider.TOGETHER:
            return AsyncTogether(base_url=config.base_url, api_key=config.api_key) if is_async \
                else Together(base_url=config.base_url, api_key=config.api_key)
        
        raise ValueError(f"不支持的提供商: {provider}")
    
    def get_client(self, model_name: str, is_async: bool = False) -> Any:
        """获取LLM客户端"""
        provider = ModelRegistry.get_provider(model_name)
        config = self.config_manager.get_api_config(provider)
        return self._create_client(provider, config, is_async)


class LLMResponse:
    """LLM响应处理类"""
    
    @staticmethod
    async def create_chat_completion(
        client: Any,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        is_json: bool = False,
        tools: Optional[List[Dict]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False
    ) -> Any:
        """创建聊天完成请求"""
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stop": stop
        }
        
        if is_json:
            params["response_format"] = {"type": "json_object"}
        
        if tools:
            params["tools"] = tools
        
        if stream:
            params["stream"] = True
        
        return await client.chat.completions.create(**params)


# 导出便捷函数
client_factory = LLMClientFactory()

async def get_model_response(
    model_name: str = "deepseek-chat",
    messages: List[Dict[str, str]] = [],
    temperature: float = 0,
    is_json: bool = False,
    tools: Optional[List[Dict]] = None,
    stop: Optional[Union[str, List[str]]] = None,
    stream: bool = False
) -> Any:
    client = client_factory.get_client(model_name, is_async=True)
    response = await LLMResponse.create_chat_completion(
        client=client,
        model=model_name,
        messages=messages,
        temperature=temperature,
        is_json=is_json,
        tools=tools,
        stop=stop,
        stream=stream
    )
    return response


if __name__ == "__main__":
    # 测试获取所有模型
    all_models = ModelRegistry.get_all_models()
    print("所有支持的模型:", all_models)
    
    # 测试获取指定供应商的模型
    groq_models = ModelRegistry.get_provider_models(ModelProvider.GROQ)
    print("\nGroq支持的模型:", groq_models)
    
    # 测试批量注册新模型
    new_models = {
        "claude-3-opus-20240229": ModelProvider.OPENAI,
        "claude-3-sonnet-20240229": ModelProvider.OPENAI,
    }
    ModelRegistry.register_models(new_models)
    print("\n注册新模型后的OpenAI模型:", 
        ModelRegistry.get_provider_models(ModelProvider.OPENAI))
    
    # 测试注册新的供应商
    new_provider = ModelRegistry.register_provider("Anthropic")
    ModelRegistry.register_models({
        "claude-3": new_provider,
        "claude-2": new_provider
    })
    print("\n新供应商Anthropic的模型:", 
          ModelRegistry.get_provider_models(new_provider))
    
    # 验证错误处理
    try:
        ModelRegistry.register_models({"invalid-model": "InvalidProvider"})
    except ValueError as e:
        print("\n错误处理测试成功:", str(e))

