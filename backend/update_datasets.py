#!/usr/bin/env python3
"""
Update existing datasets to include all_samples
"""

from database import db
from dataset_loader import load_any_dataset

def update_dataset_samples():
    """Update existing datasets to include all_samples"""
    print("🔄 Updating existing datasets with all samples...")
    
    # Get all existing datasets
    datasets = db.get_all_datasets()
    
    for dataset in datasets:
        dataset_id = dataset['id']
        dataset_name = dataset['name']
        dataset_source = dataset.get('source', '')
        
        print(f"📊 Processing dataset {dataset_id}: {dataset_name}")
        
        # Check if it already has all_samples
        metadata = dataset.get('metadata', {})
        if 'all_samples' in metadata and len(metadata['all_samples']) > 0:
            print(f"  ✅ Already has {len(metadata['all_samples'])} samples, skipping")
            continue
        
        # Try to reload the dataset
        try:
            # Extract the dataset identifier from source or use dataset_id
            if 'Hugging Face' in dataset_source:
                # Extract HF dataset ID from source
                hf_id = dataset_source.replace('Hugging Face - ', '')
                print(f"  🔄 Reloading Hugging Face dataset: {hf_id}")
                result = load_any_dataset(hf_id, max_samples=1000)
            else:
                # Try using dataset_id as local file
                print(f"  🔄 Reloading local dataset: {dataset_id}")
                result = load_any_dataset(dataset_id, max_samples=1000)
            
            if result.get('success'):
                samples = result['samples']
                print(f"  ✅ Loaded {len(samples)} samples")
                
                # Update the dataset with all_samples
                updated_metadata = metadata.copy()
                updated_metadata['all_samples'] = samples
                updated_metadata['samples_preview'] = samples[:10]  # Update preview too
                
                # Update in database
                db.update_dataset(dataset_id, {
                    'metadata': updated_metadata,
                    'sample_count': len(samples),
                    'loaded_samples': len(samples)
                })
                
                print(f"  🎉 Updated dataset {dataset_id} with {len(samples)} samples")
            else:
                print(f"  ❌ Failed to reload dataset: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Error updating dataset {dataset_id}: {e}")
    
    print("✅ Dataset update completed!")

if __name__ == "__main__":
    update_dataset_samples()
