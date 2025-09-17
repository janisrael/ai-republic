#!/usr/bin/env python3
"""
Simple API Server for AI Refinement Dashboard
Serves dataset information and training capabilities
"""

import json
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import sys
from dataset_loader import load_any_dataset
from database import db
from training_executor import training_executor
from chromadb_service import chromadb_service
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global variables - removed old datasets_info system

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get all available datasets from database"""
    try:
        datasets = db.get_all_datasets()
        return jsonify({
            'success': True,
            'datasets': datasets,
            'total': len(datasets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Removed old get_dataset_samples function - now using database

@app.route('/api/load-dataset', methods=['POST'])
def load_new_dataset():
    """Load a new dataset from Hugging Face"""
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    
    if not dataset_id:
        return jsonify({
            'success': False,
            'error': 'No dataset_id provided'
        }), 400
    
    try:
        print(f"Loading dataset: {dataset_id}")
        
        # Import and use the new dynamic loader
        from dataset_loader import load_any_dataset
        
        # Load the dataset
        result = load_any_dataset(dataset_id, max_samples=1000)
        
        if result.get('success'):
            # Check if dataset already exists
            existing_dataset = db.get_dataset_by_id(dataset_id)
            if existing_dataset:
                return jsonify({
                    'success': False,
                    'error': f'Dataset {dataset_id} already exists'
                }), 400
            
            # Prepare dataset data for database
            dataset_data = {
                'name': result['name'],
                'description': result['description'],
                'dataset_id': result['dataset_id'],
                'type': 'Text',
                'sample_count': result['total_samples'],
                'loaded_samples': result['loaded_samples'],
                'size': result['size'],
                'format': result['format'],
                'license': 'See Hugging Face',
                'tags': ['hugging-face', 'imported'],
                'source': f'Hugging Face - {dataset_id}',
                'metadata': {
                    'loaded_at': result['loaded_at'],
                    'split_used': result.get('split_used', 'train'),
                    'samples_preview': result['samples'][:10]  # Store first 10 samples as preview
                }
            }
            
            # Save to database
            db_dataset_id = db.add_dataset(dataset_data)
            
            # Get the saved dataset for response
            saved_dataset = db.get_dataset_by_id(dataset_id)
            
            return jsonify({
                'success': True,
                'message': f'Successfully loaded {result["name"]} with {result["loaded_samples"]} samples',
                'dataset': saved_dataset
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error loading dataset')
            }), 500
            
    except Exception as e:
        print(f"Error loading dataset {dataset_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Error loading dataset: {str(e)}'
        }), 500

@app.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    try:
        success = db.delete_dataset(dataset_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Dataset {dataset_id} deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Dataset {dataset_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/datasets/<dataset_id>/favorite', methods=['POST'])
def toggle_favorite(dataset_id):
    """Toggle favorite status of a dataset"""
    try:
        success = db.toggle_favorite(dataset_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Favorite status toggled for dataset {dataset_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Dataset {dataset_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def sanitize_model_name(job_name):
    """Convert job name to valid Ollama model name"""
    # Remove special characters and convert to lowercase
    sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', job_name)
    # Replace spaces with hyphens
    sanitized = re.sub(r'\s+', '-', sanitized)
    # Convert to lowercase
    sanitized = sanitized.lower()
    # Remove multiple hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Add :latest tag if not present
    if not sanitized.endswith(':latest'):
        sanitized += ':latest'
    return sanitized

@app.route('/api/training-jobs', methods=['GET'])
def get_training_jobs():
    """Get all training jobs"""
    try:
        jobs = db.get_all_training_jobs()
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs', methods=['POST'])
def create_training_job():
    """Create a new training job"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('jobName'):
            return jsonify({
                'success': False,
                'error': 'Job name is required'
            }), 400
        
        if not data.get('baseModel'):
            return jsonify({
                'success': False,
                'error': 'Base model is required'
            }), 400
        
        # Generate model name from job name
        model_name = sanitize_model_name(data['jobName'])
        
        # Prepare job data
        job_data = {
            'name': data['jobName'],
            'description': data.get('description', ''),
            'job_type': data.get('jobType', 'experimental'),
            'maker': data.get('maker', ''),
            'version': data.get('version', ''),
            'base_model': data['baseModel'],
            'training_type': data.get('type', 'lora'),
            'status': 'PENDING',
            'progress': 0.0,
            'config': json.dumps(data),
            'model_name': model_name,  # The actual model name that will be created
            'created_at': datetime.now().isoformat()
        }
        
        # Save to database
        job_id = db.add_training_job(job_data)
        
        return jsonify({
            'success': True,
            'message': 'Training job created successfully',
            'job_id': job_id,
            'model_name': model_name,
            'job': job_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>', methods=['PUT'])
def update_training_job(job_id):
    """Update training job status/progress"""
    try:
        data = request.get_json()
        
        # Update job in database
        success = db.update_training_job(job_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training job updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>', methods=['DELETE'])
def delete_training_job(job_id):
    """Delete a training job"""
    try:
        success = db.delete_training_job(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training job deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/start-training', methods=['POST'])
def start_training():
    """Start real training for a job"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({
                'success': False,
                'error': 'Job ID is required'
            }), 400
        
        # Get job data from database
        job = db.get_training_job_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Start real training
        success = training_executor.start_training(job_id, job)
        
        if success:
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': f'Real training started for job: {job["name"]}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start training'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>/start', methods=['POST'])
def start_specific_training(job_id):
    """Start training for a specific job"""
    try:
        # Get job data from database
        job = db.get_training_job_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Start real training
        success = training_executor.start_training(job_id, job)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Training started for job: {job["name"]}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start training'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>/stop', methods=['POST'])
def stop_specific_training(job_id):
    """Stop training for a specific job"""
    try:
        success = training_executor.stop_training(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Training stopped for job {job_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop training or job not running'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>/status', methods=['GET'])
def get_training_status(job_id):
    """Get training status for a specific job"""
    try:
        status = training_executor.get_training_status(job_id)
        
        if status:
            return jsonify({
                'success': True,
                'status': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/evaluations', methods=['GET'])
def get_evaluations():
    """Get all evaluations"""
    try:
        evaluations = db.get_evaluations()
        return jsonify({
            'success': True,
            'evaluations': evaluations,
            'total': len(evaluations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/evaluations', methods=['POST'])
def create_evaluation():
    """Create a new evaluation"""
    data = request.get_json()
    
    try:
        # Validate required fields
        required_fields = ['model_name', 'dataset_id', 'evaluation_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Prepare evaluation data
        eval_data = {
            'model_name': data['model_name'],
            'dataset_id': data['dataset_id'],
            'evaluation_type': data.get('evaluation_type', 'accuracy'),
            'before_metrics': data.get('before_metrics', {}),
            'after_metrics': data.get('after_metrics', {}),
            'improvement': data.get('improvement', 0.0),
            'notes': data.get('notes', '')
        }
        
        # Save to database
        eval_id = db.add_evaluation(eval_data)
        
        return jsonify({
            'success': True,
            'message': 'Evaluation created successfully',
            'evaluation_id': eval_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/evaluations/<int:eval_id>', methods=['PUT'])
def update_evaluation(eval_id):
    """Update an evaluation"""
    data = request.get_json()
    
    try:
        # Prepare update data
        updates = {}
        if 'before_metrics' in data:
            updates['before_metrics'] = data['before_metrics']
        if 'after_metrics' in data:
            updates['after_metrics'] = data['after_metrics']
        if 'improvement' in data:
            updates['improvement'] = data['improvement']
        if 'notes' in data:
            updates['notes'] = data['notes']
        
        # Update in database
        success = db.update_evaluation(eval_id, updates)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Evaluation updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Evaluation not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/evaluations/<int:eval_id>', methods=['DELETE'])
def delete_evaluation(eval_id):
    """Delete an evaluation"""
    try:
        success = db.delete_evaluation(eval_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Evaluation deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Evaluation not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models"""
    try:
        # Try to get models from Ollama
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            # If Ollama is not available, return empty list
            return jsonify({
                'success': True,
                'models': [],
                'total': 0,
                'message': 'Ollama not available or no models installed'
            })
        
        # Parse Ollama list output
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        models = []
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    model_name = parts[0]
                    size = parts[1] if parts[1] != 'latest' else parts[2] if len(parts) > 2 else 'Unknown'
                    modified = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                    
                    # Determine model capabilities based on name
                    capabilities = []
                    if any(keyword in model_name.lower() for keyword in ['code', 'coder', 'codellama']):
                        capabilities.extend(['Coding', 'Code Generation', 'Debugging'])
                    if any(keyword in model_name.lower() for keyword in ['llama', 'qwen', 'mistral']):
                        capabilities.extend(['Reasoning', 'Planning'])
                    if any(keyword in model_name.lower() for keyword in ['llava', 'vision']):
                        capabilities.extend(['Visual Analysis'])
                    if any(keyword in model_name.lower() for keyword in ['chat', 'instruct']):
                        capabilities.extend(['Conversation', 'Instructions'])
                    
                    # Remove duplicates and add default if empty
                    capabilities = list(set(capabilities))
                    if not capabilities:
                        capabilities = ['General Purpose']
                    
                    models.append({
                        'name': model_name,
                        'size': size,
                        'modified': modified,
                        'capabilities': capabilities,
                        'type': 'ollama'
                    })
        
        return jsonify({
            'success': True,
            'models': models,
            'total': len(models)
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout connecting to Ollama'
        }), 408
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Ollama not installed'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ChromaDB API Endpoints
@app.route('/api/chromadb/collections', methods=['GET'])
def get_chromadb_collections():
    """Get all ChromaDB collections"""
    try:
        collections = chromadb_service.list_collections()
        return jsonify({
            'success': True,
            'collections': collections,
            'total': len(collections)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chromadb/collections/<collection_name>', methods=['GET'])
def get_collection_info(collection_name):
    """Get information about a specific collection"""
    try:
        info = chromadb_service.get_collection_info(collection_name)
        return jsonify({
            'success': True,
            'collection': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chromadb/collections/<collection_name>/query', methods=['POST'])
def query_collection(collection_name):
    """Query a ChromaDB collection"""
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text is required'
            }), 400
        
        results = chromadb_service.query_collection(collection_name, query_text, n_results)
        return jsonify({
            'success': True,
            'results': results,
            'query': query_text,
            'n_results': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chromadb/collections/<collection_name>', methods=['DELETE'])
def delete_collection(collection_name):
    """Delete a ChromaDB collection"""
    try:
        success = chromadb_service.delete_collection(collection_name)
        return jsonify({
            'success': success,
            'message': f"Collection '{collection_name}' {'deleted' if success else 'not found'}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chromadb/knowledge-bases/<int:job_id>/query', methods=['POST'])
def query_knowledge_base(job_id):
    """Query a training job's knowledge base"""
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        n_results = data.get('n_results', 3)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text is required'
            }), 400
        
        results = chromadb_service.query_knowledge_base(job_id, query_text, n_results)
        return jsonify({
            'success': True,
            'results': results,
            'job_id': job_id,
            'query': query_text,
            'n_results': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Get dataset count from database
        datasets = db.get_all_datasets()
        
        # Get ChromaDB collections count
        chromadb_collections = chromadb_service.list_collections()
        
        return jsonify({
            'status': 'healthy',
            'datasets_loaded': True,
            'total_datasets': len(datasets),
            'chromadb_collections': len(chromadb_collections),
            'database': 'connected',
            'chromadb': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': 'disconnected',
            'chromadb': 'disconnected'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting AI Refinement Dashboard API Server...")
    print("📊 Database initialized...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📋 Available endpoints:")
    print("  GET  /api/datasets - List all datasets")
    print("  POST /api/load-dataset - Load new dataset")
    print("  GET  /api/models - Get Ollama models")
    print("  GET  /api/training-jobs - Get training jobs")
    print("  POST /api/training-jobs - Create training job")
    print("  PUT  /api/training-jobs/<id> - Update training job")
    print("  DELETE /api/training-jobs/<id> - Delete training job")
    print("  POST /api/start-training - Start training")
    print("  GET  /api/health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
