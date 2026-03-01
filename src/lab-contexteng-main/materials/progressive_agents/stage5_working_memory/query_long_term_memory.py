"""
Helper module for querying long-term memories from RAMS.

This demonstrates how RAMS automatically extracts facts from conversations.
"""

import tiktoken
from typing import List
from agent_memory_client.filters import UserId
from agent.nodes import get_memory_client


async def query_extracted_memories(
    student_id: str = "test_user",
    search_query: str = "courses student asked about",
    limit: int = 10
):
    """
    Query long-term memories automatically extracted by RAMS.
    
    Args:
        student_id: User identifier to query memories for
        search_query: Semantic search query for relevant memories
        limit: Maximum number of memories to return
        
    Returns:
        List of extracted memories, or None if error occurs
    """
    memory_client = get_memory_client()
    
    try:
        # Search long-term memory using semantic search
        search_results = await memory_client.search_long_term_memory(
            text=search_query,
            user_id=UserId(eq=student_id),
            limit=limit
        )
        
        print("🧠 Automatically Extracted Long-Term Memories:\n")
        
        if search_results.memories and len(search_results.memories) > 0:
            for i, memory in enumerate(search_results.memories, 1):
                print(f"{i}. {memory.text}")
                if hasattr(memory, 'topics') and memory.topics:
                    print(f"   Topics: {', '.join(memory.topics)}")
                if hasattr(memory, 'memory_type'):
                    print(f"   Type: {memory.memory_type}")
                if hasattr(memory, 'created_at'):
                    print(f"   Created: {memory.created_at}")
                print()
            
            print(f"📊 RAMS extracted {len(search_results.memories)} facts from conversations")
            print("   These persist across sessions and compress ~10x compared to raw message history")
            
            return search_results.memories
        else:
            print("ℹ️  No long-term memories found yet.")
            print("\n   This is normal! Memory extraction happens asynchronously.")
            print("   • Run the multi-turn tests first")
            print("   • Wait ~30-60 seconds for RAMS to process conversations")
            print("   • Then run this query again")
            print("\n   What RAMS is doing in the background:")
            print("   • Analyzing conversation turns")
            print("   • Extracting key facts (preferences, interests, questions)")
            print("   • Storing with vector embeddings for semantic search")
            print("   • Deduplicating redundant information")
            
            return []
            
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  Error querying long-term memories: {error_msg}")
        print("\n📖 Troubleshooting:")
        
        if "500" in error_msg or "Internal Server Error" in error_msg:
            print("   • HTTP 500 typically means RAMS hasn't extracted memories yet")
            print("   • This is expected if you just ran the tests")
            print("   • Wait 30-60 seconds and try again")
            print("   • Memory extraction is an async background process")
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            print("   • Check that Agent Memory Server (RAMS) is running")
            print("   • Verify AGENT_MEMORY_URL is configured correctly")
            print("   • Default: http://localhost:8088")
        else:
            print("   • Make sure you ran the multi-turn tests first")
            print("   • Verify student_id matches the one used in tests")
            print("   • Check RAMS logs for more details")
        
        print("\n💡 Even if this fails initially, RAMS is still extracting memories!")
        print("   In Stage 6, you'll learn to explicitly query and manage them.")
        
        return None


async def check_working_memory(student_id: str = "test_user", session_id: str = None):
    """
    Check if working memory exists for a user/session.
    
    Args:
        student_id: User identifier
        session_id: Optional session identifier
        
    Returns:
        Working memory object if found, None otherwise
    """
    memory_client = get_memory_client()
    
    if not session_id:
        print(f"ℹ️  No session_id provided. Cannot check working memory.")
        print("   Working memory is session-scoped.")
        print("   Provide a session_id from one of the test runs.")
        return None
    
    try:
        _, working_memory = await memory_client.get_or_create_working_memory(
            session_id=session_id,
            user_id=student_id,
            model_name="gpt-4o-mini"
        )
        
        if working_memory and working_memory.messages:
            print(f"✅ Found working memory for session: {session_id}")
            print(f"   Messages: {len(working_memory.messages)}")
            print(f"   Turns: {len(working_memory.messages) // 2}")
            return working_memory
        else:
            print(f"ℹ️  No working memory found for session: {session_id}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error checking working memory: {e}")
        return None


async def analyze_compression(session_ids: List[str], student_id: str = "test_user"):
    """
    Compare token size between working memory and long-term memory.
    
    Demonstrates RAMS's compression efficiency by counting tokens in:
    - Working memory: Full conversation history for each session
    - Long-term memory: Extracted facts across all sessions
    
    Args:
        session_ids: List of session IDs to analyze
        student_id: User identifier for memory queries
    """
    print("\n" + "=" * 70)
    print("📊 COMPRESSION ANALYSIS: Long-Term Memory vs Working Memory")
    print("=" * 70 + "\n")
    
    memory_client = get_memory_client()
    encoding = tiktoken.encoding_for_model("gpt-4o")
    
    total_ltm_tokens = 0
    total_wm_tokens = 0
    
    # Count tokens in working memory for each session
    for session_id in session_ids:
        try:
            _, working_memory = await memory_client.get_or_create_working_memory(
                session_id=session_id,
                user_id=student_id,
                model_name="gpt-4o-mini"
            )
            
            if working_memory and working_memory.messages:
                # Count tokens in working memory (full conversation history)
                wm_text = "\n".join([f"{msg.role}: {msg.content}" for msg in working_memory.messages])
                wm_tokens = len(encoding.encode(wm_text))
                total_wm_tokens += wm_tokens
                
                print(f"Session: {session_id}")
                print(f"  Working Memory: {len(working_memory.messages)} messages, {wm_tokens:,} tokens")
        except Exception as e:
            print(f"⚠️  Error loading session {session_id}: {e}")
    
    # Count tokens in long-term memory (extracted facts)
    try:
        search_results = await memory_client.search_long_term_memory(
            text="courses student asked about",
            user_id=UserId(eq=student_id),
            limit=50  # Get more to ensure we capture all extracted facts
        )
        
        if search_results.memories and len(search_results.memories) > 0:
            ltm_text = "\n".join([mem.text for mem in search_results.memories])
            total_ltm_tokens = len(encoding.encode(ltm_text))
            print(f"\nLong-Term Memory: {len(search_results.memories)} facts, {total_ltm_tokens:,} tokens")
        else:
            print("\n⚠️ No long-term memories found yet")
    except Exception as e:
        print(f"\n⚠️ Error querying long-term memory: {e}")
    
    # Show compression ratio
    if total_wm_tokens > 0 and total_ltm_tokens > 0:
        compression_ratio = total_wm_tokens / total_ltm_tokens
        print(f"\n{'=' * 70}")
        print(f"📈 COMPRESSION RATIO: {compression_ratio:.1f}x")
        print(f"{'=' * 70}")
        print(f"\nWorking Memory Total:   {total_wm_tokens:,} tokens")
        print(f"Long-Term Memory Total: {total_ltm_tokens:,} tokens")
        print(f"Tokens Saved:           {total_wm_tokens - total_ltm_tokens:,} tokens ({((total_wm_tokens - total_ltm_tokens) / total_wm_tokens * 100):.1f}% reduction)")
        print(f"\n💡 RAMS compressed {len(session_ids)} conversations into {len(search_results.memories)} searchable facts")
        print(f"   This is {compression_ratio:.1f}x more efficient than storing full message history!")
    elif total_wm_tokens > 0:
        print(f"\n⚠️ Working memory exists ({total_wm_tokens:,} tokens) but long-term extraction hasn't completed yet")
        print("   Wait 30-60 seconds and re-run this analysis to see the compression ratio")
    else:
        print("\n⚠️ No working memory found for the provided sessions")
    
    print("")
