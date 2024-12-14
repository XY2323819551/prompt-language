import arxiv


async def arxiv_search(keyword="", nums=1, params_format=False):
  if params_format:
    return ['keyword', 'nums']
  
  client = arxiv.Client()
  search = arxiv.Search(
    query = keyword,
    max_results = nums,
    sort_by = arxiv.SortCriterion.SubmittedDate
  )
  results = []
  for r in client.results(search):
    print("title:", r.title)
    print("authors:", r.authors)
    print("published:", r.published)
    print("summary:", r.summary)
    down_load_path = r.download_pdf("./tmp/arxiv")
    results.append(
      {
        "title": r.title,
        "authors": r.authors,
        "published": r.published,
        "summary": r.summary,
        "down_load_path": down_load_path
      }
    )
  return results

