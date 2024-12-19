@code(```python
def get_query():
    return "1912年中国、法国、英国、美国都发生过哪些历史事件"
query = get_query()
```) -> query


@duckduckgo_search($query) >> search_result
@bing_search($query) >> search_result
@google_search($query) >> search_result

@deduplicate($search_result) -> deduplicated_result
@save2local(content=$deduplicated_result, filename="books/event_raws.json") -> status

