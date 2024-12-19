@read_local(filename="books/event_names.json") -> event_names

FOR $event_name in $event_names:
    @wikipedia_search($event_name) >> search_result
    @bing_search($event_name) >> search_result
    @google_search($event_name) >> search_result
    @duckduckgo_search($event_name) >> search_result
END

@deduplicate($search_result) -> deduplicated_result
@save2local(content=$deduplicated_result, filename="books/event_names_raw_content.json") -> status

