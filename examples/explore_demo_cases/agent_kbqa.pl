@agent(
    type="explore", 
    task="cto下面有哪些团队", 
    tools=["ngql", "kgrag", "query_rewrite", "r1_model"]
) -> res
