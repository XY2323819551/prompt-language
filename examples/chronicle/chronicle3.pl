@read_local(filename="books/event_names_raw_content.json") -> event_names_content

FOR $item in $event_names_content:
    请根据参考资料，简要总结出参考资料中所发生的历史事件，所总结的事件内容最好包括事件名称、事件年份、国家、事件主要内容、该事件产生的影响。参考资料如下：
    $item

    返回格式如下：
    '{
        "event_name": "事件名称",
        "event_year": "事件年份",
        "country": "事件发生国家",
        "event_summary": "事件简要总结"
    }' >> result
END


@save2local(content=$result, filename="books/event_names_summary.json") -> status

