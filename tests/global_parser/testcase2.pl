@code(```json
{
    "tasks": ["翻译", "总结", "分析"],
    "content": "这是一段需要处理的文本内容"
}
```) -> task_data

FOR $task in ${task_data.tasks}:
    IF $task == "翻译":
        将${task_data.content}翻译成英文 -> en_result
        $en_result >> results
    elif $task == "总结":
        总结${task_data.content}的要点 -> summary_result
        $summary_result >> results
    else:
        分析${task_data.content}的关键信息 -> analysis_result
        $analysis_result >> results
    END
END

@exit(msg="高级语句测试完成！")

