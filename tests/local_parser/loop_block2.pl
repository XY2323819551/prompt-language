
FOR $question in ${test_data.questions}:
    @serpapi_search($question) -> search_result
    总结一下$search_result -> summary
    $summary >> qa_collection
END
