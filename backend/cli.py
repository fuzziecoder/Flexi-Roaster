"""
CLI interface for FlexiRoaster Pipeline Engine.
Allows testing pipeline execution from command line.
"""
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.pipeline_engine import PipelineEngine
from backend.core.executor import PipelineExecutor
from backend.models.pipeline import LogLevel


def execute_pipeline(pipeline_path: str, verbose: bool = False):
    """Execute a pipeline from a YAML/JSON file"""
    print(f"\n{'='*60}")
    print(f"FlexiRoaster Pipeline Executor")
    print(f"{'='*60}\n")
    
    try:
        # Parse pipeline
        print(f"📄 Loading pipeline from: {pipeline_path}")
        engine = PipelineEngine()
        pipeline = engine.parse_pipeline(pipeline_path)
        print(f"✅ Pipeline loaded: {pipeline.name}")
        print(f"   Description: {pipeline.description}")
        print(f"   Stages: {len(pipeline.stages)}")
        
        # Validate pipeline
        print(f"\n🔍 Validating pipeline...")
        is_valid, errors = engine.validate_pipeline(pipeline)
        if not is_valid:
            print(f"❌ Pipeline validation failed:")
            for error in errors:
                print(f"   - {error}")
            return 1
        print(f"✅ Pipeline validation passed")
        
        # Execute pipeline
        print(f"\n🚀 Executing pipeline...\n")
        executor = PipelineExecutor()
        execution = executor.execute(pipeline)
        
        # Print execution results
        print(f"\n{'='*60}")
        print(f"Execution Results")
        print(f"{'='*60}")
        print(f"Status: {execution.status.value}")
        print(f"Duration: {execution.duration:.2f}s" if execution.duration else "Duration: N/A")
        print(f"Stages Completed: {execution.stages_completed}/{execution.total_stages}")
        
        if execution.error:
            print(f"\n❌ Error: {execution.error}")
        
        # Print logs
        if verbose or execution.status.value == 'failed':
            print(f"\n{'='*60}")
            print(f"Execution Logs")
            print(f"{'='*60}")
            for log in execution.logs:
                level_emoji = {
                    'INFO': 'ℹ️',
                    'WARN': '⚠️',
                    'ERROR': '❌',
                    'DEBUG': '🔧'
                }.get(log.level.value, '📝')
                
                stage_info = f"[{log.stage_id}]" if log.stage_id else "[SYSTEM]"
                print(f"{level_emoji} {log.timestamp.strftime('%H:%M:%S')} {stage_info} {log.message}")
        
        # Return appropriate exit code
        return 0 if execution.status.value == 'completed' else 1
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def list_examples():
    """List available example pipelines"""
    examples_dir = Path(__file__).parent / "backend" / "examples"
    if not examples_dir.exists():
        print("No examples directory found")
        return
    
    print("\nAvailable example pipelines:")
    for file in examples_dir.glob("*.yaml"):
        print(f"  - {file.name}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FlexiRoaster Pipeline Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.cli execute --pipeline examples/sample.yaml
  python -m backend.cli execute --pipeline examples/sample.yaml --verbose
  python -m backend.cli list-examples
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute a pipeline')
    execute_parser.add_argument(
        '--pipeline',
        '-p',
        required=True,
        help='Path to pipeline YAML/JSON file'
    )
    execute_parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show detailed logs'
    )
    
    # List examples command
    subparsers.add_parser('list-examples', help='List available example pipelines')
    
    args = parser.parse_args()
    
    if args.command == 'execute':
        sys.exit(execute_pipeline(args.pipeline, args.verbose))
    elif args.command == 'list-examples':
        list_examples()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
