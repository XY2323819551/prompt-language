import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

async def dict_to_multiline_string(d, indent=0):
    result = ""
    for key, value in d.items():
        if isinstance(value, dict):  # 如果值是字典，递归处理
            inner = await dict_to_multiline_string(value, indent + 4)
            result += " " * indent + f"{key}:\n" + inner
        else:  # 否则直接添加键值对
            result += " " * indent + f"{key}: {value}\n"
    return result

async def send_email(content="", subject="", to_addrs="xyzhang290@gmail.com"):
    # Set up the SMTP server
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # 修改为SSL端口465
    smtp_username = "2323819551@qq.com"
    smtp_password = os.getenv("QQAYTHORIZATIONCODE")  # 从.env文件中读取QQ邮箱授权码
    if not smtp_password:
        raise ValueError("未找到QQ邮箱授权码，请检查.env文件中的QQAYTHORIZATIONCODE配置")
    
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = ""
    msg['Subject'] = subject
    if isinstance(content, dict):
        content = await dict_to_multiline_string(content, 0)
    elif isinstance(content, list):
        content = "[" + "\n".join(content) + "\n]" 
    else:
        content = str(content)
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    try:
        # 连接 SMTP 服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用 SSL 加密
        server.login(smtp_username, smtp_password)  # 登录邮箱
        server.sendmail(from_addr=smtp_username, to_addrs=to_addrs, msg=msg.as_string())  # 发送邮件
        print("邮件发送成功！")
        return f"Send email to {to_addrs} successfully"
    except smtplib.SMTPException as e:
        print(f"邮件发送失败：{e}")
        return "failed"
    finally:
        server.quit()

if __name__ == '__main__':
    import asyncio
    content = """
    '```json\n{\n    "推荐阅读内容和顺序": [\n        "ConQRet: Benchmarking Fine-Grained Evaluation of Retrieval Augmented Argumentation with LLM Judges",\n        "DEMO: Reframing Dialogue Interaction with Fine-grained Element Modeling",\n        "Stag-1: Towards Realistic 4D Driving Simulation with Video Generation Model",\n        "TeamCraft: A Benchmark for Multi-Modal Multi-Agent Systems in Minecraft",\n        "MixedGaussianAvatar: Realistically and Geometrically Accurate Head Avatar via Mixed 2D-3D Gaussian Splatting"\n    ],\n    "参考论文总结": {\n        "LLM": "在LLM领域，有两篇论文值得关注。第一篇是\'ConQRet: Benchmarking Fine-Grained Evaluation of Retrieval Augmented Argumentation with LLM Judges\'，该论文介 
绍了ConQRet基准，用于评估检索增强论证的细粒度评估，并提出了使用多个细粒度LLM法官的自动化评估方法。第二篇是\'DEMO: Reframing Dialogue Interaction with Fine-grained Element Modeling\'，该论文提出了对话元素建模（DEMO）任务，并开发了一个基于DEMO的对话代理，展示了在对话建模和评估方面的优越性能。",\n        "RAG": "在RAG领域，\'ConQRet: Benchmarking Fine-Grained Evaluation of Retrieval Augmented Argumentation with LLM Judges\'同样值得关注。该论文介绍了ConQRet基准 
，用于评估检索增强论证的细粒度评估，并提出了使用多个细粒度LLM法官的自动化评估方法。",\n        "Agent": "在Agent领域，有两篇论文值得关注。第一篇是\'DEMO: 
Reframing Dialogue Interaction with Fine-grained Element Modeling\'，该论文提出了对话元素建模（DEMO）任务，并开发了一个基于DEMO的对话代理，展示了在对话建 
模和评估方面的优越性能。第二篇是\'TeamCraft: A Benchmark for Multi-Modal Multi-Agent Systems in Minecraft\'，该论文介绍了TeamCraft基准，用于评估多模态多代
理系统在Minecraft中的性能，揭示了现有模型在泛化到新目标、场景和代理数量方面的不足。",\n        "多模态": "在多模态领域，有三篇论文值得关注。第一篇是\'TeamCraft: A Benchmark for Multi-Modal Multi-Agent Systems in Minecraft\'，该论文介绍了TeamCraft基准，用于评估多模态多代理系统在Minecraft中的性能。第二篇是\'MixedGaussianAvatar: Realistically and Geometrically Accurate Head Avatar via Mixed 2D-3D Gaussian Splatting\'，该论文提出了MixedGaussianAvatar方法，结合了
2D和3D高斯喷射技术，以实现高保真度和几何精确的3D头部头像重建。第三篇是\'Stag-1: Towards Realistic 4D Driving Simulation with Video Generation Model\'，该 
论文提出了Stag-1模型，用于实现逼真的4D驾驶模拟，通过视频生成模型创建照片级真实感和可控的4D驾驶模拟视频。",\n        "音频": "在音频领域，\'BIAS: A Body-based Interpretable Active Speaker Approach\'值得关注。该论文提出了BIAS模型，结合音频、面部和身体信息来准确预测不同挑战条件下的主动说话者，并提供了可解释性 
。",\n        "计算机视觉": "在计算机视觉领域，有三篇论文值得关注。第一篇是\'Sparse autoencoders reveal selective remapping of visual concepts during adaptation\'，该论文介绍了PatchSAE稀疏自动编码器，用于提取视觉概念及其空间属性，并研究了这些概念在模型适应过程中的影响。第二篇是\'MixedGaussianAvatar: Realistically and Geometrically Accurate Head Avatar via Mixed 2D-3D Gaussian Splatting\'，该论文提出了MixedGaussianAvatar方法，结合了2D和3D高斯喷射技术，以实现 
高保真度和几何精确的3D头部头像重建。第三篇是\'BIAS: A Body-based Interpretable Active Speaker Approach\'，该论文提出了BIAS模型，结合音频、面部和身体信息来
准确预测不同挑战条件下的主动说话者，并提供了可解释性。第四篇是\'Stag-1: Towards Realistic 4D Driving Simulation with Video Generation Model\'，该论文提出 
了Stag-1模型，用于实现逼真的4D驾驶模拟，通过视频生成模型创建照片级真实感和可控的4D驾驶模拟视频。"\n    }\n}\n```'
"""
    res = asyncio.run(send_email(content, "test", to_addrs="xyzhang290@gmail.com"))
    print(res)
