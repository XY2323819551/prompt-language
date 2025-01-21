import pandas as pd
import matplotlib.pyplot as plt
import os

async def log2excelpic(prompts=None, acc=None, fluency_acc=None, consistency_acc=None, suggestions=None):
    """将log文件转换为excel文件和图片
    """
    os.makedirs('output', exist_ok=True)
    
    # 1. 写入Excel
    data = {
        'prompt': prompts,
        'acc': acc,
        'fluency_accuracy': fluency_acc,
        'consistency_accuracy': consistency_acc,
    }

    if acc:
        while len(acc) < len(prompts):
            acc.append(100)
        data['acc'] = acc
    if fluency_acc:
        while len(fluency_acc) < len(prompts):
            fluency_acc.append(100)
        data['fluency_accuracy'] = fluency_acc
    
    if consistency_acc:
        while len(consistency_acc) < len(prompts):
            consistency_acc.append(100)
        data['consistency_accuracy'] = consistency_acc
    
    if suggestions:
        while len(suggestions) < len(prompts):
            suggestions.append("no suggestions")
        data['suggestion'] = suggestions
    
    df = pd.DataFrame(data)
    excel_path = 'output/prompt_analysis.xlsx'
    df.to_excel(excel_path, index=False)
    print(f"Excel文件已保存到: {excel_path}")
    
    # 2. 生成图表
    plt.figure(figsize=(12, 6))
    
    x_labels = [f'iter_{i}' for i in range(len(prompts))]
    
    # 绘制三条曲线
    if acc:
        plt.plot(x_labels, acc, marker='o', linestyle='-', linewidth=2, markersize=8, label='Accuracy')
        for i, score in enumerate(acc):
            plt.annotate(f'{score:.2f}', (i, score), textcoords="offset points", xytext=(0,10), ha='center')
    
    if fluency_acc:
        plt.plot(x_labels, fluency_acc, marker='s', linestyle='--', linewidth=2, markersize=8, label='Fluency')
        for i, score in enumerate(fluency_acc):
            plt.annotate(f'{score:.2f}', (i, score), textcoords="offset points", xytext=(0,-15), ha='center')
    
    if consistency_acc:
        plt.plot(x_labels, consistency_acc, marker='^', linestyle=':', linewidth=2, markersize=8, label='Consistency')
        for i, score in enumerate(consistency_acc):
            plt.annotate(f'{score:.2f}', (i, score), textcoords="offset points", xytext=(0,25), ha='center')
    
    # 设置图表属性
    plt.title('Prompt Performance Analysis', fontsize=14)
    plt.xlabel('Iterations', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    
    # 设置y轴范围
    all_scores = []
    if acc: all_scores.extend(acc)
    if fluency_acc: all_scores.extend(fluency_acc)
    if consistency_acc: all_scores.extend(consistency_acc)
    if all_scores:
        plt.ylim(min(all_scores) - 0.1 if min(all_scores) > 0.1 else 0, 1.0)
    
    # 添加图例
    plt.legend(loc='lower right')
    
    # 调整布局
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
    test_fluency_acc = [0.76, 0.88, 0.90]
    test_consistency_acc = [0.9, 0.92, 0.95]
    test_suggestions = ["建议1", "建议2"]
    
    await log2excelpic(prompts=test_prompts, acc=test_acc, fluency_acc=test_fluency_acc, consistency_acc=test_consistency_acc, suggestions=test_suggestions)
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
