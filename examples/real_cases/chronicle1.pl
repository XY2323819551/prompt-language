@read_local(filename="books/event_raws.json") -> event_names

For $res in $search_result:
    请找出下列内容信息中提到的重要历史事件。内容信息如下：
    $res

    结果以字符串列表的形式返回，列表中的每一项都是一个历史事件的名称，
    直接按照要求返回字符串列表即可，不要多余的解释 >> result
END

@deduplicate($result) -> deduplicated_result
@save2local(content=$deduplicated_result, filename="books/event_names.json") -> status
