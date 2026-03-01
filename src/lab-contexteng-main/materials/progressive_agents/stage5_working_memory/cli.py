#!/usr/bin/env python3
"""
Interactive CLI for the Memory-Augmented Course Q&A Agent (Stage 5).

Usage:
    python cli.py --student-id alice                           # Interactive mode
    python cli.py --student-id alice "your question"           # Single query mode
    python cli.py --student-id alice --session-id sess_001     # Resume session
    python cli.py --student-id alice --simulate                # Simulate with example queries
    python cli.py --student-id alice --quiet "your question"   # Suppress intermediate logging
"""

import asyncio
import atexit
import logging
import os
import sys
import uuid
from pathlib import Path

# Check for quiet mode early, before any logging or imports happen
_quiet_mode = "--quiet" in sys.argv or "-q" in sys.argv

# Configure logging level very early, before any imports that might configure logging
if _quiet_mode:
    logging.basicConfig(level=logging.CRITICAL)
    # Also suppress httpx and other common loggers
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("redisvl.index.index").setLevel(logging.CRITICAL)

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from repository root (2 levels up from this file)
env_path = Path(__file__).parent.parent.parent / ".env"
if not load_dotenv(env_path):
    # Fallback: try to find .env in current directory or parent directories
    current = Path.cwd()
    for _ in range(5):  # Try up to 5 levels up
        test_path = current / ".env"
        if test_path.exists():
            load_dotenv(test_path)
            break
        current = current.parent

# Add agent module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import create_workflow, run_agent_async, setup_agent
from agent.setup import cleanup_courses

# If quiet mode, ensure all loggers are suppressed after imports
if _quiet_mode:
    logging.getLogger("course-qa-setup").setLevel(logging.CRITICAL)
    logging.getLogger("course-qa-workflow").setLevel(logging.CRITICAL)
    logging.getLogger("working-memory-agent").setLevel(logging.CRITICAL)


class MemoryAugmentedCLI:
    """Interactive CLI for Memory-Augmented Course Q&A Agent."""

    def __init__(
        self,
        student_id: str,
        session_id: str = None,
        cleanup_on_exit: bool = False,
        debug: bool = False,
        show_reasoning: bool = False,
        verbose: bool = True,
    ):
        self.agent = None
        self.course_manager = None
        self.memory_client = None
        self.student_id = student_id
        self.session_id = session_id or f"session_{student_id}_{uuid.uuid4().hex[:8]}"
        self.cleanup_on_exit = cleanup_on_exit
        self.debug = debug
        self.show_reasoning = show_reasoning
        self.verbose = verbose

        # Register cleanup handler if requested
        if cleanup_on_exit:
            atexit.register(self._cleanup)

    def _cleanup(self):
        """Cleanup handler called on exit."""
        if self.course_manager and self.cleanup_on_exit:
            if self.verbose:
                print("\n🧹 Cleaning up courses from Redis...")
            try:
                asyncio.run(cleanup_courses(self.course_manager))
                if self.verbose:
                    print("✅ Cleanup complete")
            except Exception as e:
                print(f"⚠️  Cleanup failed: {e}")

    async def initialize(self):
        """Initialize the agent and load course data."""
        if self.verbose:
            print("=" * 80)
            print("Memory-Augmented Course Q&A Agent - Stage 5")
            print("=" * 80)
            print()

        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY environment variable not set")
            print("   Please set it with: export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)

        # Check for Agent Memory Server
        memory_url = os.getenv("AGENT_MEMORY_URL", "http://localhost:8088")
        if self.verbose:
            print(f"🔗 Agent Memory Server: {memory_url}")

        try:
            # Initialize the agent (will auto-load courses if needed)
            if self.verbose:
                print("🔧 Initializing Memory-Augmented Course Q&A Agent...")
                print("📦 Loading courses into Redis (if not already loaded)...")
            self.course_manager, self.memory_client = await setup_agent(
                auto_load_courses=True
            )
            if self.verbose:
                print()

            # Create the workflow with verbose setting
            if self.verbose:
                print("🔧 Creating LangGraph workflow with memory nodes...")
            self.agent = create_workflow(self.course_manager, verbose=self.verbose)
            if self.verbose:
                print("✅ Workflow created successfully")
                print()

            # Show session info
            if self.verbose:
                print(f"👤 Student ID: {self.student_id}")
                print(f"🔗 Session ID: {self.session_id}")
                print()

            # Show cleanup status
            if self.verbose:
                if self.cleanup_on_exit:
                    print("🧹 Courses will be cleaned up on exit")
                else:
                    print("💾 Courses will persist in Redis after exit")
                print()

        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            if self.debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    async def ask_question(self, query: str, show_details: bool = True):
        """Ask a question and get a response."""
        if self.verbose:
            print("=" * 80)
            print(f"❓ Question: {query}")
            print("=" * 80)
            print()

        # Run the agent with session and student IDs (async)
        result = await run_agent_async(
            self.agent,
            query,
            session_id=self.session_id,
            student_id=self.student_id,
            enable_caching=False,
        )

        # Show reasoning trace if enabled and verbose
        if self.show_reasoning and self.verbose and result.get("reasoning_trace"):
            print("🧠 Reasoning Trace:")
            print("=" * 80)
            for step in result["reasoning_trace"]:
                if step["type"] == "thought":
                    print(f"💭 Thought: {step['content']}")
                elif step["type"] == "action":
                    print(f"🔧 Action: {step['action']}")
                    print(f"   Input: {step['input']}")
                    obs = step['observation']
                    obs_preview = obs[:200] + "..." if len(obs) > 200 else obs
                    print(f"👁️  Observation: {obs_preview}")
                elif step["type"] == "finish":
                    print(f"✅ FINISH")
                print()
            print("=" * 80)
            print()

        # Always print the response
        if self.verbose:
            print("📝 Answer:")
            print("-" * 80)
        print(result["final_response"])
        if self.verbose:
            print("-" * 80)
        print()

        if show_details and self.verbose:
            # Print metrics
            metrics = result["metrics"]
            print("📊 Performance:")
            print(f"   Total Time: {metrics['total_latency']:.2f}ms")
            print(f"   Memory Load: {metrics.get('memory_load_latency', 0):.3f}s")
            print(f"   Memory Save: {metrics.get('memory_save_latency', 0):.3f}s")
            print(f"   ReAct Iterations: {result.get('react_iterations', 0)}")
            print(f"   Reasoning Steps: {len(result.get('reasoning_trace', []))}")
            print(f"   Execution: {metrics['execution_path']}")
            print()

            # Print conversation history info
            history_count = len(result.get("conversation_history", []))
            if history_count > 0:
                print(
                    f"💾 Loaded {history_count} previous messages from working memory"
                )
                print()

            # Print sub-questions if decomposed
            if len(result.get("sub_questions", [])) > 1:
                print("🧠 Sub-questions:")
                for i, sq in enumerate(result["sub_questions"], 1):
                    print(f"   {i}. {sq}")
                print()

        return result

    async def interactive_mode(self):
        """Run in interactive mode with multi-turn conversations."""
        if self.verbose:
            print("=" * 80)
            print("Interactive Mode - Multi-turn Conversations")
            print("Commands: 'quit' or 'exit' to stop, 'help' for help")
            print("=" * 80)
            print()

        while True:
            try:
                # Get user input
                query = input("\n❓ Your question: ").strip()

                if not query:
                    continue

                # Handle commands
                if query.lower() in ["quit", "exit", "q"]:
                    if self.verbose:
                        print("\n👋 Goodbye!")
                    break

                if query.lower() == "help":
                    self.show_help()
                    continue

                # Ask the question
                print()
                await self.ask_question(query, show_details=True)

            except KeyboardInterrupt:
                if self.verbose:
                    print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                if self.debug:
                    import traceback

                    traceback.print_exc()
                print()

    async def simulate_mode(self):
        """Run simulation with multi-turn conversation examples."""
        if self.verbose:
            print("=" * 80)
            print("Simulation Mode - Multi-turn Conversation Examples")
            print("=" * 80)
            print()

        # Multi-turn conversation examples
        conversations = [
            [
                "What is CS004?",
                "What are the prerequisites?",
                "Give me details about it",
            ],
            [
                "Show me machine learning courses",
                "What about the first one?",
                "What's the workload like?",
            ],
        ]

        for conv_num, queries in enumerate(conversations, 1):
            if self.verbose:
                print(f"\n{'=' * 80}")
                print(f"Conversation {conv_num}/{len(conversations)}")
                print(f"{'=' * 80}\n")

            for turn_num, query in enumerate(queries, 1):
                if self.verbose:
                    print(f"\n--- Turn {turn_num}/{len(queries)} ---\n")
                await self.ask_question(query, show_details=True)

                # Pause between turns
                if turn_num < len(queries) and self.verbose:
                    print("Press Enter to continue to next turn...")
                    input()

            # Pause between conversations
            if conv_num < len(conversations) and self.verbose:
                print("\n" + "=" * 80)
                print("Press Enter to start next conversation...")
                input()

        if self.verbose:
            print("=" * 80)
            print("✅ Simulation complete!")
            print("=" * 80)

    def show_help(self):
        """Show help information."""
        print()
        print("=" * 80)
        print("Help - Memory-Augmented Course Q&A Agent")
        print("=" * 80)
        print()
        print("This agent can answer questions about courses with conversation memory.")
        print()
        print("Example multi-turn conversation:")
        print("  Turn 1: What is CS004?")
        print("  Turn 2: What are the prerequisites?")
        print("  Turn 3: Give me details about it")
        print()
        print("The agent remembers context from previous turns!")
        print()
        print("Commands:")
        print("  • help  - Show this help message")
        print("  • quit  - Exit the program")
        print("  • exit  - Exit the program")
        print()
        print("=" * 80)
        print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 5 Memory-Augmented Agent - Multi-turn Conversations with Working Memory"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, runs in interactive mode)",
    )
    parser.add_argument(
        "--student-id", required=True, help="Student identifier (required)"
    )
    parser.add_argument(
        "--session-id",
        help="Session identifier (auto-generated if not provided)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run simulation mode with multi-turn conversation examples",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove courses from Redis on exit"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed error messages and tracebacks",
    )
    parser.add_argument(
        "--show-reasoning",
        action="store_true",
        help="Show ReAct reasoning trace",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress intermediate logging, only show final response",
    )

    args = parser.parse_args()

    # Determine cleanup behavior
    cleanup_on_exit = args.cleanup

    # Determine verbose mode (opposite of quiet)
    verbose = not args.quiet

    if args.simulate:
        # Simulation mode
        cli = MemoryAugmentedCLI(
            student_id=args.student_id,
            session_id=args.session_id,
            cleanup_on_exit=cleanup_on_exit,
            debug=args.debug,
            show_reasoning=args.show_reasoning,
            verbose=verbose,
        )
        await cli.initialize()
        await cli.simulate_mode()
    elif args.query:
        # Single query mode
        cli = MemoryAugmentedCLI(
            student_id=args.student_id,
            session_id=args.session_id,
            cleanup_on_exit=cleanup_on_exit,
            debug=args.debug,
            show_reasoning=args.show_reasoning,
            verbose=verbose,
        )
        await cli.initialize()
        await cli.ask_question(args.query, show_details=True)
    else:
        # Interactive mode
        cli = MemoryAugmentedCLI(
            student_id=args.student_id,
            session_id=args.session_id,
            cleanup_on_exit=cleanup_on_exit,
            debug=args.debug,
            show_reasoning=args.show_reasoning,
            verbose=verbose,
        )
        await cli.initialize()
        await cli.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
