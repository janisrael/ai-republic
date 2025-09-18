#!/usr/bin/env python3
"""
Test script to fix LoRA training issues
Generates proper training data and tests the fixed training script
"""

import os
import json
from database import db

def create_test_training_data():
    """Create proper test training data"""
    print("🔄 Creating test training data...")
    
    # Create training data directory
    train_dir = "training_data/job_test"
    os.makedirs(train_dir, exist_ok=True)
    
    # Sample training data in proper format
    train_samples = [
        {
            "instruction": "Write a Python function to calculate the factorial of a number",
            "input": "5",
            "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nresult = factorial(5)\nprint(result)  # Output: 120"
        },
        {
            "instruction": "Create a function to reverse a string",
            "input": "hello",
            "output": "def reverse_string(s):\n    return s[::-1]\n\nresult = reverse_string('hello')\nprint(result)  # Output: olleh"
        },
        {
            "instruction": "Write a function to check if a number is prime",
            "input": "17",
            "output": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nresult = is_prime(17)\nprint(result)  # Output: True"
        },
        {
            "instruction": "Create a function to find the maximum element in a list",
            "input": "[3, 7, 2, 9, 1]",
            "output": "def find_max(lst):\n    if not lst:\n        return None\n    max_val = lst[0]\n    for num in lst:\n        if num > max_val:\n            max_val = num\n    return max_val\n\nresult = find_max([3, 7, 2, 9, 1])\nprint(result)  # Output: 9"
        },
        {
            "instruction": "Write a function to count vowels in a string",
            "input": "programming",
            "output": "def count_vowels(s):\n    vowels = 'aeiouAEIOU'\n    count = 0\n    for char in s:\n        if char in vowels:\n            count += 1\n    return count\n\nresult = count_vowels('programming')\nprint(result)  # Output: 3"
        }
    ]
    
    val_samples = [
        {
            "instruction": "Create a function to calculate the sum of two numbers",
            "input": "10, 20",
            "output": "def add_numbers(a, b):\n    return a + b\n\nresult = add_numbers(10, 20)\nprint(result)  # Output: 30"
        },
        {
            "instruction": "Write a function to check if a string is a palindrome",
            "input": "racecar",
            "output": "def is_palindrome(s):\n    return s == s[::-1]\n\nresult = is_palindrome('racecar')\nprint(result)  # Output: True"
        }
    ]
    
    # Save training data
    with open(os.path.join(train_dir, 'train.jsonl'), 'w') as f:
        for sample in train_samples:
            f.write(json.dumps(sample) + '\n')
    
    with open(os.path.join(train_dir, 'val.jsonl'), 'w') as f:
        for sample in val_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"✅ Created test training data: {len(train_samples)} train, {len(val_samples)} val samples")
    return train_dir

def test_dataset_conversion():
    """Test the dataset conversion process"""
    print("🔄 Testing dataset conversion...")
    
    # Get available datasets
    datasets = db.get_all_datasets()
    print(f"📊 Available datasets: {len(datasets)}")
    
    for dataset in datasets:
        print(f"Dataset: {dataset['name']} (ID: {dataset['id']})")
        metadata = dataset.get('metadata', {})
        samples_preview = metadata.get('samples_preview', [])
        print(f"  Samples: {len(samples_preview)}")
        
        if samples_preview:
            # Show first sample
            sample = samples_preview[0]
            print(f"  First sample keys: {list(sample.keys())}")
            if 'instruction' in sample:
                print(f"  Instruction: {sample['instruction'][:50]}...")
            if 'output' in sample:
                print(f"  Output: {sample['output'][:50]}...")

def main():
    print("🚀 Testing LoRA Fix")
    print("=" * 50)
    
    # Test dataset conversion
    test_dataset_conversion()
    print()
    
    # Create test training data
    train_dir = create_test_training_data()
    print()
    
    # Test data files
    train_file = os.path.join(train_dir, 'train.jsonl')
    val_file = os.path.join(train_dir, 'val.jsonl')
    
    print(f"📊 Training data file size: {os.path.getsize(train_file)} bytes")
    print(f"📊 Validation data file size: {os.path.getsize(val_file)} bytes")
    
    # Show first few lines
    print("\n📝 First training sample:")
    with open(train_file, 'r') as f:
        first_line = f.readline()
        sample = json.loads(first_line)
        print(f"Instruction: {sample['instruction']}")
        print(f"Input: {sample['input']}")
        print(f"Output: {sample['output'][:100]}...")
    
    print("\n✅ Test data creation completed!")
    print("Now you can run the fixed training script with this data.")

if __name__ == "__main__":
    main()
