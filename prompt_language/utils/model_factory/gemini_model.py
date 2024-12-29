
import os
import asyncio
from pathlib import Path
from google import genai
from google.generativeai import types
from dotenv import load_dotenv
from IPython.display import Markdown



root_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

config=types.GenerationConfig(
    temperature=0.4,
    top_p=0.95,
    top_k=20,
    candidate_count=1,
    seed=5,
    max_output_tokens=2000,
    stop_sequences=["STOP!"],
    presence_penalty=0.0,
    frequency_penalty=0.0,
)

async def get_model_response_gemini(model="gemini-2.0-flash-exp", contents=""):
    response = client.models.generate_content(
        model=model, 
        contents=contents
    )
    return response.text



async def get_model_response_gemini_thinking():
    response = client.models.generate_content(
        model='gemini-2.0-flash-thinking-exp', contents='Explain how RLHF works in simple terms.'
    )
    for part in response.candidates[0].content.parts:
        if part.thought == True:
            print(f"Model Thought:\n{part.text}\n")
        else:
            print(f"\nModel Response:\n{part.text}\n")



async def get_model_response_gemini_thinking_stream():
    for chunk in client.models.generate_content_stream(
        model='gemini-2.0-flash-thinking-exp', 
        contents='Tell me the name of a country whose name ends with ‘lia’. Give me the capital city country as well.'
    ):
        for part in chunk.candidates[0].content.parts:
            if part.thought == True:
                print(f"Model Thought Chunk:\n{part.text}\n")
            else:
                print(f"\nModel Response:\n{part.text}\n")



async def multi_turn_chat(model_name='gemini-2.0-flash-thinking-exp'):
    chat = client.aio.chats.create(model=model_name)
    response = await chat.send_message('What is your name?')
    print(response.text)
    response = await chat.send_message('What did you just say before this?')
    print(response.text)

# https://ai.google.dev/gemini-api/docs/models/experimental-models
model_list = [
    'gemini-1.5-pro', 
    'gemini-1.5-flash', 
    'gemini-2.0-flash-exp',
    'gemini-exp-1206',
    'gemini-2.0-flash-thinking-exp',
    'gemini-2.0-flash-thinking-exp-1219',

    ]

if __name__ == "__main__":
    async def test():
        # 测试普通模型
        print("\n=== Gemini Pro 测试 ===")
        contents = "Write a haiku where the second letter of each word when put together spells “Simple”."
        response1 = await get_model_response_gemini(contents=contents)
        print(f"回复: {response1}")
        
        # 测试思考模型
        # print("\n=== Gemini Thinking 测试 ===")
        # response2 = await get_model_response_gemini_thinking()


        # # 测试思考模型
        # print("\n=== Gemini Thinking Stream 测试 ===")
        # response3 = await get_model_response_gemini_thinking_stream()

        # print("\n=== Gemini Thinking multi-turn chat ===")
        # response2 = await multi_turn_chat()

    asyncio.run(test())

