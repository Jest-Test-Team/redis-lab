"""
Test comparison script for Stage 3 Hierarchical Retrieval.

This script runs multiple test queries to demonstrate adaptive retrieval
and compares token usage across different query types.

Run this after completing the Stage 3 implementation to validate your work.
"""

from tqdm.auto import tqdm


async def run_comparison_tests(workflow):
    """Run all test queries and display comparison analysis.
    
    Args:
        workflow: The compiled LangGraph workflow (already created in notebook)
    """
    
    # Test queries
    queries = [
        ("hi", "Greeting"),
        ("What courses are available?", "General Overview"),
        ("What will I learn in CS002?", "Learning Objectives"),
        ("What assignments are in CS002?", "Assignments")
    ]
    
    results = []
    
    print("\n" + "="*70)
    print("Running comparison tests...")
    print("="*70 + "\n")
    
    # Run each query with progress bar
    progress_bar = tqdm(total=len(queries), desc="Testing queries", 
                       bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}')
    
    for query, query_type in queries:
        result = await workflow.ainvoke({"original_query": query})
        results.append(result)
        progress_bar.update(1)
    
    progress_bar.close()
    
    print("\n" + "="*70)
    print("All tests complete!")
    print("="*70)
    
    # Build comparison table
    comparison_data = []
    retrieval_types = ["None", "Summaries Only", "Hierarchical (Full)", "Hierarchical (Full)"]
    
    for i, (result, (query, query_type)) in enumerate(zip(results, queries)):
        token_usage = result.get('metrics', {}).get('token_usage', {})
        comparison_data.append({
            "Query Type": query_type,
            "Intent": result.get('query_intent', 'N/A'),
            "Retrieval": retrieval_types[i],
            "LLM Calls": sum(result.get('llm_calls', {}).values()),
            "Input Tokens": token_usage.get('input_tokens', 0),
            "Output Tokens": token_usage.get('output_tokens', 0),
            "Total Tokens": token_usage.get('total_tokens', 0),
            "Latency (ms)": result.get('metrics', {}).get('total_latency', 0),
        })
    
    # Display comparison table
    print("\n" + "="*110)
    print("📊 ADAPTIVE RETRIEVAL COMPARISON - TOKEN USAGE ANALYSIS")
    print("="*110)
    
    # Table header
    print(f"{'Query Type':<20} {'Intent':<20} {'Retrieval':<20} {'LLM Calls':<10} {'Input':<10} {'Output':<10} {'Total':<10} {'Latency':<10}")
    print("-" * 110)
    
    # Table rows
    for row in comparison_data:
        print(f"{row['Query Type']:<20} {row['Intent']:<20} {row['Retrieval']:<20} "
              f"{row['LLM Calls']:<10} {row['Input Tokens']:<10} {row['Output Tokens']:<10} "
              f"{row['Total Tokens']:<10} {row['Latency (ms)']:<10.2f}")
    
    print("="*110)
    
    # Calculate efficiency gains
    total_tokens = sum([r['Total Tokens'] for r in comparison_data])
    total_input = sum([r['Input Tokens'] for r in comparison_data])
    total_output = sum([r['Output Tokens'] for r in comparison_data])
    
    hierarchical_data = [r for r in comparison_data if r['Retrieval'] == 'Hierarchical (Full)']
    if hierarchical_data:
        avg_hierarchical = sum([r['Total Tokens'] for r in hierarchical_data]) / len(hierarchical_data)
        if_always_hierarchical = int(avg_hierarchical * len(comparison_data))
        savings = if_always_hierarchical - total_tokens
        savings_pct = (savings / if_always_hierarchical * 100) if if_always_hierarchical > 0 else 0
        
        print(f"\n💰 EFFICIENCY ANALYSIS:")
        print(f"   Adaptive Approach: {total_tokens:,} tokens (in: {total_input:,}, out: {total_output:,})")
        print(f"   Always Hierarchical: ~{if_always_hierarchical:,} tokens")
        print(f"   Tokens Saved: ~{savings:,} ({savings_pct:.1f}% reduction)")
        print(f"\n🎯 Key Insight: Intent-driven retrieval saves ~{savings_pct:.0f}% tokens!")
        
        # Cost estimate
        cost_adaptive = (total_input / 1_000_000) * 2.50 + (total_output / 1_000_000) * 10.00
        hier_input = sum([r['Input Tokens'] for r in hierarchical_data]) / len(hierarchical_data) * len(comparison_data)
        hier_output = sum([r['Output Tokens'] for r in hierarchical_data]) / len(hierarchical_data) * len(comparison_data)
        cost_always = (hier_input / 1_000_000) * 2.50 + (hier_output / 1_000_000) * 10.00
        
        print(f"\n💵 COST IMPACT (GPT-4o):")
        print(f"   These 4 queries: ${cost_adaptive:.6f} vs ${cost_always:.6f} (saving ${cost_always - cost_adaptive:.6f})")
        print(f"   Scaled to 10K queries/day: ${(cost_always - cost_adaptive) * 2500:.2f}/day savings!\n")
