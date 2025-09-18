#!/usr/bin/env python3
"""
Dataset Loader for AI Refinement Dashboard
Loads Hugging Face datasets and makes them available via API
"""

import json
from datasets import load_dataset
from typing import Dict, List, Any
import argparse
import os
import time

def load_python_dataset() -> Dict[str, Any]:
    """Load the Python code dataset from Hugging Face"""
    print("Loading Python code dataset...")
    ds = load_dataset('jtatman/python-code-dataset-500k')
    
    # Get sample data
    sample_data = []
    for i in range(min(100, len(ds['train']))):  # Get first 100 samples
        sample = ds['train'][i]
        sample_data.append({
            'id': f'python-{i}',
            'instruction': sample.get('instruction', ''),
            'output': sample.get('output', ''),
            'system': sample.get('system', ''),
            'type': 'Python Code',
            'source': 'Hugging Face - jtatman/python-code-dataset-500k'
        })
    
    return {
        'name': 'Python Code Dataset',
        'description': 'Python code snippets with instructions and outputs',
        'total_samples': len(ds['train']),
        'samples': sample_data,
        'format': 'JSONL',
        'size': f'{len(ds["train"]):,} samples'
    }

def load_javascript_dataset() -> Dict[str, Any]:
    """Load a JavaScript dataset (if available)"""
    try:
        print("Loading JavaScript dataset...")
        ds = load_dataset('axay/javascript-dataset')
        
        sample_data = []
        for i in range(min(100, len(ds['train']))):
            sample = ds['train'][i]
            sample_data.append({
                'id': f'js-{i}',
                'code': sample.get('code', ''),
                'description': sample.get('description', ''),
                'type': 'JavaScript Code',
                'source': 'Hugging Face - axay/javascript-dataset'
            })
        
        return {
            'name': 'JavaScript Dataset',
            'description': 'JavaScript code snippets',
            'total_samples': len(ds['train']),
            'samples': sample_data,
            'format': 'JSONL',
            'size': f'{len(ds["train"]):,} samples'
        }
    except Exception as e:
        print(f"JavaScript dataset not available: {e}")
        return None

def load_any_dataset(dataset_id: str, max_samples: int = 1000) -> Dict[str, Any]:
    """Load any Hugging Face dataset by ID or local file"""
    try:
        print(f"Loading dataset: {dataset_id}")
        
        # Check if it's a local file first
        if dataset_id.endswith('.json'):
            return load_local_json_dataset(dataset_id, max_samples)
        
        # Load the dataset from Hugging Face
        ds = load_dataset(dataset_id)
        
        # Determine which split to use
        split_name = 'train' if 'train' in ds else list(ds.keys())[0]
        dataset_split = ds[split_name]
        
        # Get sample data
        sample_data = []
        total_samples = len(dataset_split)
        samples_to_load = min(max_samples, total_samples) if max_samples is not None else total_samples
        
        print(f"Loading {samples_to_load} samples from {total_samples} total...")
        
        for i in range(samples_to_load):
            sample = dataset_split[i]
            
            # Try to extract common fields with fallbacks
            sample_item = {
                'id': f'{dataset_id.replace("/", "-")}-{i}',
                'type': 'Code' if 'code' in str(sample).lower() else 'Text',
                'source': f'Hugging Face - {dataset_id}'
            }
            
            # Extract instruction/input
            for field in ['instruction', 'input', 'prompt', 'question', 'text']:
                if field in sample:
                    sample_item['instruction'] = str(sample[field])
                    break
            
            # Extract output/target
            for field in ['output', 'target', 'answer', 'response', 'code', 'solution']:
                if field in sample:
                    sample_item['output'] = str(sample[field])
                    break
            
            # Extract system prompt if available
            if 'system' in sample:
                sample_item['system'] = str(sample['system'])
            
            # If no instruction/output found, use all available fields
            if 'instruction' not in sample_item:
                sample_item['content'] = str(sample)
            
            sample_data.append(sample_item)
        
        # Estimate size
        avg_sample_size = len(str(sample_data[0])) if sample_data else 0
        estimated_size = (avg_sample_size * total_samples) / (1024 * 1024)  # MB
        
        return {
            'success': True,
            'name': dataset_id.split('/')[-1].replace('-', ' ').replace('_', ' ').title(),
            'description': f'Dataset loaded from Hugging Face: {dataset_id}',
            'dataset_id': dataset_id,
            'total_samples': total_samples,
            'loaded_samples': len(sample_data),
            'samples': sample_data,
            'format': 'Hugging Face Dataset',
            'size': f'{estimated_size:.1f} MB (estimated)',
            'split_used': split_name,
            'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"Error loading dataset {dataset_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'dataset_id': dataset_id
        }

def save_dataset_json(dataset_info: Dict[str, Any], filename: str):
    """Save dataset info to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, indent=2, ensure_ascii=False)
    print(f"Dataset saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Load datasets for AI training')
    parser.add_argument('--dataset', choices=['python', 'javascript', 'all'], 
                       default='python', help='Dataset to load')
    parser.add_argument('--output', default='dataset_info.json', 
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    datasets = []
    
    if args.dataset in ['python', 'all']:
        python_data = load_python_dataset()
        datasets.append(python_data)
        save_dataset_json(python_data, 'python_dataset.json')
    
    if args.dataset in ['javascript', 'all']:
        js_data = load_javascript_dataset()
        if js_data:
            datasets.append(js_data)
            save_dataset_json(js_data, 'javascript_dataset.json')
    
    # Save combined info
    save_dataset_json({
        'datasets': datasets,
        'total_datasets': len(datasets),
        'loaded_at': str(pd.Timestamp.now()) if 'pd' in globals() else '2024-01-16'
    }, args.output)
    
    print(f"\n✅ Successfully loaded {len(datasets)} dataset(s)")
    for dataset in datasets:
        print(f"  - {dataset['name']}: {dataset['size']}")

def load_local_json_dataset(file_path: str, max_samples: int = 1000) -> Dict[str, Any]:
    """Load a local JSON dataset file"""
    try:
        import os
        full_path = os.path.join('dataset', file_path)
        
        if not os.path.exists(full_path):
            return {
                'success': False,
                'error': f'Local file {file_path} not found'
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'datasets' in data:
            # Our dataset_info.json format
            datasets = data['datasets']
            if datasets:
                dataset = datasets[0]  # Take first dataset
                samples = dataset.get('samples', [])
                
                # Limit samples
                limited_samples = samples[:max_samples] if max_samples is not None else samples
                
                return {
                    'success': True,
                    'name': dataset.get('name', 'Local Dataset'),
                    'description': dataset.get('description', 'Local dataset'),
                    'dataset_id': file_path,
                    'total_samples': len(samples),
                    'loaded_samples': len(limited_samples),
                    'samples': limited_samples,
                    'format': 'JSON',
                    'size': f'{len(samples):,} samples',
                    'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
        elif isinstance(data, dict) and 'samples' in data:
            # Direct dataset format with samples array
            samples = data.get('samples', [])
            limited_samples = samples[:max_samples] if max_samples is not None else samples
            
            return {
                'success': True,
                'name': data.get('name', 'Local Dataset'),
                'description': data.get('description', 'Local dataset'),
                'dataset_id': file_path,
                'total_samples': len(samples),
                'loaded_samples': len(limited_samples),
                'samples': limited_samples,
                'format': 'JSON',
                'size': f'{len(samples):,} samples',
                'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        elif isinstance(data, list):
            # Direct list of samples
            limited_samples = data[:max_samples] if max_samples is not None else data
            return {
                'success': True,
                'name': 'Local Dataset',
                'description': 'Local dataset from JSON file',
                'dataset_id': file_path,
                'total_samples': len(data),
                'loaded_samples': len(limited_samples),
                'samples': limited_samples,
                'format': 'JSON',
                'size': f'{len(data):,} samples',
                'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return {
            'success': False,
            'error': 'Unknown JSON format'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error loading local file: {str(e)}'
        }

if __name__ == '__main__':
    main()
