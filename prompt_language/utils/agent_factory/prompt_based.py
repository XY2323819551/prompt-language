from prompt_language.utils.model_factory.model_factory import get_model_response


class PromptBasedAgent():
    def __init__(self, tools=None, tool_pool=None):
        self.messages = []

    
    async def generate_content(self):
        response = await get_model_response(
            messages=self.messages,
            stream=True
        )
        async for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    yield content
    
    async def execute(self, task):
        self.messages = [{"role": "system", "content": task}]
        async for content in self.generate_content():
            yield content
        yield "\n"

        while True:
            user_input = input("user: ")
            if user_input.lower() in ["exit", "quit", "q", "e", "quit"]:
                break
            self.messages.append({"role": "user", "content": user_input})
            reply_msg = ""
            async for content in self.generate_content():
                reply_msg += content
                yield content
            yield "\n"
            self.messages.append({"role": "assistant", "content": reply_msg}) 
