# -*- coding: utf-8 -*-
import os
import asyncio
from openai import AsyncOpenAI
from openai import OpenAI


async def get_client():
    return AsyncOpenAI(
        api_key="sk-65742e37656f4f3b8543e15d44ffa8c2",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


query = "9.8和9.11谁大"
messages=[{"role": "user", "content": query}]

async def r1_model(history_message=""):
    """专业的报告撰写和解决复杂问题的深度推理专家。
    1. 基于参考内容撰写专业深度报告
    2. 基于参考内容进行深度推理并解决问题

    Args:
        history_message (str): 历史对话信息

    Returns:
        str: 最终的输出内容。如果是报告任务，返回结构化的专业报告；
            如果是推理任务，返回经过深入分析的解决方案。
    """
    prompt=f"""
你是一个具有深度洞察力的分析师，可以根据某些历史对话信息，深入挖掘深刻的观点，最终形成专业的报告或者回答用户复杂的问题。

历史对话信息:
{history_message}

回答最好以markdown格式输出。
"""
    
    is_answering = False  
    messages=[{"role":"user", "content":prompt}] 

    client = await get_client()
    stream = await client.chat.completions.create(
        model="deepseek-r1",  
        messages=messages,
        stream=True
    )

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    content, reasoning_content = "", ""
    async for chunk in stream:
        delta = chunk.choices[0].delta

        if not hasattr(delta, 'reasoning_content'):
            continue
        if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
            continue

        if not getattr(delta, 'reasoning_content', None) and not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            is_answering = True

        if getattr(delta, 'reasoning_content', None):
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
            
        elif getattr(delta, 'content', None):
            print(delta.content, end='', flush=True)
            content += delta.content
    return content

async def test_r1():
    history_message = """为了全面评估《哪吒2》的票房潜力，我将按照以下步骤进行分析：
步骤1：确认电影基本信息与市场预热状态
我将使用【searchall】工具搜索《哪吒2》的上映时间、制作团队及前期宣传情况，以了解电影的基本信息和市场预热状态。

<CALL_TOOL>searchall: {"query": "哪吒2上映时间、制作团队及前期宣传情况"}</CALL_TOOL>
<TOOL_RES>[有用的信息]
1. 上映时间：《哪吒2》密钥延期延长上映至3月30日。
2. 制作团队：《哪吒2》幕后有超过4000人的创作团队，包括上海温哥华电影学院校友侯广域等。全片镜头量超过2400个，特效镜头数量超过1900个，超过百家国内动画团队参与制作。
3. 前期宣传：成都天府长岛数字文创园是《哪吒2》的“诞生地”，主创团队所在的成都可可豆动画影视有限公司门口有许多粉丝与巨幅哪吒IP宣传画合影，电影粉丝络绎不绝前来打卡。
</TOOL_RES>
 
已经解决了步骤1，接下来进行步骤2。

步骤2：分析前作《哪吒之魔童降世》的票房表现与市场反响
为了评估《哪吒2》的票房潜力，我需要了解其前作《哪吒之魔童降世》的票房表现和市场反响。这将帮助我预测《哪吒2》的市场表现。
<TOOL_RES>[有用的信息]
1. 《哪吒之魔童降世》总票房突破80亿大关，登顶中国影史冠军，改写了商业电影的游戏规则，并折射出中国文化产业的深层变革。
2. 《哪吒之魔童降世》的票房奇迹仍在记忆里翻涌，首日预售即突破8000万，院线排片占比超35%，这部脱胎于传统IP的动画电影，正在搅动观众的观影热情和资本市场。
3. 《哪吒之魔童降世》票房突破50亿大关，成为中国影史票房亚军，刷新了动画电影的票房纪录，标志着中国文化市场迎来历史性拐点。
4. 《哪吒之魔童闹海》票房已突破百亿，成为我国影史首部百亿元票房影片，延续了前作《哪吒之魔童降世》的票房热度，维持了其在主流评论平台的高评分、高口碑态势。
</TOOL_RES>
 
已经执行内容:我已经解决了步骤2，接下来进行步骤3。
步骤3：评估当前市场环境与竞争态势
为了进一步评估《哪吒2》的票房潜力，我需要了解当前电影市场的整体环境以及同期上映的其他竞争影片。这将帮助我判断《哪吒2》在市场中的竞争力和吸引力。

<CALL_TOOL>searchall: {"query": "当前电影市场环境及同期上映的竞争影片"}</CALL_TOOL>
<TOOL_RES>[有用的信息]
1. 2024年中国电影总票房达到425.02亿元，但同比下降了23%，观影总人次为10.1亿，较2023年同期的13亿有所减少。这表明观众消费趋于理性，对影片质量等需求有所调整，导致市场规模出现下滑。
2. 电影市场竞争激烈，头部影片的影响力逐渐减弱，导致轻频观众的观影意愿不高。同时，随着流媒体服务和短视频应用的普及，观众更倾向于在家观看视频，尤其是年轻一代。
3. 2023年中国“十一”黄金周电影市场以总票房累计27.34亿收尾，超去年同期83%，总观影人次超6511.4万，同比增长80%。这表明切中社会话题、提供情绪价值的影片成为当下电影市场的主流审美。
4. 传统院线电影发展正从“增量时代”向“存量时代”迈进，尽管银幕数量、影院数量不断增加，但平均电影的上座率仍在下降，显示出观众在市场里的话语权将前所未有地提升。
</TOOL_RES>
 
  
已经执行内容:我已经解决了步骤3，接下来进行步骤4。
步骤4：综合分析与预测《哪吒2》的票房表现
基于以上步骤收集的信息，我将综合分析《哪吒2》的票房潜力。以下是主要分析点：
1. 前作表现：《哪吒之魔童降世》取得了巨大的票房成功，总票房突破80亿，成为中国影史冠军。这表明《哪吒》系列具有强大的市场吸引力和观众基础。
2. 制作团队与宣传：《哪吒2》的制作团队规模庞大，特效镜头数量众多，显示出高水平的制作质量。前期宣传也取得了良好的效果，粉丝热情高涨。
3. 市场环境：当前电影市场整体环境较为复杂，观众消费趋于理性，对影片质量要求提高。同时，流媒体和短视频的普及也对传统院线电影产生了一定的冲击。
4. 竞争态势：虽然市场竞争激烈，但《哪吒2》作为一部备受期待的续集，凭借其前作的口碑和粉丝基础，仍然具有较强的竞争力。
综合以上因素，预计《哪吒2》的票房表现将保持强劲，但可能难以超越前作的辉煌成绩。具体票房预测需要进一步的数据分析和市场调研。

步骤5：撰写最终报告
基于以上分析，我将使用【r1_model】工具撰写一份详细的票房预测报告。"""



    
    result2 = await r1_model(history_message=history_message)
    print(f"结果：{result2}")

if __name__ == "__main__":
    asyncio.run(test_r1())



