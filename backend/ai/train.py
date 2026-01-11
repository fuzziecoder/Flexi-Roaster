"""
Training Dataset Generator for AI Model
Generates synthetic training data for failure prediction
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_training_dataset(num_samples: int = 100) -> List[Dict]:
    """
    Generate synthetic training dataset
    
    Features:
    - total_executions
    - failed_executions
    - avg_duration
    - last_7_days_failures
    - stage_count
    
    Target:
    - will_fail (0 or 1)
    """
    dataset = []
    
    for i in range(num_samples):
        # Generate features
        total_executions = random.randint(5, 100)
        
        # Create patterns for failure prediction
        if random.random() < 0.3:  # 30% high-risk pipelines
            failed_executions = random.randint(int(total_executions * 0.3), int(total_executions * 0.7))
            last_7_days_failures = random.randint(3, 10)
            avg_duration = random.uniform(120, 300)
            stage_count = random.randint(7, 15)
            will_fail = 1
        else:  # 70% stable pipelines
            failed_executions = random.randint(0, int(total_executions * 0.1))
            last_7_days_failures = random.randint(0, 2)
            avg_duration = random.uniform(30, 100)
            stage_count = random.randint(3, 7)
            will_fail = 0
        
        sample = {
            'pipeline_id': f'pipe-{i:04d}',
            'total_executions': total_executions,
            'failed_executions': failed_executions,
            'avg_duration': round(avg_duration, 2),
            'last_7_days_failures': last_7_days_failures,
            'stage_count': stage_count,
            'failure_rate': round(failed_executions / total_executions, 3),
            'will_fail': will_fail
        }
        
        dataset.append(sample)
    
    return dataset


def save_dataset(dataset: List[Dict], filename: str = 'training_data.json'):
    """Save dataset to JSON file"""
    with open(filename, 'w') as f:
        json.dump(dataset, f, indent=2)
    print(f"✓ Saved {len(dataset)} samples to {filename}")


def load_dataset(filename: str = 'training_data.json') -> List[Dict]:
    """Load dataset from JSON file"""
    with open(filename, 'r') as f:
        dataset = json.load(f)
    print(f"✓ Loaded {len(dataset)} samples from {filename}")
    return dataset


if __name__ == '__main__':
    # Generate training dataset
    print("Generating training dataset...")
    dataset = generate_training_dataset(num_samples=200)
    
    # Save to file
    save_dataset(dataset, 'backend/ai/training_data.json')
    
    # Print statistics
    high_risk = sum(1 for s in dataset if s['will_fail'] == 1)
    low_risk = len(dataset) - high_risk
    
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(dataset)}")
    print(f"  High-risk pipelines: {high_risk} ({high_risk/len(dataset)*100:.1f}%)")
    print(f"  Stable pipelines: {low_risk} ({low_risk/len(dataset)*100:.1f}%)")
    
    # Print sample
    print(f"\nSample data:")
    print(json.dumps(dataset[0], indent=2))
