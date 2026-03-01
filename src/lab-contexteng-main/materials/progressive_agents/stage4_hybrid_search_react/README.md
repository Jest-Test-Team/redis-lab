# Stage 4: Hybrid Search with ReAct Loop

## 📍 Position in Learning Path

| Previous | Current | Next |
|----------|---------|------|
| [Stage 3: Full Agent](../stage3_full_agent_without_memory/) | **Stage 4** | [Stage 5: Working Memory](../stage5_working_memory/) |

This stage adds hybrid search capabilities with Named Entity Recognition and an explicit **ReAct** (Reasoning + Acting) loop for transparent reasoning.

---

## 🎯 Purpose

The ReAct pattern makes the agent's decision-making process **visible and debuggable**. Instead of opaque tool-calling, you see:
- **Thought**: What the agent is thinking
- **Action**: What tool it decides to use
- **Observation**: What results it receives

**Key Learning**: "Transparent reasoning improves debugging, trust, and understanding of agent behavior."

---

## 📚 Related Notebooks

| Notebook | Concepts Applied | Implementation in This Stage |
|----------|-----------------|------------------------------|
| [Section 4: Tools and LangGraph Fundamentals](../../notebooks/section-4-tools-and-agents/01_tools_and_langgraph_fundamentals.ipynb) | ReAct pattern, agent loops | `react_agent.py` - ReAct loop implementation |
| [Section 2: Crafting and Optimizing Context](../../notebooks/section-2-retrieved-context-engineering/02_crafting_and_optimizing_context.ipynb) | Hybrid search, progressive disclosure | `tools.py: search_courses_sync()` |

### Key Notebook Concepts Demonstrated

**From Section 4, Notebook 1 - "Tools and LangGraph Fundamentals":**
- **ReAct Pattern**: Thought → Action → Observation loop
- **Iterative Reasoning**: Multiple iterations until task complete
- **Explicit Termination**: FINISH action to end loop

**Study Path**: Read Section 4, Notebook 1's ReAct section, then examine `react_agent.py` and `react_prompts.py` to see the implementation.

---

## 🔄 What Changed from Stage 3

| Feature | Stage 3 | Stage 4 |
|---------|---------|---------|
| **Search** | Semantic only | **Hybrid** (exact + semantic) |
| **Reasoning** | Hidden (tool-calling) | **Visible** (Thought → Action → Observation) |
| **Decision Process** | Opaque LLM | **Transparent** reasoning trace |
| **Debugging** | Harder | **Easier** with `--show-reasoning` |

---

## 🏗️ Architecture

```mermaid
graph TD
    Q[Query] --> RA[ReAct Agent]

    subgraph ReAct Loop
        RA --> T1[💭 Thought: Analyze query]
        T1 --> A1[🔧 Action: search_courses]
        A1 --> O1[👁️ Observation: Results]
        O1 --> T2[💭 Thought: Evaluate]
        T2 --> |Need more| A1
        T2 --> |Done| F[✅ FINISH]
    end

    F --> R[Response + Reasoning Trace]
```

## 🚀 Usage

### Prerequisites

Make sure you have:
- Installed the package: `pip install -e .` (from repository root)
- Set environment variables:
  ```bash
  export OPENAI_API_KEY="your-openai-api-key"
  export REDIS_URL="redis://localhost:6379"
  ```

### Running the Agent

From the repository root:

```bash
cd progressive_agents/stage4_hybrid_search

# Single query
python cli.py "What are the prerequisites for CS002?"

# Show reasoning trace
python cli.py --show-reasoning "What are the prerequisites for CS009?"

# Interactive mode
python cli.py
```

## 📁 File Structure

```
stage4_hybrid_search/
├── cli.py                    # Interactive CLI with --show-reasoning
├── README.md                 # This file
└── agent/
    ├── __init__.py          # Module exports
    ├── react_agent.py       # ReAct loop implementation
    ├── react_parser.py      # Output parsing (max_length=8000)
    ├── react_prompts.py     # System prompt with examples
    ├── tools.py             # search_courses tool with FilterQuery
    ├── state.py             # WorkflowState with reasoning_trace
    ├── setup.py             # CourseManager initialization
    └── workflow.py          # LangGraph workflow
```

## Key Fixes Applied

1. **Hierarchical Path**: Uses correct path `parent.parent.parent.parent / "src"`
2. **FilterQuery**: Exact course code matching instead of semantic search
3. **Observation Length**: 8000 chars to prevent syllabus truncation
4. **Empty Data Handling**: Prompt guidance for empty prerequisites

## Test Results

| Query | Time | Iterations | Result |
|-------|------|------------|--------|
| CS002 prerequisites (has CS001) | 5.1s | 2 | ✅ "requires CS001 (Intro to Programming)" |
| CS010 prerequisites (has CS002, MATH020) | 3.3s | 2 | ✅ "requires CS002 and MATH020" |
| CS006 syllabus | 7.3s | 2 | ✅ Full syllabus returned |

## Comparison with Other Stages

| Feature | Stage 3 | Stage 4 | Stage 5 | Stage 6 |
|---------|---------|---------|---------|---------|
| Search | Semantic | Hybrid | Hybrid | Hybrid |
| Reasoning | Hidden | **Visible** | Visible | Visible |
| Memory | None | None | Working (session) | Full (working + long-term) |
| Tools | N/A | 1 | 1 | 3 |

## Example Reasoning Trace

```
🧠 Reasoning Trace:
================================================================================
💭 Thought: The user is asking about prerequisites. I'll use exact match.

🔧 Action: search_courses
   Input: {"query": "CS002", "intent": "PREREQUISITES", "search_strategy": "exact_match", ...}
👁️  Observation: Found CS002 - Data Structures and Algorithms...

💭 Thought: I found the course info. Prerequisites: CS001 (Introduction to Programming).

✅ FINISH
================================================================================
```

## 🔍 Code References & Automatic Behaviors

This section provides exact code references for the ReAct pattern implementation.

### ReAct Loop Implementation

**Code References:**

| Concept | File | Lines | Description |
|---------|------|-------|-------------|
| ReAct Agent | `progressive_agents/stage4_hybrid_search/agent/react_agent.py` | All | ReAct loop implementation |
| ReAct Prompts | `progressive_agents/stage4_hybrid_search/agent/react_prompts.py` | All | System prompt with Thought/Action/Observation format |
| Output Parser | `progressive_agents/stage4_hybrid_search/agent/react_parser.py` | All | Parses LLM output into structured format |
| State with Trace | `progressive_agents/stage4_hybrid_search/agent/state.py` | All | `WorkflowState` with `reasoning_trace` field |

### Automatic Behaviors (Inherited from Stage 3)

| Behavior | Handled By | How It Works |
|----------|------------|--------------|
| **Progressive Disclosure** | `HierarchicalContextAssembler` | Summaries for all, details for top N |
| **Hybrid Search Fallback** | `search_courses_sync()` | Falls back to semantic if exact match fails |
| **Observation Truncation** | `react_parser.py` | Limits observation to 8000 chars to prevent syllabus truncation |

---

## 🔗 Related Resources

### Learning Path Navigation
- **Previous**: [Stage 3: Full Agent](../stage3_full_agent_without_memory/) - Basic agent with tool calling
- **Next**: [Stage 5: Working Memory](../stage5_working_memory/) - Add session-based memory

### Notebooks to Study
- **[Section 4: Tools and LangGraph Fundamentals](../../notebooks/section-4-tools-and-agents/01_tools_and_langgraph_fundamentals.ipynb)**: ReAct pattern fundamentals
- **[Section 3: Working and Long-term Memory](../../notebooks/section-3-memory-systems/01_working_and_longterm_memory.ipynb)**: Prepare for Stage 5

