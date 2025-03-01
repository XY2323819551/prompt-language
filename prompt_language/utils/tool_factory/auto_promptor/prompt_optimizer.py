from openai import OpenAI
import re

prompt_rules = '''
• 策略一：给出明确的指示                                                                                     
       • 角色扮演: 明确指定 AI 在当前任务中扮演的角色。                                                          
       • 格式规范: 明确规定输出内容的格式、长度和风格。                                                          
       • 示例提供: 提供具体的例子，精确展示期望的结果。                                                          
    • 策略二：提供优质参考资料                                                                                   
       • 明确引用: 指示 AI 参考你提供的资料生成回复。                                                            
       • 引用来源: 要求 AI 在回复中引用参考资料的内容。                                                          
       • 权威性: 优先使用权威的信息来源，减少错误。                                                              
    • 策略三：大任务化小，分步完成                                                                               
       • 分解任务: 明确完整回答请求所需的关键步骤或组成部分。                                                    
       • 逐个提示: 针对每个子任务给出单独的输入提示。                                                            
       • 结果串联: 将前一步的输出用作后一步的输入。                                                              
    • 策略四：让模型 "展示工作"，迭代优化                                                                        
       • 逐步解释: 要求模型在给出最终答案前，逐步解释推理过程。                                                  
       • 自我检查: 提示模型检查自己的工作，找出可能遗漏的要点。
'''
prompt_rules = '''
## 4.1 skill1—保持清晰、具有上下文和具体

- 给 LLM大模型 提供上下文信息： 就像你在了解更多上下文的情况下可能会更好地完成任务一样，LLM大模型 在有更多上下文信息的情况下也会表现得更好。上下文信息的一些例子：
  - 任务结果将用于什么
  - 输出内容面向什么受众
  - 任务属于什么工作流程，以及这个任务在工作流程中的位置
  - 任务的最终目标，或者成功完成任务是什么样子
- 具体说明你想要 LLM大模型 做什么： 例如，如果你只想要 LLM大模型 输出代码而不要其他内容，就要明确说明。
- 按顺序提供指示： 使用编号列表或项目符号，以更好地确保 LLM大模型 按照你想要的方式执行任务。

**examples1**

```Bash
【角色】
用户

【不清晰的提示】
用户请从这些客户反馈信息中删除所有可识别个人身份的信息：{{FEEDBACK_DATA}}

【不清晰的模型回复】
以下是匿名化的客户反馈信息：
1. 我使用你们的软件已经很多年了，一直都很好。但最近，AcmeCloud 经常崩溃。请修复它！
2. XXX，你们的客服代表非常有帮助。他指导我完成了整个过程。我的邮箱是 XXX，如果你们想发送调查。
3. 我是 John Smith，我很不高兴。我已经等了2小时想联系到 XXX。这是不可接受的
【角色】
用户

【清晰的提示】
你的任务是为我们的季度审查匿名化客户反馈。

指示：
1. 将所有客户姓名替换为”CUSTOMER_[ID]“（例如，“Jane Doe” → “CUSTOMER_001”）
2. 将电子邮件地址替换为”EMAIL_[ID]@example.com”
3. 将电话号码编辑为”PHONE_[ID]“
4. 如果信息中提到特定产品（如”AcmeCloud”），保持不变
5. 如果没有发现个人身份信息，逐字复制信息
6. 仅输出处理后的信息，用”---“分隔

要处理的数据：{{FEEDBACK_DATA}}



【清晰的模型回复】
CUSTOMER_001：我使用你们的软件已经很多年了，一直都很好。但最近，AcmeCloud 经常崩溃。请修复它！
---
CUSTOMER_002：CUSTOMER_SERVICE_001，你们的客服代表非常有帮助。他指导我完成了整个过程。我的邮箱是 EMAIL_002@example.com，如果你们想发送调查。
---
CUSTOMER_003：我是 CUSTOMER_003，我很不高兴。我已经等了2小时想联系到 PHONE_001。这是不可接受的！
```

## 4.2 skill3—让 LLM大模型 思考（思维链提示）以提高性能

在面对研究、分析或问题解决等复杂任务时，给 LLM大模型 思考的空间可以显著提高其表现。这种被称为思维链（CoT）提示的技术，鼓励 LLM大模型 逐步分解问题，从而产生更准确和细致的输出。

### **为什么要让 LLM大模型 思考？**

- 准确性： 逐步解决问题可以减少错误，尤其是在数学、逻辑、分析或一般复杂任务中。
- 连贯性： 结构化思维可以产生更连贯、组织更完善的回答。
- 调试： 查看 LLM大模型 的思维过程有助于你找出提示可能不清晰的地方。

### **为什么不让 LLM大模型 思考？**

- 增加输出长度可能影响延迟。
- 并非所有任务都需要深入思考。明智地使用思维链，以确保性能和延迟之间的适当平衡。

### 如何提示思考

以下思维链技术按从简单到复杂的顺序排列。较简单的方法在上下文窗口中占用较少空间，但通常功能也较弱。

思维链提示： 始终让 LLM大模型 输出其思考过程。如果不输出思维过程，就不会发生思考！

- 基本提示： 在提示中包含”逐步思考”。
  - 缺乏关于*如何*思考的指导（如果任务特别针对你的应用、用例或组织，这尤其不理想）
- 示例：撰写捐赠者邮件（基本思维链）

| 角色 | 内容                                                         |
| ---- | ------------------------------------------------------------ |
| 用户 | 起草个性化邮件，向捐赠者请求为今年的关爱儿童计划捐款。  项目信息： <program>{{PROGRAM_DETAILS}} </program>  捐赠者信息： <donor>{{DONOR_DETAILS}} </donor>  在写邮件之前逐步思考。 |

- 引导式提示： 为 LLM大模型 的思维过程列出具体步骤。
  - 缺乏结构化，难以剥离和分离答案与思考过程。
- 示例：撰写捐赠者邮件（引导式思维链）

| 角色 | 内容                                                         |
| ---- | ------------------------------------------------------------ |
| 用户 | 起草个性化邮件，向捐赠者请求为今年的关爱儿童计划捐款。  项目信息： <program>{{PROGRAM_DETAILS}} </program>  捐赠者信息： <donor>{{DONOR_DETAILS}} </donor>  在写邮件之前先思考。首先，根据这位捐赠者的捐赠历史和他们过去支持过的活动，思考什么信息可能会吸引他们。然后，根据他们的历史，思考关爱儿童计划的哪些方面会吸引他们。最后，使用你的分析写出个性化的捐赠者邮件。 |

- 结构化提示： 使用像 `<thinking>` 和 `<answer>` 这样的 XML 标签来分离推理和最终答案。
- 示例：撰写捐赠者邮件（结构化引导思维链）

| 角色 | 内容                                                         |
| ---- | ------------------------------------------------------------ |
| 用户 | 起草个性化邮件，向捐赠者请求为今年的关爱儿童计划捐款。  项目信息： <program>{{PROGRAM_DETAILS}} </program>  捐赠者信息： <donor>{{DONOR_DETAILS}} </donor>  在写邮件之前，在 <thinking> 标签中思考。首先，根据这位捐赠者的捐赠历史和他们过去支持过的活动，思考什么信息可能会吸引他们。然后，根据他们的历史，思考关爱儿童计划的哪些方面会吸引他们。最后，在 <email> 标签中使用你的分析写出个性化的捐赠者邮件。 |

## 4.3 skill4—使用XML标签构建你的提示

当你的提示包含多个组件(如上下文、指令和示例)时，XML标签可以成为改变游戏规则的工具。它们帮助LLM大模型更准确地解析你的提示，从而产生更高质量的输出。

### 为什么使用XML标签？

- 清晰度： 清晰地分隔提示的不同部分，确保提示结构良好。
- 准确性： 减少因LLM大模型误解提示部分而导致的错误。
- 灵活性： 无需重写所有内容即可轻松查找、添加、删除或修改提示的部分。
- 可解析性： 让LLM大模型在输出中使用XML标签，使得通过后处理更容易提取其响应的特定部分。

LLM大模型并没有被特别训练使用某些”最佳”的标准XML标签，不过我们建议你的标签名称要与它们所包含的信息相符。

### 标签使用最佳实践

1. 保持一致性：在整个提示中使用相同的标签名称，并在谈论内容时引用这些标签名称（例如，`使用<contract>标签中的合同...`）。
2. 嵌套标签：对于层级内容，你应该嵌套标签`<outer><inner></inner></outer>`。

高级用户提示：将XML标签与其他技术结合使用，如多示例提示（`<examples>`）或思维链（`<thinking>`、`<answer>`）。这将创建超结构化的高性能提示。

### 示例：法律合同分析

没有XML标签时，LLM大模型的分析杂乱无章且遗漏关键点。使用标签后，它提供了一个法律团队可以采取行动的结构化、全面的分析。

| 角色 | 无XML标签                                                    | 使用XML标签                                                  |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 用户 | 分析这份软件许可协议的潜在风险和责任：{{CONTRACT}}。重点关注赔偿、责任限制和知识产权所有权条款。另外，注意任何不寻常或令人担忧的条款。这是我们的标准合同供参考：{{STANDARD_CONTRACT}}。为我们的法律团队提供调查结果和建议的总结。 | 分析这份软件许可协议的法律风险和责任。  我们是一家考虑将此协议用于核心数据基础设施的跨国企业。  <agreement> {{CONTRACT}}</agreement>  这是我们的标准合同供参考： <standard_contract>{{STANDARD_CONTRACT}}</standard_contract>  <instructions> 1. 分析这些条款： - 赔偿 - 责任限制 - 知识产权所有权  2. 注意不寻常或令人担忧的条款。  3. 与我们的标准合同进行比较。  4. 在<findings>标签中总结调查结果。  5. 在<recommendations>标签中列出可行的建议。</instructions> |
| 助手 | 提供的软件许可协议存在几个令人担忧的方面。赔偿条款过于宽泛，可能使我们面临重大责任。责任限制部分将损害赔偿上限设定为仅500美元，这对于我们的企业级使用来说是不够的。关于知识产权，该协议授予供应商对我们创建的任何修改或集成的共同所有权。  总之，这份协议不符合我们的最佳利益。它使我们面临不当风险，限制了我们在发生故障时的追索权，并损害了我们的知识产权。我建议重新谈判这些条款或寻找替代供应商。 | <findings> 1. 赔偿（第8条）： - 问题：过于宽泛。我们需要对”任何和所有索赔”进行赔偿。 - 风险：即使是供应商的疏忽或产品缺陷也可能使我们承担责任。 - 偏差：我们的标准合同将赔偿限制在因我们违反协议而产生的索赔。  2. 责任限制（第9条）： - 问题：将所有损害赔偿（包括直接损害）上限设为500美元。 - 风险：对企业使用来说严重不足。关键故障可能造成数百万美元损失。 - 偏差：我们的标准允许直接损害赔偿最高达已付费用的12个月。  3. 知识产权所有权（第12条）： - 问题：授予供应商对我们的修改/集成的共同所有权。 - 风险：供应商可能使用或出售我们的专有算法或数据洞察。 - 偏差：我们的标准保留对我们工作的完全所有权。  4. 不寻常条款： - 第5.3条：供应商可以”出于任何目的”使用我们的使用数据。 - 第7.2条：供应商可以仅提前7天通知就”随意”终止。 - 第11条：不提供任何保证，即使是基本的适销性保证。 </findings>  <recommendations> 1. 拒绝这份协议。对企业来说风险远大于收益。 2. 提出反建议： - 赔偿：限制在因我们违反协议而产生的索赔。 - 责任：直接损害上限为12个月费用；就间接损害进行谈判。 - 知识产权：对我们的修改/集成拥有完全所有权。 - 数据使用：仅限于服务改进。 - 终止：最少90天通知；仅限有因终止。 - 保证：要求基本的适销性和适用性保证。 3. 如果供应商拒绝，探索替代供应商或内部解决方案。 4. 鉴于风险较高，聘请法律顾问进行合同谈判。 </recommendations> |

## 4.4 skill5—通过系统提示给LLM大模型分配角色

在使用LLM大模型时，您可以通过使用`system`参数给它分配角色来显著提升其表现。这种技术被称为角色提示，是使用系统提示与LLM大模型交互的最有效方式。

合适的角色可以将LLM大模型从一个通用助手转变为您的虚拟领域专家！

系统提示技巧：使用`system`参数来设置LLM大模型的角色。将其他所有内容（如特定任务的指令）放在`user`轮次中。

### 为什么要使用角色提示？

- **提高准确性：** 在法律分析或财务建模等复杂场景中，角色提示可以显著提升LLM大模型的表现。
- **定制语气：** 无论您需要CFO的简洁还是文案撰写人的文采，角色提示都可以调整LLM大模型的沟通风格。
- **提升专注度：** 通过设置角色背景，LLM大模型能更好地保持在您任务特定要求的范围内。

## 4.5 skill6—预填充LLM大模型的回复以获得更好的输出控制

在使用LLM大模型时，您可以通过预填充`Assistant`消息来引导其回复。这种强大的技术允许您指导LLM大模型的行为，跳过前言，强制使用特定格式如JSON或XML，甚至帮助LLM大模型在角色扮演场景中保持角色一致性。

在某些LLM大模型表现不如预期的情况下，预填充几句话就能大大改善LLM大模型的表现。一点预填充就能产生很大的影响！

### 如何预填充LLM大模型的回复

要进行预填充，请在`Assistant`消息中包含所需的初始文本（LLM大模型的回复将从`Assistant`消息结束的地方继续）

### 示例

#### 示例1：控制输出格式并跳过前言

高级用户提示：预填充`{`强制LLM大模型跳过前言并直接输出JSON对象。这样更简洁、更清晰，也更容易被程序解析而无需额外处理。

示例：不使用预填充的结构化数据提取

| 角色      | 内容                                                         |
| --------- | ------------------------------------------------------------ |
| User      | 从这个产品描述中提取名称、尺寸、价格和颜色作为JSON对象：  <description> SmartHome Mini是一款紧凑型智能家居助手，有黑色和白色可选，售价仅为$49.99。宽度仅5英寸，无论您将其放在家中何处，都可以通过语音或应用程序控制灯光、恒温器和其他连接设备。这款价格实惠的小型集线器为您的智能设备带来便捷的免提控制。 </description> |
| Assistant | 以下是JSON格式的提取信息：  ```json { “name”: “SmartHome Mini”, “size”: “5 inches wide”, “price”: “$49.99”, “colors”: [“black”, “white”] } ```  我从产品描述中提取了以下详细信息： - 名称：SmartHome Mini - 尺寸：宽5英寸 - 价格：$49.99 - 颜色：有黑色和白色可选  JSON对象提供了一个易于程序解析和使用的结构化格式。如果您需要任何修改或有其他问题，请告诉我！ |

示例：使用预填充的结构化数据提取

| 角色                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| User                     | 从这个产品描述中提取名称、尺寸、价格和颜色作为JSON对象：  <description> SmartHome Mini是一款紧凑型智能家居助手，有黑色和白色可选，售价仅为$49.99。宽度仅5英寸，无论您将其放在家中何处，都可以通过语音或应用程序控制灯光、恒温器和其他连接设备。这款价格实惠的小型集线器为您的智能设备带来便捷的免提控制。 </description> |
| Assistant (预填充)       | {                                                            |
| Assistant (LLM大模型的回复) | “name”: “SmartHome Mini”, “size”: “5 inches wide”, “price”: “$49.99”, “colors”: [ “black”, “white” ] } |

#### 示例2：在角色扮演场景中保持角色

角色扮演提示：预填充一个方括号中的`[角色名称]`可以提醒LLM大模型保持角色，即使在更长和更复杂的对话中也是如此。当与`system`参数中的角色提示结合使用时，这种方法特别有效。

示例：不使用角色提示保持角色

| 角色                                         | 内容                                                         |
| -------------------------------------------- | ------------------------------------------------------------ |
| User (与”夏洛克·福尔摩斯”LLM大模型的第50轮对话) | 你能从这只鞋子推断出什么关于它的主人？<image>muddy_shoe.jpg</image> |
| Assistant                                    | 作为一个AI助手，我很乐意分析这张泥泞鞋子的图片，就好像您提供了它一样。以下是我的推断… |

示例：使用角色提示保持角色

| 角色                                         | 内容                                                         |
| -------------------------------------------- | ------------------------------------------------------------ |
| User (与”夏洛克·福尔摩斯”LLM大模型的第50轮对话) | 你能从这只鞋子推断出什么关于它的主人？ <image>muddy_shoe.jpg</image> |
| Assistant (预填充)                           | [夏洛克·福尔摩斯]                                            |
| Assistant (LLM大模型的回复)                     | 啊，这里有什么？华生，这是一个非常有趣的样本！让我们用敏锐的眼光来检查这只鞋子。你看，这泥土不是普通的伦敦粘土，而是具有汉普斯特德希思特有的富含铁的土壤的独特红色色调。然而，鞋底的磨损痕迹表明，这种步态更适合白教堂的鹅卵石路面，而不是希思公园的缓坡。  现在，观察鞋带！它们打的是医疗专业人员常用的特殊结——毫无疑问是在多年系手术服的过程中养成的习惯。但鞋尖的擦痕讲述了另一个故事：这些痕迹与武术中的踢腿动作一致，特别是巴里兹术。  因此，我们可以得出结论，这只鞋子的主人是一位医生，可能是外科医生，住在白教堂但经常去汉普斯特德希思——也许是为了秘密练习巴里兹术，远离窥探的目光。华生，这是一个非常有趣的案例！我们必须抓紧时间；游戏开始了！ |

## 4.6 skill7— 链式复杂提示以获得更强的性能
'''


client = OpenAI(
    api_key="sk-9efddec830e34a1d915ebb4af09d26fb",
    base_url="https://api.deepseek.com"
)


async def prompt_optimizer(prompt_template="", ans=""):
    """根据提示词优化建议，优化原始的prompt"""

    prompt = f"""你是一位专业的提示词优化专家。你的任务是根据【提示词撰写总则】和【提示词优化建议】，对原始prompt进行系统性优化。

    【提示词撰写总则】：
    {prompt_rules}
    
    【提示词优化建议】：
    {ans}
    
    【原始的prompt】：
    {prompt_template}
    
    请按照以下步骤进行优化：
    1. 分析原始prompt的不足之处
    2. 根据提示词总则中的四大策略逐一思考优化方向
    3. 结合优化建议给出具体的改进方案
    4. 输出最终优化后的prompt
    
    ## 输出格式要求
    1. 思考过程部分，使用<analysis></analysis>标签包裹, 例如：
    <analysis>
    - 【原始prompt分析】
    - 【应用策略说明】
    - 【改进方案阐述】
    </analysis>
    
    2. 优化结果部分：
    使用<optimized_prompt></optimized_prompt>标签包裹优化后的prompt，例如：
    <optimized_prompt>
    作为一位[角色]，你的任务是[任务描述]。
    </optimized_prompt>
    
    目前不要在prompt中填写examples（示例部分）。
    请用中文回答。确保优化后的prompt简洁有力、结构清晰、易于理解。"""

    
    try:
        from prompt_language.utils.model_factory.gemini_model import get_model_response_gemini
        response = await get_model_response_gemini(contents=prompt)
        content = response
    except:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            temperature=0.0,
            max_tokens=2000
        )
        content = response.choices[0].message.content


    match = re.search(r'<optimized_prompt>(.*?)</optimized_prompt>', content, re.DOTALL)
    optimized_prompt = match.group(1) if match else content
    return optimized_prompt


async def main():
    prompt_template = "找出符合条件的人员，回答尽量精炼。问题：{{query}}\n参考信息：{{content}}\n"
    analysis_collections = '''
### 可扩展的建议总结：

1. **明确回答要求**：在提示词中明确要求回答内容要"完整、准确且精炼"，以引导模型全面回答问题。
2. **强调参考资料**：强调模型需要根据参考信息来回答问题，确保回答的准确性。
3. **增加引导性语句**：在提示词中加入一些引导性语句，帮助模型更好地理解问题并提取关键信息。

### 改进原始prompt的建议：

**改进后的提示词**：
```
请根据以下参考信息，找出符合条件的人员，并确保回答内容完整、准确且精炼。问题：{{query}}
参考信息：{{content}}
```

**改进点**：
- **明确要求**：在提示词中明确要求回答内容要"完整、准确且精炼"，以引导模型全面回答问题。
- **强调参考资料**：强调模型需要根据参考信息来回答问题，确保回答的准确性。
- **增加引导**：可以在提示词中加入一些引导性语句，帮助模型更好地理解问题并提取关键信息。

通过以上改进，模型应该能够更准确地输出符合标准答案的回答。
'''
    optimized_prompt = await prompt_optimizer(prompt_template=prompt_template, ans=analysis_collections)
    print(optimized_prompt)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
