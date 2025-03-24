import json
import asyncio
from prompt_language.utils.model_factory.model_factory import get_model_response
from prompt_language.utils.model_factory.deepseek_r1 import get_model_response_r1, get_model_response_r1_static, get_model_response_v3
from prompt_language.utils.func_to_schema import function_to_schema


# dolphin中的prompt
class ExploreAgent():
    def __init__(self, roles=None, tools=None, tool_pool=None):
        self.tool_pool = tool_pool
        self.roles = roles
        self.tools = tools
        self.role = None
        self.add_solution=False
        self.query = ""
        self.kg_schema = {
    "entity": [
        {
            "name": "business",
            "alias": "专业领域",
            "props": [
                {
                    "name": "name",
                    "alias": "name",
                    "data_type": "string",
                    "partial_values": [
                        "产品介绍",
                        "数据资产",
                        "知识网络",
                        "制度规范",
                        "AnyDATA"
                    ]
                }
            ]
        },
        {
            "name": "district",
            "alias": "地区",
            "props": [
                {
                    "name": "parent",
                    "alias": "隶属于",
                    "data_type": "string",
                    "partial_values": [
                        "重庆市",
                        "河北省保定市",
                        "新疆维吾尔自治区",
                        "河北省石家庄市"
                    ]
                },
                {
                    "name": "level",
                    "alias": "层级",
                    "data_type": "integer",
                    "partial_values": [
                        "3",
                        "2",
                        "1"
                    ]
                },
                {
                    "name": "code",
                    "alias": "区划代码",
                    "data_type": "string",
                    "partial_values": [
                        "610925000000",
                        "610600000000",
                        "640200000000",
                        "652826000000",
                        "620524000000"
                    ]
                },
                {
                    "name": "name",
                    "alias": "名称",
                    "data_type": "string",
                    "partial_values": [
                        "市辖区",
                        "鼓楼区",
                        "市中区",
                        "新华区",
                        "省直辖县级行政区划"
                    ]
                }
            ]
        },
        {
            "name": "person",
            "alias": "人员",
            "props": [
                {
                    "name": "english_name",
                    "alias": "英文名",
                    "data_type": "string",
                    "partial_values": [
                        "Jason",
                        "Leo",
                        "Kevin",
                        "Jack"
                    ]
                },
                {
                    "name": "status",
                    "alias": "用户状态",
                    "data_type": "string",
                    "partial_values": [
                        "enabled",
                        "disabled"
                    ]
                },
                {
                    "name": "is_expert",
                    "alias": "专家角色",
                    "data_type": "boolean",
                    "partial_values": [
                        "false",
                        "true"
                    ]
                },
                {
                    "name": "university",
                    "alias": "毕业院校",
                    "data_type": "string",
                    "partial_values": [
                        "[]"
                    ]
                },
                {
                    "name": "email",
                    "alias": "邮箱",
                    "data_type": "string",
                    "partial_values": [
                        "Meya.pan@aishu.cn",
                        "Arnold.hua@aishu.cn",
                        "jin.huihui@aishu.cn",
                        "Chao.Li@aishu.cn"
                    ]
                },
                {
                    "name": "contact",
                    "alias": "联系方式",
                    "data_type": "string",
                    "partial_values": [
                        "13601996899"
                    ]
                },
                {
                    "name": "user_securtiy_level",
                    "alias": "用户密级",
                    "data_type": "integer",
                    "partial_values": [
                        "5"
                    ]
                },
                {
                    "name": "user_role",
                    "alias": "用户角色",
                    "data_type": "string",
                    "partial_values": []
                },
                {
                    "name": "position",
                    "alias": "职位",
                    "data_type": "string",
                    "partial_values": [
                        "技术工程师",
                        "高级技术工程师",
                        "高级后端开发工程师",
                        "高级解决方案顾问"
                    ]
                },
                {
                    "name": "id",
                    "alias": "id",
                    "data_type": "string",
                    "partial_values": [
                        "b7a8903e-d786-11ee-8d78-42a9aad9dca0",
                        "b6b791e6-d535-11ee-a2b0-42a9aad9dca0",
                        "c22ec652-d535-11ee-a2b0-42a9aad9dca0",
                        "dbf4b862-d12a-11ee-9ee9-42a9aad9dca0",
                        "ba0a7018-d786-11ee-8d78-42a9aad9dca0"
                    ]
                },
                {
                    "name": "name",
                    "alias": "姓名",
                    "data_type": "string",
                    "partial_values": [
                        "王磊",
                        "李蓉",
                        "龙文",
                        "余双军",
                        "李超-01"
                    ]
                }
            ]
        },
        {
            "name": "orgnization",
            "alias": "部门",
            "props": [
                {
                    "name": "desc",
                    "alias": "部门职责描述",
                    "data_type": "string",
                    "partial_values": [
                        "负责南区 AnyDATA、AnyFabric 产品的数据治理、知识图谱构建及认知应用开发，持续提升技术能力和服务水平，达成业务目标，实现客户成功和合作伙伴成功。",
                        "负责围绕大数据基础设施战略，基于产品定位开展灾难恢复管理子系统和灾备运营管理子系统规划、研发交付、质量管理、技术赋能，以高价值、高竞争力的产品实现客户成功",
                        "负责华东地区（上海市、江苏省、浙江省、安徽省、福建省）的公共事业行业市场拓展及大客户销售工作，围绕公司发展战略及行业市场发展目标，通过客户经营、销售过程管理落地销售策略，达成销售目标，实现客户成功"
                    ]
                },
                {
                    "name": "parent",
                    "alias": "隶属于",
                    "data_type": "string",
                    "partial_values": [
                        "aishu.cn",
                        "aishu.cn/aishu",
                        "aishu.cn/aishu/外部用户",
                        "aishu.cn/aishu/大客户销售体系",
                        "aishu.cn/aishu/大客户销售体系/系统行业大客户销售线"
                    ]
                },
                {
                    "name": "email",
                    "alias": "邮箱",
                    "data_type": "string",
                    "partial_values": []
                },
                {
                    "name": "id",
                    "alias": "id",
                    "data_type": "string",
                    "partial_values": [
                        "2e7ee324-d535-11ee-a2b0-42a9aad9dca0",
                        "2b16eff6-d535-11ee-a2b0-42a9aad9dca0",
                        "2ee1cc50-d535-11ee-a2b0-42a9aad9dca0",
                        "735389be-2463-11ef-a0ef-fe611520b6e4",
                        "2eafd0ce-d535-11ee-a2b0-42a9aad9dca0"
                    ]
                },
                {
                    "name": "name",
                    "alias": "名称",
                    "data_type": "string",
                    "partial_values": [
                        "存储测试组",
                        "系统测试部",
                        "引擎研发部",
                        "北区企业数据智能方案部",
                        "引擎测试组"
                    ]
                }
            ]
        },
        {
            "name": "project",
            "alias": "项目",
            "props": [
                {
                    "name": "name",
                    "alias": "名称",
                    "data_type": "string",
                    "partial_values": []
                }
            ]
        }
    ],
    "edge": [
        {
            "name": "person_2_business_belong_to",
            "alias": "擅长领域",
            "subject": "person",
            "object": "business",
            "description": "人员-擅长领域->专业领域"
        },
        {
            "name": "district_2_district_child",
            "alias": "下级地区",
            "subject": "district",
            "object": "district",
            "description": "地区-下级地区->地区"
        },
        {
            "name": "person_2_district_work_at",
            "alias": "工作地点",
            "subject": "person",
            "object": "district",
            "description": "人员-工作地点->地区"
        },
        {
            "name": "person_2_project_join",
            "alias": "负责项目",
            "subject": "person",
            "object": "project",
            "description": "人员-负责项目->项目"
        },
        {
            "name": "person_2_orgnization_belong_to",
            "alias": "所在部门",
            "subject": "person",
            "object": "orgnization",
            "description": "人员-所在部门->部门"
        },
        {
            "name": "orgnization_2_orgnization_child",
            "alias": "子部门",
            "subject": "orgnization",
            "object": "orgnization",
            "description": "部门-子部门->部门"
        }
    ]
}
    
    async def init(self):
        """异步初始化方法"""
        bambo_role = await self.get_role()
        self.roles_info = ""
        for key, value in self.roles.items():
            self.roles_info += f"@{key}: {value}\n"
        
        self.tools, self.tool_describe = await self._transfer_func_info()
        self.role = bambo_role.replace(r"{roles}", self.roles_info).replace(r"{tools}", "".join(self.tool_describe))

    async def _transfer_func_info(self):
        """异步方法处理工具信息"""
        format_tools, tool_describe = {}, []
        for tool_name in self.tools:
            tool = await self.tool_pool.get_tool(tool_name)
            format_tools[tool_name] = tool

            tool_schema = function_to_schema(tool)
            required_paras = tool_schema["function"]["parameters"]["required"]
            desc = {}
            for para in required_paras:
                para_desc = tool_schema["function"]["parameters"]["properties"][para]["description"]
                desc.update({para: para_desc})
            tool_desc = tool_schema["function"]["description"] + "\n" + "参数:\n" + json.dumps(desc, ensure_ascii=False)
            tool_describe.append(f"{tool_name}: {tool_desc}\n")
        return format_tools, tool_describe

    async def get_r1_plan_prompt(self):
        return """
你是一个任务规划师，你会根据用户的问题和当前拥有的工具，将用户的复杂问题拆分为尽可能简单的子问题。
你拆分子问题是有依据的，你会根据图谱的schema来对原问题进行拆分，尽可能一个子问题对应一个三元组，通过逐步解决子问题，最终综合得出原始问题的答案。请给出关键步骤。最终结果仅仅输出解决问题的步骤即可，按条罗列。
你解决问题的过程中尽可能使用工具。

用户的问题为：
当前问题为：{origin_query}\n\n

你拥有的工具信息为:
{tools}

图谱的schema为：
{kg_schema}

注意：
(1)工具名称一定要和工具信息中的名称一致。
(2)当前世界时间2025年2月。

Examples:
示例1: xxx所在的组还有谁
分析: 要想知道xxx所在的组还有谁，我们必须先知道xxx在哪个组，然后再查询该组有哪些人。所以应该分为两个查询子问题。先查询xxx在哪个组，再查询该组有哪些人（查询之前需要调用重写工具重写query）

示例2: AnyDATA模型工厂研发部开发、测试和算法分别有多少人
分析：AnyDATA模型工厂研发部有可能是个大部门，所以我们要先知道AnyDATA模型工厂研发部包含了哪些子部门，再知道这些子部门都有谁，最后根据找到的信息回答问题。(回答下一个子问题之前需要根据上下文决定是否调用重写工具）
 
"""

    async def get_role(self):
        job_describe = """
# Role: 团队负责人

# Profile:
- language: 中文
- description: 你是一个团队负责人，善于使用工具，利用工具的结果解决用户的复杂问题，你有很多的工具可以使用。

## Goals：
- 你需要按照Constraints、system Workflows、执行步骤中的要求和限制来解决用户问题。tools中的工具就是你可以使用的全部工具。

## tools:
{tools}

## Constraints：
- 你必须清晰的理解问题和执行步骤，并熟练使用工具。
- 你需要逐步执行【执行步骤】中的规划。
- 当需要调用工具的时候，你需要使用"<CALL_TOOL>tool_name: {key:value}</CALL_TOOL>"的格式来调用工具,其中参数为严格的json格式，例如"<CALL_TOOL>=>#send_email: {subject: 'Hello', content: 'This is a test email'}</CALL_TOOL>"。

## system Workflows：
- 分析用户问题，如果当前问题可以使用工具解决则优先调用工具解决，否则你自己回答。
- 如果需要调用工具来处理，需要使用以下符号进行触发："<CALL_TOOL>tool_name: {key:value}</CALL_TOOL>"，例如"<CALL_TOOL>send_email: {subject: 'Hello', content: 'This is a test email'}</CALL_TOOL>"。
- 每一次触发了不同的tool之后，你需要停止作答，等待用户调用对应的tool处理之后，将tool的结果重新组织语言后再继续依照【执行步骤】中的规划作答(tool的结果格式为<TOOL_RES>tool的结果</TOOL_RES>)
- 新的答案要接着"</TOOL_RES>"后继续生成结果，要保持结果通顺，衔接词可以是：我已经解决了步骤1，接下来还行步骤2...。


## 目标问题
当前问题为：{origin_query}\n

## 执行步骤:
<SOLUTIONS>
{solutions}
</SOLUTIONS>

## 问题解决进展
{prompt}
"""
        return job_describe

    async def params_extract(self, params_content):
        stack = 0
        params_content = params_content.strip()
        if params_content[0] != "{":
            raise Exception("params_content extract error, can not be parsed to json")
        json_end = 0
        for index, char in enumerate(params_content):
            if char == "{":
                stack += 1
            elif char == "}":
                stack -= 1
            if stack == 0:
                json_end = index + 1
                break
        return json.loads(params_content[:json_end+1])
    
    async def tool_run(self, tool_message):
        function_name, function_params = tool_message.split(":", 1)
        # code_tool需要特殊处理以保持历史上下文
        if "code_" in function_name.strip():
            try:
                result = await self.tools[function_name](history_message=self.query)
                return str(result)
            except Exception as e:
                return f"代码执行错误: {str(e)}"
        elif "r1_model" in function_name.strip():
            breakpoint()
            try:
                result = await self.tools[function_name](history_message=self.query)
                return str(result)
            except Exception as e:
                return f"代码执行错误: {str(e)}"
        
        # 其他工具的常规处理
        function_params = await self.params_extract(function_params)
        param_values = list(function_params.values())
        if "query_rewrite" in function_name.strip():
            result = await self.tools[function_name](*param_values, history_message=self.query)
        else:
            result = await self.tools[function_name](*param_values)
        return str(result)

    
    async def execute(self, query):
        self.query = query
        if not self.add_solution:
            planner_prompt = await self.get_r1_plan_prompt()
            planner_prompt = planner_prompt.replace(r"{kg_schema}", str(self.kg_schema))
            planner_prompt = planner_prompt.replace(r"{tools}", "".join(self.tool_describe))
            planner_prompt = planner_prompt.replace(r"{origin_query}", query).strip()
            messages = [
                {"role": "user", "content": planner_prompt}
            ]
            solutions = await get_model_response_r1_static(messages)

            # 修复替换顺序问题
            prompt = self.role
            prompt = prompt.replace("{origin_query}", query)
            prompt = prompt.replace("{solutions}", solutions)
            prompt = prompt.replace("{prompt}", query)
            prompt = prompt.strip()
            self.add_solution = True
            print("\n\n")
        else:
            prompt = self.role.replace("{prompt}", query).strip()

        messages = [{"role": "user", "content": prompt}]

        all_answer = ""
        query_params = ""
        tool_Flag = False
        # breakpoint()
        async for chunk in get_model_response_v3(messages=messages):
            all_answer += chunk.choices[0].delta.content
            if tool_Flag:
                query_params += chunk.choices[0].delta.content
                if "</CALL_TOOL>" in all_answer:
                    yield query_params + "\n"
                    break
                continue
            if ":" in chunk.choices[0].delta.content and "<CALL_TOOL>" in all_answer:
                tool_Flag = True
                # tool_messages += chunk.choices[0].delta.content
                if chunk.choices[0].delta.content == ":":
                    yield ": "
                else:
                    yield chunk.choices[0].delta.content
                continue
            yield chunk.choices[0].delta.content
        
        if tool_Flag:
            # 使用正则表达式提取<CALL_TOOL>和</CALL_TOOL>之间的内容
            import re
            pattern = r'<CALL_TOOL>(.*?)</CALL_TOOL>'
            match = re.search(pattern, all_answer)
            # breakpoint()
            if match:
                tool_messages = match.group(1)

            self.query = query + "\n" + all_answer
            result = await self.tool_run(tool_message=tool_messages)
            yield "<TOOL_RES>"
            for item in str(result):
                yield item
            yield "</TOOL_RES>"
            query = query + "\n" + "已经执行内容:" + all_answer + "\n" + "工具执行结果:" + "<TOOL_RES>" + result + "/<TOOL_RES>"
            # breakpoint()
            async for item in self.execute(query=query):
                yield item

