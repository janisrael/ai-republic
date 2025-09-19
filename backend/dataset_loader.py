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

def check_and_convert_dataset_format(sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check dataset format and convert to standard LoRA format if needed
    Returns format analysis and converted samples
    """
    if not sample_data:
        return {
            'format_type': 'empty',
            'is_lora_compatible': False,
            'converted_samples': [],
            'conversion_applied': False,
            'format_analysis': 'No samples found'
        }
    
    # Analyze first sample to determine format
    first_sample = sample_data[0]
    sample_keys = list(first_sample.keys())
    
    print(f"📊 Analyzing dataset format. Sample keys: {sample_keys}")
    
    # Check if it's already in standard LoRA format
    if 'instruction' in sample_keys and 'output' in sample_keys:
        print("✅ Dataset is already in standard LoRA format")
        return {
            'format_type': 'standard_lora',
            'is_lora_compatible': True,
            'converted_samples': sample_data,
            'conversion_applied': False,
            'format_analysis': 'Standard LoRA format (instruction/output fields)'
        }
    
    # Check if it's in Devops format (content field with JSON string)
    if 'content' in sample_keys:
        print("🔄 Converting Devops format to LoRA format...")
        converted_samples = []
        conversion_count = 0
        
        for sample in sample_data:
            try:
                # Parse the content field
                content = sample.get('content', '')
                if isinstance(content, str):
                    # Try to parse as JSON string
                    import ast
                    try:
                        # Handle single quotes in JSON-like string
                        content_dict = ast.literal_eval(content)
                        
                        # Extract fields with various possible names
                        instruction = (content_dict.get('Instruction') or 
                                     content_dict.get('instruction') or 
                                     content_dict.get('Prompt') or 
                                     content_dict.get('prompt') or '')
                        
                        output = (content_dict.get('Response') or 
                                content_dict.get('response') or 
                                content_dict.get('Output') or 
                                content_dict.get('output') or '')
                        
                        if instruction and output:
                            converted_sample = {
                                'id': sample.get('id', ''),
                                'instruction': instruction,
                                'output': output,
                                'input': content_dict.get('input', ''),
                                'system': content_dict.get('system', ''),
                                'source': sample.get('source', ''),
                                'type': sample.get('type', 'Text')
                            }
                            converted_samples.append(converted_sample)
                            conversion_count += 1
                        else:
                            print(f"⚠️ Skipping sample {sample.get('id', 'unknown')}: missing instruction or output")
                    except (ValueError, SyntaxError) as e:
                        print(f"⚠️ Failed to parse content for sample {sample.get('id', 'unknown')}: {e}")
                        continue
                else:
                    print(f"⚠️ Content field is not a string for sample {sample.get('id', 'unknown')}")
                    continue
            except Exception as e:
                print(f"⚠️ Error converting sample {sample.get('id', 'unknown')}: {e}")
                continue
        
        print(f"✅ Converted {conversion_count} out of {len(sample_data)} samples")
        
        return {
            'format_type': 'devops_format',
            'is_lora_compatible': len(converted_samples) > 0,
            'converted_samples': converted_samples,
            'conversion_applied': True,
            'format_analysis': f'Devops format converted to LoRA format ({conversion_count}/{len(sample_data)} samples)',
            'conversion_stats': {
                'total_samples': len(sample_data),
                'converted_samples': conversion_count,
                'failed_samples': len(sample_data) - conversion_count
            }
        }
    
    # Check for other possible formats
    if 'question' in sample_keys and 'answer' in sample_keys:
        print("🔄 Converting Q&A format to LoRA format...")
        converted_samples = []
        
        for sample in sample_data:
            converted_sample = {
                'id': sample.get('id', ''),
                'instruction': sample.get('question', ''),
                'output': sample.get('answer', ''),
                'input': '',
                'system': '',
                'source': sample.get('source', ''),
                'type': sample.get('type', 'Text')
            }
            converted_samples.append(converted_sample)
        
        return {
            'format_type': 'qa_format',
            'is_lora_compatible': True,
            'converted_samples': converted_samples,
            'conversion_applied': True,
            'format_analysis': f'Q&A format converted to LoRA format ({len(converted_samples)} samples)'
        }
    
    # Unknown format - try to extract any available fields
    print("⚠️ Unknown format detected. Attempting basic conversion...")
    converted_samples = []
    
    for sample in sample_data:
        # Try to find instruction-like and output-like fields
        instruction_fields = ['text', 'input', 'prompt', 'question']
        output_fields = ['response', 'answer', 'code', 'solution']
        
        instruction = ''
        output = ''
        
        for field in instruction_fields:
            if field in sample and sample[field]:
                instruction = str(sample[field])
                break
        
        for field in output_fields:
            if field in sample and sample[field]:
                output = str(sample[field])
                break
        
        if instruction or output:
            converted_sample = {
                'id': sample.get('id', ''),
                'instruction': instruction,
                'output': output,
                'input': '',
                'system': '',
                'source': sample.get('source', ''),
                'type': sample.get('type', 'Text')
            }
            converted_samples.append(converted_sample)
    
    return {
        'format_type': 'unknown_format',
        'is_lora_compatible': len(converted_samples) > 0,
        'converted_samples': converted_samples,
        'conversion_applied': True,
        'format_analysis': f'Unknown format - basic conversion attempted ({len(converted_samples)} samples converted)',
        'available_fields': sample_keys
    }

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
        
        # 🎯 NEW: Check and convert dataset format
        print("🔍 Checking dataset format compatibility...")
        format_analysis = check_and_convert_dataset_format(sample_data)
        
        # Use converted samples if conversion was applied
        if format_analysis['conversion_applied']:
            sample_data = format_analysis['converted_samples']
            print(f"✅ Format conversion applied: {format_analysis['format_analysis']}")
        else:
            print(f"ℹ️ No conversion needed: {format_analysis['format_analysis']}")
        
        # Estimate size
        avg_sample_size = len(str(sample_data[0])) if sample_data else 0
        estimated_size = (avg_sample_size * total_samples) / (1024 * 1024)  # MB
        
        # Prepare metadata with format analysis
        metadata = {
            'format_analysis': format_analysis,
            'all_samples': sample_data,
            'split_used': split_name
        }
        
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
            'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': metadata,
            'is_lora_compatible': format_analysis['is_lora_compatible'],
            'format_type': format_analysis['format_type']
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
