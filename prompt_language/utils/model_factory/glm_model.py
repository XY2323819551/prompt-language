import zhipuai
import requests
import json
import base64
import time
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

class GLMCreator:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))   # 加载 .env 文件
        self.api_key = os.getenv('ZHIPUAI_API_KEY')
        if not self.api_key:
            raise ValueError("未找到 ZHIPUAI_API_KEY 环境变量，请在 .env 文件中设置")
            
        zhipuai.api_key = self.api_key
        self.client = zhipuai.ZhipuAI(api_key=self.api_key)
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')  # 创建assets目录，存放生成的文件和视频
        os.makedirs(self.assets_dir, exist_ok=True)
        
    def _download_file(self, url: str, file_type: str) -> Optional[str]:
        """下载文件并保存到assets目录"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{file_type}_{timestamp}.{file_type}"
                filepath = os.path.join(self.assets_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
            return None
        except Exception as e:
            print(f"下载{file_type}文件时出错: {str(e)}")
            return None

    # glm-4-plus（text-generation）
    def generate_image_description(self, prompt: str) -> str:
        """使用GLM-3-Turbo生成图片描述"""
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[
                    {"role": "user", "content": f"请为以下主题生成一段详细的图片描述，包含场景、物体、颜色、光影等细节：\n{prompt}"}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"生成描述时出错: {str(e)}")
            return None

    # cogview-3-plus（text-to-image)
    def text_to_image(self, prompt: str) -> tuple[Optional[str], Optional[str]]:
        """使用CogView-3生成图片，返回(url, local_path)"""
        try:
            response = self.client.images.generations(
                model="cogview-3-plus",  # 也可以使用基础版本的cogview-3
                prompt=prompt,
            )
            
            if hasattr(response, 'data') and len(response.data) > 0:
                image_url = response.data[0].url
                local_path = self._download_file(image_url, 'png')
                return image_url, local_path
            return None, None
        except Exception as e:
            print(f"生成图片时出错: {str(e)}")
            return None, None

    # cogvideox（text-to-video)
    def text_to_video(self, prompt: str) -> tuple[Optional[str], Optional[str]]:
        """使用CogVideoX生成视频，返回(url, local_path)"""
        try:
            # 创建视频生成任务
            response = self.client.videos.generations(
                model="cogvideox",
                prompt=prompt
            )
            
            # 获取任务ID
            if hasattr(response, 'id'):
                task_id = response.id
                print(f"视频生成任务已创建，任务ID: {task_id}")
                
                # 轮询检查任务状态
                max_attempts = 10  # 最大尝试次数
                attempt = 0
                while attempt < max_attempts:
                    # 查询任务状态
                    status_response = self.client.videos.retrieve_videos_result(task_id)
                    
                    # 检查任务状态
                    if hasattr(status_response, 'task_status'):
                        if status_response.task_status == 'SUCCESS':
                            # 任务完成，获取视频URL
                            if hasattr(status_response, 'video_result') and len(status_response.video_result) > 0:
                                # cover_image_url = status_response.video_result[0].cover_image_url
                                video_url = status_response.video_result[0].url
                                local_path = self._download_file(video_url, 'mp4')
                                print(f"视频生成成功！")
                                return video_url, local_path
                        else:
                            print(f"视频正在生成中... ({attempt + 1}/{max_attempts})")
                    
                    attempt += 1
                    time.sleep(5)  # 每5秒检查一次
                
                print("视频生成超时")
                return None, None
            else:
                print("创建视频生成任务失败")
                return None, None
                
        except Exception as e:
            print(f"生成��频时出错: {str(e)}")
            return None, None

    # glm-4v-plus（基于视频的对话)
    def vision_chat_with_video(self, video_path: str, prompt: str) -> str:
        """
        上传视频base64 + 语言指令进行对话
        Args:
            video_path: 视频文件路径
            prompt: 用户提问
        Returns:
            模型回答
        """
        try:
            # 读取视频文件并转换为base64
            with open(video_path, 'rb') as video_file:
                video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="glm-4v-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "video_url",
                                "video_url": {
                                    "url": f"data:video/mp4;base64,{video_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            return None
            
        except Exception as e:
            print(f"视频对话出错: {str(e)}")
            return None

    # glm-4v-plus（基于图片的对话)
    def vision_chat_with_image(self, image_path: str, prompt: str) -> str:
        """
        上传图片base64 + 语言指令进行对话
        Args:
            image_path: 图片文件路径
            prompt: 用户提问
        Returns:
            模型回答
        """
        try:
            # 读取图片文件并转换为base64
            with open(image_path, 'rb') as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="glm-4v-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            return None
            
        except Exception as e:
            print(f"图片对话出错: {str(e)}")
            return None

    # glm-4-plus
    def agent_chat(self, prompt: str) -> str:
        """
        使用glm-4-plus进行智能体对话
        Args:
            prompt: 用户输入的问题
        Returns:
            模型回答
        """
        try:
            messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            response = self.client.chat.completions.create(
                model="glm-4-plus",  # glm-4-alltools、glm-4-plus
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "获取指定城市的天气信息",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "城市名称，如：北京"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"],
                                        "description": "温度单位"
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_stock_price",
                            "description": "获取指定股票的价格信息",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "symbol": {
                                        "type": "string",
                                        "description": "股票代码"
                                    }
                                },
                                "required": ["symbol"]
                            }
                        }
                    }
                ],
                tool_choice="auto"
            )
            
            # 处理模型响应
            if hasattr(response, 'choices') and len(response.choices) > 0:
                message = response.choices[0].message
                
                # 检查是否需要调用工具
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    # 处理工具调用
                    tool_responses = []
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # 模拟工具调用
                        if function_name == "get_current_weather":
                            tool_result = self._mock_weather_api(function_args)
                        elif function_name == "get_stock_price":
                            tool_result = self._mock_stock_api(function_args)
                        else:
                            tool_result = {"error": "Unknown function"}
                            
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(tool_result)
                        })
                    
                    # 继续对话，将工具返回结果发送给模型
                    messages.extend(tool_responses)
                    second_response = self.client.chat.completions.create(
                        model="glm-4-plus",
                        messages=messages
                    )
                    return second_response.choices[0].message.content
                else:
                    # 直接返回模型回答
                    return message.content
            return None
            
        except Exception as e:
            print(f"智能体对话出错: {str(e)}")
            return None
            
    def _mock_weather_api(self, args: dict) -> dict:
        """模拟天气API"""
        location = args.get('location', '')
        unit = args.get('unit', 'celsius')
        
        return {
            "location": location,
            "temperature": 25 if unit == "celsius" else 77,
            "unit": unit,
            "condition": "晴朗",
            "humidity": 60,
            "wind_speed": 10
        }
        
    def _mock_stock_api(self, args: dict) -> dict:
        """模拟股票API"""
        symbol = args.get('symbol', '')
        
        return {
            "symbol": symbol,
            "price": 100.00,
            "currency": "CNY",
            "change": "+2.5%",
            "volume": 1000000
        }
    

    # 外部使用的时候直接传入model_name, messages即可（默认模型是glm-4-plus）
    


def main():
    # 使用示例
    creator = GLMCreator("")
    
    # # Step 1: 生成图片描述
    # prompt = "一只可爱的猫咪在阳光下玩耍" 
    # description = creator.generate_image_description(prompt)
    # print(f"生成的描述：{description}")
    
    # if description:
    #     # Step 2: 基于描述生成图片
    #     image_url, image_path = creator.text_to_image(description)
    #     print(f"生成的图片URL：{image_url}")
    #     print(f"图片保存路径：{image_path}")
        
    #     # Step 3: 基于描述生��视频
    #     video_url, video_path = creator.text_to_video(description)
    #     print(f"生成的视频URL：{video_url}")
    #     print(f"视频保存路径：{video_path}")
        
    #     # Step 4: 测试视频对话
    #     # video_path = "xxx.mp4"  # 替换为实际视频路径
    #     video_prompt = "请描述这个视频中发生了什么？"
    #     video_response = creator.vision_chat_with_video(video_path, video_prompt)
    #     print(f"视频对话响应：{video_response}")
        
    #     # Step 5: 测试图片对话
    #     # image_path = "xxx.png"  # 替换为实际图片路径
    #     image_prompt = "这张图片中有什么内容？"
    #     image_response = creator.vision_chat_with_image(image_path, image_prompt)
    #     print(f"图片对话响应：{image_response}")

    # 测试 glm-4-plus 的函数调用能力
    agent_prompt = "北京今天的天气怎么样？顺便帮我查询一下阿里巴巴的股票价格。"
    agent_response = creator.agent_chat(agent_prompt)
    print(f"\n(with function call)对话测试：")
    print(f"问题：{agent_prompt}")
    print(f"回答：{agent_response}")

# if __name__ == "__main__":
#     main()


from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)
api_key=os.getenv("ZHIPUAI_API_KEY")
client = zhipuai.ZhipuAI(api_key=api_key)
async def get_model_response_glm(model_name="glm-4-plus", messages=[], temperature=0, tools=None, stop=None, stream=False):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            tools=tools,
            stop=stop,
            stream=stream
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"{model_name}生成出错: {str(e)}")
        return None



if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试基本对话功能
        messages = [
            {"role": "user", "content": "你好，请介绍一下你自己"},
            {"role": "assistant", "content": "我是一个AI助手"},
            {"role": "user", "content": "总结一下我们的对话"}
        ]
        
        try:
            response = await get_model_response_glm(
                model_name="glm-4-plus",
                messages=messages
            )
            print("\n=== GLM-4 测试 ===")
            print(f"输入消息: {messages[-1]['content']}")
            print(f"模型回复: {response}")
            
        except Exception as e:
            print(f"测试出错: {str(e)}")
    
    asyncio.run(test())

