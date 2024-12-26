"""
This module contains the main functionality for generating prompts.
"""

import os
import argparse
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import json

from .prompts import META_PROMPT, META_SCHEMA, META_SCHEMA_PROMPT

load_dotenv()

def get_api_key(api_key: Optional[str] = None) -> str:
    if api_key:
        return api_key
    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        return env_api_key
    raise ValueError("需要提供OpenAI API密钥")

def generate_prompt(
    task_or_prompt: str,
    api_key: Optional[str] = None,
    prompt_template: Optional[str] = META_PROMPT,
    model_name: Optional[str] = "gpt-4o-mini",
) -> str:
    api_key = get_api_key(api_key=api_key)
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": prompt_template,
            },
            {
                "role": "user",
                "content": f"Task:\n{task_or_prompt}",
            },
        ],
    )

    return f"```markdown\n{completion.choices[0].message.content}\n```"

def generate_meta_schema(
    task_or_prompt: str,
    api_key: Optional[str] = None,
    schema_template: dict = META_SCHEMA,
    prompt_template: Optional[str] = META_SCHEMA_PROMPT,
    model_name: Optional[str] = "gpt-4o-mini",
) -> dict:
    api_key = get_api_key(api_key=api_key)
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_schema", "json_schema": schema_template},
        messages=[
            {
                "role": "system",
                "content": prompt_template,
            },
            {
                "role": "user",
                "content": f"Task:\n{task_or_prompt}",
            },
        ],
    )

    return json.loads(completion.choices[0].message.content)

def main():
    parser = argparse.ArgumentParser(description="生成AI提示")
    parser.add_argument("task", type=str, help="任务描述或现有提示")
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt-4o-mini",
        help="要使用的模型名称",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="是否生成schema而不是prompt",
    )

    args = parser.parse_args()
    
    if args.schema:
        result = generate_meta_schema(task_or_prompt=args.task, model_name=args.model_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        prompt = generate_prompt(task_or_prompt=args.task, model_name=args.model_name)
        print(prompt)

if __name__ == "__main__":
    main()
