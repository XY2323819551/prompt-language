

# 模型工厂使用手册

## 1. 查看和使用现有模型

### 1.1 获取所有支持的模型
```python
from prompt_language.utils.model_factory import ModelRegistry

# 获取所有已注册的模型列表
all_models = ModelRegistry.get_all_models()
```

### 1.2 当前支持的模型列表
- DeepSeek模型
  - `deepseek-chat`
- Groq模型
  - `mixtral-8x7b-32768`
  - `llama3-70b-8192`
  - `llama3-groq-70b-8192-tool-use-preview`
  - `llama-3.2-90b-text-preview`
  - `llama-3.2-70b-versatile-preview`
  - `llama-3.1-70b-versatile`
  - `gemma2-9b-it`
- Together模型
  - `Qwen/Qwen2-72B-Instruct`
  - `codellama/CodeLlama-34b-Python-hf`
- OpenAI模型
  - `gpt-4o`
  - `gpt-4o-mini`

### 1.3 获取特定供应商的模型
```python
from prompt_language.utils.model_factory import ModelRegistry, ModelProvider

# 获取Groq提供的所有模型
groq_models = ModelRegistry.get_provider_models(ModelProvider.GROQ)
```

## 2. 注册新模型

### 2.1 单个模型注册
```python
from prompt_language.utils.model_factory import ModelRegistry, ModelProvider

# 注册单个模型
ModelRegistry.register_models({
    "claude-3-opus-20240229": ModelProvider.OPENAI
})
```

### 2.2 批量注册模型
```python
# 批量注册多个模型
new_models = {
    "claude-3-opus-20240229": ModelProvider.OPENAI,
    "claude-3-sonnet-20240229": ModelProvider.OPENAI,
    "gpt-4-turbo": ModelProvider.OPENAI
}
ModelRegistry.register_models(new_models)
```

## 3. 注册新的模型供应商

### 3.1 注册新供应商
```python
# 注册新的供应商
new_provider = ModelRegistry.register_provider("Anthropic")

# 为新供应商注册模型
ModelRegistry.register_models({
    "claude-3": new_provider,
    "claude-2": new_provider
})
```

## 4. 错误处理

### 4.1 常见错误处理
```python
try:
    # 错误的注册方式
    ModelRegistry.register_models({
        "invalid-model": "InvalidProvider"  # 错误：提供商必须是ModelProvider类型
    })
except ValueError as e:
    print(f"错误: {str(e)}")
```

## 5. 完整使用示例

```python
from prompt_language.utils.model_factory import ModelRegistry, ModelProvider

# 1. 查看现有模型
all_models = ModelRegistry.get_all_models()
print("所有支持的模型:", all_models)

# 2. 查看特定供应商的模型
groq_models = ModelRegistry.get_provider_models(ModelProvider.GROQ)
print("Groq支持的模型:", groq_models)

# 3. 注册新的供应商
anthropic = ModelRegistry.register_provider("Anthropic")

# 4. 为新供应商注册模型
ModelRegistry.register_models({
    "claude-3": anthropic,
    "claude-2": anthropic
})

# 5. 验证注册结果
anthropic_models = ModelRegistry.get_provider_models(anthropic)
print("Anthropic支持的模型:", anthropic_models)
```

## 6. 注意事项

1. 注册新模型时，提供商必须是`ModelProvider`类型
2. 模型名称不能重复，新注册的模型会覆盖同名的已存在模型
3. 注册新的供应商后，需要为其注册对应的模型才能使用
4. 建议在使用前先检查模型是否已经注册
5. 所有操作都有适当的错误处理机制

## 7. 最佳实践

1. 在项目初始化时完成所有模型和供应商的注册
2. 使用前先验证模型的可用性
3. 保持模型名称的唯一性
4. 使用批量注册来提高效率
5. 始终使用正确的类型进行注册
