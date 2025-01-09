import pandas as pd
import matplotlib.pyplot as plt
import os

async def log2excelpic(prompts=None, acc=None, suggestions=None):
    """将log文件转换为excel文件和图片
    """
    
    prompts = eval(prompts)
    acc = eval(acc)
    suggestions = eval(suggestions)
    
    # 创建output目录（如果不存在）
    os.makedirs('output', exist_ok=True)
    
    # 1. 写入Excel
    # 构建数据字典
    data = {
        'prompt': prompts,
        'accuracy': acc,
    }

    if acc:
        # 确保suggestions长度和prompts一致（用None填充）
        while len(acc) < len(prompts):
            acc.append(100)
        data['acc'] = acc
    
    # 如果suggestions存在，添加到数据中
    if suggestions:
        # 确保suggestions长度和prompts一致（用None填充）
        while len(suggestions) < len(prompts):
            suggestions.append("no suggestions")
        data['suggestion'] = suggestions
    
    # 创建DataFrame并保存到Excel
    df = pd.DataFrame(data)
    excel_path = 'output/prompt_analysis.xlsx'
    df.to_excel(excel_path, index=False)
    print(f"Excel文件已保存到: {excel_path}")
    
    # 2. 生成图表
    plt.figure(figsize=(12, 6))
    
    # 生成x轴标签（用iter_index替代长文本）
    x_labels = [f'iter_{i}' for i in range(len(prompts))]
    
    # 绘制折线图
    plt.plot(x_labels, acc, marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # 设置图表属性
    plt.title('Prompt Performance Analysis', fontsize=14)
    plt.xlabel('Iterations', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    
    # 设置网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 旋转x轴标签，防止重叠
    plt.xticks(rotation=45)
    
    # 设置y轴范围，让图表更美观
    plt.ylim(min(acc) - 0.1 if min(acc) > 0.1 else 0, 1.0)
    
    # 添加数据标签
    for i, score in enumerate(acc):
        plt.annotate(f'{score:.4f}', 
                    (i, score), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center')
    
    # 调整布局，确保所有元素都显示完整
    plt.tight_layout()
    
    # 保存图片
    pic_path = 'output/prompt_performance.png'
    plt.savefig(pic_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"性能分析图表已保存到: {pic_path}")


async def main():
    # 测试代码
    test_prompts = [
        "这是一个很长的prompt1...",
        "这是一个很长的prompt2...",
        "这是一个很长的prompt3..."
    ]
    test_acc = [0.75, 0.82, 0.90]
    test_suggestions = ["建议1", "建议2"]
    
    await log2excelpic(prompts=test_prompts, acc=test_acc, suggestions=test_suggestions)
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
