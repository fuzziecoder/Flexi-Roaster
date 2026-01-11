"""
CLI for testing pipeline execution
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.pipeline_engine import PipelineEngine
from backend.core.executor import PipelineExecutor


def main():
    parser = argparse.ArgumentParser(description='FlexiRoaster Pipeline CLI')
    parser.add_argument('command', choices=['execute', 'validate', 'list'], help='Command to run')
    parser.add_argument('--pipeline', '-p', help='Pipeline file path (YAML/JSON)')
    parser.add_argument('--id', help='Pipeline ID (for execute)')
    
    args = parser.parse_args()
    
    engine = PipelineEngine()
    executor = PipelineExecutor()
    
    if args.command == 'execute':
        if not args.pipeline:
            print("Error: --pipeline required for execute command")
            sys.exit(1)
        
        try:
            # Load pipeline
            print(f"Loading pipeline from: {args.pipeline}")
            if args.pipeline.endswith('.yaml') or args.pipeline.endswith('.yml'):
                pipeline = engine.load_from_yaml(args.pipeline)
            else:
                pipeline = engine.load_from_json(args.pipeline)
            
            print(f"Pipeline loaded: {pipeline.name} (ID: {pipeline.id})")
            print(f"Stages: {len(pipeline.stages)}")
            
            # Create execution
            execution = engine.create_execution(pipeline.id)
            print(f"\nExecution ID: {execution.id}")
            print(f"Status: {execution.status}")
            
            # Execute pipeline
            print("\n" + "="*50)
            print("EXECUTING PIPELINE")
            print("="*50 + "\n")
            
            result = executor.execute(pipeline, execution)
            
            # Print results
            print("\n" + "="*50)
            print("EXECUTION RESULTS")
            print("="*50)
            print(f"Status: {result.status}")
            print(f"Duration: {result.duration:.2f}s")
            
            if result.error:
                print(f"Error: {result.error}")
            
            print(f"\nStages executed: {len(result.stage_executions)}")
            for stage_exec in result.stage_executions:
                status_symbol = "✓" if stage_exec.status == "completed" else "✗"
                print(f"  {status_symbol} {stage_exec.stage_id}: {stage_exec.status} ({stage_exec.duration:.2f}s)")
            
            # Print logs
            if 'logs' in result.context:
                print("\n" + "="*50)
                print("EXECUTION LOGS")
                print("="*50)
                for log in result.context['logs']:
                    print(log)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.command == 'validate':
        if not args.pipeline:
            print("Error: --pipeline required for validate command")
            sys.exit(1)
        
        try:
            # Load pipeline
            if args.pipeline.endswith('.yaml') or args.pipeline.endswith('.yml'):
                pipeline = engine.load_from_yaml(args.pipeline)
            else:
                pipeline = engine.load_from_json(args.pipeline)
            
            # Validate
            is_valid, error = engine.validate_pipeline(pipeline)
            
            if is_valid:
                print(f"✓ Pipeline '{pipeline.name}' is valid")
                print(f"  Stages: {len(pipeline.stages)}")
            else:
                print(f"✗ Pipeline validation failed: {error}")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == 'list':
        pipelines = engine.list_pipelines()
        if not pipelines:
            print("No pipelines loaded")
        else:
            print(f"Loaded pipelines: {len(pipelines)}")
            for p in pipelines:
                print(f"  - {p.name} (ID: {p.id}, Stages: {len(p.stages)})")


if __name__ == '__main__':
    main()
