async def run_agent_test(workflow, query):
    """
    Run a single test query against the workflow and print detailed metrics.
    """
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")

    result = await workflow.ainvoke({"original_query": query})

    total_llm_calls = sum(result.get('llm_calls', {}).values())
    token_usage = result.get('metrics', {}).get('token_usage', {})
    total_tokens = token_usage.get('total_tokens', 0)
    
    courses_found = result.get('courses_found', 0)
    retrieval_status = 'Yes' if courses_found > 0 else 'No'

    print(f"""
🤖 Agent Response:
{result['final_response']}

📊 Metrics:
   Intent Detected: {result.get('query_intent', 'N/A')}
   Retrieval Triggered: {retrieval_status}
   Quality Score: {result.get('quality_score', 0):.2f}
   Total LLM Calls: {total_llm_calls}
   Total Tokens: {total_tokens:,} (input: {token_usage.get('input_tokens', 0):,}, output: {token_usage.get('output_tokens', 0):,})
   Latency: {result.get('metrics', {}).get('total_latency', 0):.2f}ms
""")
