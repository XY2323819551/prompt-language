@code(```python
def get_query():
    return "18世纪中、法、美的科技发明创造"
query = get_query()
```) -> query

@duckduckgo_search($query) >> search_result
@bing_search($query) >> search_result
@google_search($query) >> search_result

@deduplicate($search_result) -> deduplicated_result
@save2local(content=$deduplicated_result, filename="books/event_raws.json") -> status

