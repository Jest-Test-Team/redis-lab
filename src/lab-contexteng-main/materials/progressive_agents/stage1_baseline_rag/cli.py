#!/usr/bin/env python3
"""
CLI for Stage 1 Baseline RAG Agent.

Usage:
    # Interactive mode
    python cli.py

    # Single query
    python cli.py "What machine learning courses are available?"

    # Simulation mode (run example queries)
    python cli.py --simulate

    # Cleanup courses on exit
    python cli.py --cleanup

    # Quiet mode (suppress intermediate logging)
    python cli.py --quiet "What is CS001?"
"""

import asyncio
import atexit
import logging
import sys
from pathlib import Path

# Check for quiet mode early, before any logging happens
_quiet_mode = "--quiet" in sys.argv or "-q" in sys.argv

# Configure logging based on quiet mode
logging.basicConfig(
    level=logging.CRITICAL if _quiet_mode else logging.INFO,
    format="%(asctime)s %(name)-20s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("stage1-cli")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from project root
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(env_path)

from agent import cleanup_courses, initialize_state, setup_agent
from agent.workflow import create_workflow










class BaselineRAGCLI:
    """
    CLI for Stage 1 Baseline RAG Agent.

    Provides interactive mode, single query mode, and simulation mode.
    """

    def __init__(
        self, cleanup_on_exit: bool = False, debug: bool = False, verbose: bool = True
    ):
        """
        Initialize CLI.

        Args:
            cleanup_on_exit: If True, remove courses from Redis on exit
            debug: If True, show detailed error messages and tracebacks
            verbose: If True, show detailed logging. If False, only show final response.
        """
        self.workflow = None
        self.course_manager = None
        self.cleanup_on_exit = cleanup_on_exit
        self.debug = debug
        self.verbose = verbose

        # Register cleanup handler
        if cleanup_on_exit:
            atexit.register(self._cleanup)

    def _cleanup(self):
        """Cleanup courses on exit if requested."""
        if self.course_manager and self.cleanup_on_exit:
            if self.verbose:
                logger.info("\n🧹 Cleaning up courses...")
            asyncio.run(cleanup_courses(self.course_manager))

    def initialize(self):
        """Initialize the agent."""
        if self.verbose:
            logger.info("=" * 60)
            logger.info("Stage 1: Baseline RAG Agent (No Context Engineering)")
            logger.info("=" * 60)
            logger.info("")

        # Setup agent (this loads courses, we need the course_manager)
        # Pass verbose to suppress logging during setup
        self.workflow, self.course_manager = setup_agent(
            auto_load_courses=True, verbose=self.verbose
        )

        if self.verbose:
            if self.cleanup_on_exit:
                logger.info("🧹 Courses will be cleaned up on exit")
            else:
                logger.info("💾 Courses will persist in Redis after exit")

            logger.info("")

    def ask_question(self, query: str) -> dict:
        """
        Ask a question and get an answer.

        Args:
            query: User's question

        Returns:
            Result dictionary with answer and metadata
        """
        if self.verbose:
            logger.info(f"❓ Question: {query}")
            logger.info("")

        # Initialize state
        state = initialize_state(query)

        # Run workflow
        result = self.workflow.invoke(state)

        return result

    def print_result(self, result: dict):
        """
        Print the result in a formatted way.

        Args:
            result: Result dictionary from workflow
        """
        if self.verbose:
            logger.info("")
            logger.info("=" * 60)
            logger.info("📝 Answer:")
            logger.info("=" * 60)

        # Always print the final answer
        print(result["final_answer"])
        print()

        # Print metrics only if verbose
        if self.verbose:
            logger.info("=" * 60)
            logger.info("📊 Metrics:")
            logger.info("=" * 60)
            logger.info(f"   Courses Found: {result['courses_found']}")
            if result.get("total_tokens"):
                logger.info(f"   Estimated Tokens: ~{result['total_tokens']}")
            logger.info("")
            logger.warning("⚠️  This agent uses RAW context - no optimization!")
            logger.warning("   See Stage 2 for context engineering improvements")
            logger.info("")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.initialize()

        if self.verbose:
            logger.info("💬 Interactive Mode")
            logger.info("   Type your questions (or 'quit' to exit)")
            logger.info("")

        while True:
            try:
                query = input("You: ").strip()

                if not query:
                    continue

                if query.lower() in ["quit", "exit", "q"]:
                    if self.verbose:
                        logger.info("👋 Goodbye!")
                    break

                result = self.ask_question(query)
                self.print_result(result)

            except KeyboardInterrupt:
                if self.verbose:
                    logger.info("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                if self.debug:
                    import traceback

                    traceback.print_exc()

    def single_query_mode(self, query: str):
        """Run a single query."""
        self.initialize()

        result = self.ask_question(query)
        self.print_result(result)

    def simulation_mode(self):
        """Run simulation with example queries."""
        self.initialize()

        if self.verbose:
            logger.info("🎬 Simulation Mode - Running Example Queries")
            logger.info("")

        example_queries = [
            "What machine learning courses are available?",
            "What are beginner-level computer science courses?",
            "Which courses teach Python programming?",
        ]

        for i, query in enumerate(example_queries, 1):
            if self.verbose:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Example {i}/{len(example_queries)}")
                logger.info(f"{'=' * 60}\n")

            result = self.ask_question(query)
            self.print_result(result)

            if i < len(example_queries) and self.verbose:
                logger.info("Press Enter to continue...")
                input()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 1 Baseline RAG Agent - No Context Engineering"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, runs in interactive mode)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run simulation mode with example queries",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove courses from Redis on exit"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep courses in Redis after exit (default)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed error messages and tracebacks",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress intermediate logging, only show final response",
    )

    args = parser.parse_args()

    # Determine cleanup behavior
    cleanup = args.cleanup and not args.no_cleanup

    # Determine verbose mode (opposite of quiet)
    verbose = not args.quiet

    # Create CLI
    cli = BaselineRAGCLI(cleanup_on_exit=cleanup, debug=args.debug, verbose=verbose)

    try:
        if args.simulate:
            # Simulation mode
            cli.simulation_mode()
        elif args.query:
            # Single query mode
            cli.single_query_mode(args.query)
        else:
            # Interactive mode
            cli.interactive_mode()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if cli.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()