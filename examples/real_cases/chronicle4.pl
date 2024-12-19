@read_local(filename="books/event_names_summary.json") -> event_names_details


现在，请你根据所有参考内容，总结出一份历史事件分析表。重点关注同一个时期不同国家的发展情况，突出对比同一时期世界的发展差异。
并从这些差异中找到中国发展的弱点，并给出发展建议。（最好关注到参考信息中所有的历史事件）
参考资料如下：
$event_names_details

以markdown格式输出。输出内容不少于2000字 -> final_summary

@save2local(content=$final_summary, filename="books/final_summary.md") -> status
@send_email(content=$final_summary) -> status
