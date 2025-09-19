#!/usr/bin/env python3
"""
Simple API Server for AI Refinement Dashboard
Serves dataset information and training capabilities
"""

import json
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import sys
from dataset_loader import load_any_dataset
from database import db
from training_executor import TrainingExecutor
from chromadb_service import chromadb_service
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable SocketIO with CORS

# Initialize training executor
training_executor = TrainingExecutor()

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
    dataset_id = None
    try:
        data = request.get_json()
        print(f"Raw request data: {data}")
        print(f"Data type: {type(data)}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
            
        dataset_id = data.get('dataset_id')
        custom_name = data.get('custom_name')
        custom_description = data.get('custom_description')
        
        print(f"Dataset ID extracted: {dataset_id}")
        print(f"Custom name: {custom_name}")
        print(f"Custom description: {custom_description}")
        
        if not dataset_id:
            return jsonify({
                'success': False,
                'error': 'No dataset_id provided'
            }), 400
        
        print(f"Loading dataset: {dataset_id}")
        print(f"Dataset ID type: {type(dataset_id)}")
        print(f"Dataset ID value: {repr(dataset_id)}")
        
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
                'name': custom_name if custom_name else result['name'],
                'description': custom_description if custom_description else result['description'],
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
                    'samples_preview': result['samples'][:10],  # Store first 10 samples as preview
                    'all_samples': result['samples'],  # Store all samples for training
                    'format_analysis': result['metadata'].get('format_analysis')  # Include format analysis!
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
        print(f"Exception type: {type(e)}")
        print(f"Exception args: {e.args}")
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


def get_model_details_from_ollama(model_name):
    """Get detailed model information from ollama show command"""
    try:
        result = subprocess.run(['ollama', 'show', model_name], capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            # Fallback to basic capabilities if ollama show fails
            return get_fallback_model_details(model_name)
        
        output = result.stdout
        details = {
            'capabilities': [],
            'architecture': 'Unknown',
            'parameters': 'Unknown',
            'context_length': 'Unknown',
            'quantization': 'Unknown',
            'temperature': 0.7,
            'top_p': 0.9,
            'system_prompt': '',
            'license': 'Unknown'
        }
        
        # Parse capabilities section
        capabilities_match = re.search(r'Capabilities\s*\n((?:\s+\w+\s*\n?)+)', output)
        if capabilities_match:
            capabilities_text = capabilities_match.group(1)
            capabilities = re.findall(r'\s+(\w+)', capabilities_text)
            details['capabilities'] = capabilities
        
        # Parse architecture
        arch_match = re.search(r'architecture\s+(\w+)', output)
        if arch_match:
            details['architecture'] = arch_match.group(1)
        
        # Parse parameters
        param_match = re.search(r'parameters\s+([\d.]+[BMK]?)', output)
        if param_match:
            details['parameters'] = param_match.group(1)
        
        # Parse context length
        ctx_match = re.search(r'context length\s+(\d+)', output)
        if ctx_match:
            details['context_length'] = int(ctx_match.group(1))
        
        # Parse quantization
        quant_match = re.search(r'quantization\s+(\w+)', output)
        if quant_match:
            details['quantization'] = quant_match.group(1)
        
        # Parse temperature
        temp_match = re.search(r'temperature\s+([\d.]+)', output)
        if temp_match:
            details['temperature'] = float(temp_match.group(1))
        
        # Parse top_p
        top_p_match = re.search(r'top_p\s+([\d.]+)', output)
        if top_p_match:
            details['top_p'] = float(top_p_match.group(1))
        
        # Parse system prompt
        system_match = re.search(r'System\s*\n(.+?)(?:\n\s*\n|\n\s*License|\n\s*Parameters)', output, re.DOTALL)
        if system_match:
            details['system_prompt'] = system_match.group(1).strip()
        
        # Parse license
        license_match = re.search(r'License\s*\n(.+?)(?:\n\s*\n|\Z)', output, re.DOTALL)
        if license_match:
            details['license'] = license_match.group(1).strip().split('\n')[0]
        
        # Add specialized capabilities from system prompt
        if details['system_prompt']:
            specialized_caps = extract_capabilities_from_prompt(details['system_prompt'])
            details['capabilities'].extend(specialized_caps)
        
        # Add architecture-based capabilities
        arch_caps = get_architecture_capabilities(details['architecture'])
        details['capabilities'].extend(arch_caps)
        
        # Remove duplicates and ensure we have at least one capability
        details['capabilities'] = list(set(details['capabilities']))
        if not details['capabilities']:
            details['capabilities'] = ['General Purpose']
        
        return details
        
    except Exception as e:
        print(f"Error getting model details for {model_name}: {e}")
        return get_fallback_model_details(model_name)

def get_fallback_model_details(model_name):
    """Fallback model details when ollama show fails"""
    capabilities = []
    
    # Basic pattern matching as fallback
    if any(keyword in model_name.lower() for keyword in ['code', 'coder', 'codellama']):
        capabilities.extend(['Coding', 'Code Generation', 'Debugging'])
    if any(keyword in model_name.lower() for keyword in ['llama', 'qwen', 'mistral']):
        capabilities.extend(['Reasoning', 'Planning'])
    if any(keyword in model_name.lower() for keyword in ['llava', 'vision']):
        capabilities.extend(['Visual Analysis'])
    if any(keyword in model_name.lower() for keyword in ['chat', 'instruct']):
        capabilities.extend(['Conversation', 'Instructions'])
    
    if not capabilities:
        capabilities = ['General Purpose']
    
    return {
        'capabilities': capabilities,
        'architecture': 'Unknown',
        'parameters': 'Unknown',
        'context_length': 'Unknown',
        'quantization': 'Unknown',
        'temperature': 0.7,
        'top_p': 0.9,
        'system_prompt': '',
        'license': 'Unknown'
    }

def extract_capabilities_from_prompt(system_prompt):
    """Extract specialized capabilities from system prompt"""
    capabilities = []
    prompt_lower = system_prompt.lower()
    
    # Common capability keywords
    capability_keywords = {
        'debugging': 'Debugging',
        'code analysis': 'Code Analysis',
        'programming': 'Programming',
        'mathematics': 'Mathematics',
        'reasoning': 'Reasoning',
        'planning': 'Planning',
        'conversation': 'Conversation',
        'instruction': 'Instruction Following',
        'creative': 'Creative Writing',
        'analysis': 'Analysis',
        'problem solving': 'Problem Solving',
        'devops': 'DevOps',
        'kubernetes': 'Kubernetes',
        'docker': 'Docker',
        'ci/cd': 'CI/CD'
    }
    
    for keyword, capability in capability_keywords.items():
        if keyword in prompt_lower:
            capabilities.append(capability)
    
    return capabilities

def get_architecture_capabilities(architecture):
    """Get capabilities based on model architecture"""
    arch_capabilities = {
        'llama': ['Reasoning', 'Planning'],
        'mistral': ['Reasoning', 'Efficiency'],
        'qwen': ['Multilingual', 'Reasoning'],
        'phi': ['Efficiency', 'Reasoning'],
        'gemma': ['Efficiency', 'Reasoning']
    }
    
    return arch_capabilities.get(architecture.lower(), [])

def sanitize_model_name(job_name, version=''):
    """Convert job name to valid Ollama model name with version"""
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
    
    # Add version if provided, otherwise add :latest
    if version and version.strip():
        version_clean = re.sub(r'[^a-zA-Z0-9\-_.]', '-', version.strip())
        version_clean = version_clean.lower()
        sanitized += f':{version_clean}'
    else:
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
        # Handle both JSON and FormData requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData request (with avatar)
            training_data_str = request.form.get('trainingData')
            if not training_data_str:
                return jsonify({
                    'success': False,
                    'error': 'Training data is required'
                }), 400
            
            data = json.loads(training_data_str)
            avatar_file = request.files.get('avatar')
        else:
            # Regular JSON request
            data = request.get_json()
            avatar_file = None
        
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
        
        # Generate model name from job name and version
        model_name = sanitize_model_name(data['jobName'], data.get('version', ''))
        
        # Prepare job data
        job_data = {
            'name': data['jobName'],
            'description': data.get('description', ''),
            'custom_capabilities': data.get('customCapabilities', []),
            'maker': data.get('maker', ''),
            'version': data.get('version', ''),
            'base_model': data['baseModel'],
            'training_type': data.get('training_type', data.get('type', 'lora')),
            'temperature': data.get('temperature', 0.7),
            'top_p': data.get('top_p', 0.9),
            'context_length': data.get('context_length', 4096),
            'status': 'PENDING',
            'progress': 0.0,
            'config': json.dumps(data),
            'model_name': model_name,  # The actual model name that will be created
            'created_at': datetime.now().isoformat()
        }
        
        # Save to database
        job_id = db.add_training_job(job_data)
        
        # Handle avatar upload if provided
        avatar_url = None
        if avatar_file:
            try:
                from werkzeug.utils import secure_filename
                import os
                import uuid
                from PIL import Image
                
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                if not ('.' in avatar_file.filename and 
                        avatar_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                    print(f"Warning: Invalid avatar file type for job {job_id}")
                else:
                    # Create avatars directory
                    avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
                    os.makedirs(avatars_dir, exist_ok=True)
                    
                    # Generate unique filename
                    file_extension = avatar_file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{secure_filename(model_name)}_{uuid.uuid4().hex[:8]}.{file_extension}"
                    file_path = os.path.join(avatars_dir, unique_filename)
                    
                    # Save file
                    avatar_file.save(file_path)
                    
                    # Resize image to standard avatar size (128x128)
                    try:
                        with Image.open(file_path) as img:
                            img = img.convert('RGB')
                            img = img.resize((128, 128), Image.Resampling.LANCZOS)
                            img.save(file_path, 'JPEG', quality=85)
                    except Exception as e:
                        print(f"Warning: Could not resize avatar image: {e}")
                    
                    # Generate URL
                    avatar_url = f"/api/avatars/{unique_filename}"
                    
                    # Create model profile with avatar
                    profile_data = {
                        'model_name': model_name,
                        'training_job_id': job_id,
                        'avatar_path': file_path,
                        'avatar_url': avatar_url
                    }
                    db.add_model_profile(profile_data)
                    print(f"✅ Created model profile with avatar for {model_name}")
                    
            except Exception as e:
                print(f"Warning: Failed to process avatar for job {job_id}: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Training job created successfully',
            'job_id': job_id,
            'model_name': model_name,
            'job': job_data,
            'avatar_url': avatar_url
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
    """Delete a training job and clean up associated resources"""
    try:
        # Get job details before deletion for cleanup
        job = db.get_training_job(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Clean up associated resources
        cleanup_results = []
        
        # 1. Delete ChromaDB collection if it's a RAG training job
        if job.get('training_type') == 'rag':
            try:
                collection_name = f"knowledge_base_job_{job_id}"
                chromadb_deleted = chromadb_service.delete_collection(collection_name)
                cleanup_results.append(f"ChromaDB collection '{collection_name}': {'deleted' if chromadb_deleted else 'not found'}")
            except Exception as e:
                cleanup_results.append(f"ChromaDB cleanup error: {str(e)}")
        
        # 2. Delete model files if job was completed
        if job.get('status') == 'COMPLETED' and job.get('model_name'):
            try:
                import os
                import shutil
                model_name = job.get('model_name', '').replace(':', '_').replace('/', '_')
                model_dir = f"models/{model_name}"
                
                if os.path.exists(model_dir):
                    shutil.rmtree(model_dir)
                    cleanup_results.append(f"Model directory '{model_dir}': deleted")
                else:
                    cleanup_results.append(f"Model directory '{model_dir}': not found")
                    
                # Also try to remove from Ollama if possible
                try:
                    import subprocess
                    ollama_model_name = job.get('model_name')
                    if ollama_model_name:
                        result = subprocess.run(['ollama', 'rm', ollama_model_name], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            cleanup_results.append(f"Ollama model '{ollama_model_name}': removed")
                        else:
                            cleanup_results.append(f"Ollama model '{ollama_model_name}': not found or error")
                except Exception as e:
                    cleanup_results.append(f"Ollama cleanup error: {str(e)}")
                    
            except Exception as e:
                cleanup_results.append(f"Model file cleanup error: {str(e)}")
        
        # 3. Delete training data directory
        try:
            import os
            import shutil
            train_data_dir = f"training_data/job_{job_id}"
            if os.path.exists(train_data_dir):
                shutil.rmtree(train_data_dir)
                cleanup_results.append(f"Training data directory '{train_data_dir}': deleted")
            else:
                cleanup_results.append(f"Training data directory '{train_data_dir}': not found")
        except Exception as e:
            cleanup_results.append(f"Training data cleanup error: {str(e)}")
        
        # 4. Delete from database
        success = db.delete_training_job(job_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training job deleted successfully',
                'cleanup_results': cleanup_results,
                'job_name': job.get('name', 'Unknown')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete job from database'
            }), 500
            
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
        
        # Start real training based on training type
        training_type = data.get('training_type', job.get('training_type', 'lora'))
        
        if training_type.lower() == 'rag':
            # Import and use RAG training executor
            from rag_training_executor import TrainingExecutor as RAGTrainingExecutor
            rag_executor = RAGTrainingExecutor()
            success = rag_executor.start_training(job_id, job)
        else:
            # Use default LoRA training executor
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
            'status': 'PENDING',
            'notes': data.get('notes', '')
        }
        
        # Save to database
        eval_id = db.add_evaluation(eval_data)
        
        # Start real evaluation
        from evaluation_executor import evaluation_executor
        success = evaluation_executor.start_evaluation(eval_id, eval_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Evaluation started successfully',
                'evaluation_id': eval_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start evaluation'
            }), 500
        
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
        if 'model_name' in data:
            updates['model_name'] = data['model_name']
        if 'status' in data:
            updates['status'] = data['status']
        
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

@app.route('/api/evaluations/<int:eval_id>/status', methods=['GET'])
def get_evaluation_status(eval_id):
    """Get evaluation status"""
    try:
        evaluation = db.get_evaluation_by_id(eval_id)
        if not evaluation:
            return jsonify({
                'success': False,
                'error': 'Evaluation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        })
        
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
    """Get available Ollama models with detailed capabilities"""
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
                    
                    # Get detailed model information from ollama show
                    model_details = get_model_details_from_ollama(model_name)
                    
                    # Get avatar information from model profile
                    profile = db.get_model_profile(model_name)
                    avatar_url = profile['avatar_url'] if profile else None
                    
                    models.append({
                        'name': model_name,
                        'size': size,
                        'modified': modified,
                        'capabilities': model_details['capabilities'],
                        'architecture': model_details['architecture'],
                        'parameters': model_details['parameters'],
                        'context_length': model_details['context_length'],
                        'quantization': model_details['quantization'],
                        'temperature': model_details['temperature'],
                        'top_p': model_details['top_p'],
                        'system_prompt': model_details['system_prompt'],
                        'license': model_details['license'],
                        'avatar_url': avatar_url,
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

@app.route('/api/models/<path:model_name>', methods=['PUT'])
def update_model(model_name):
    """Update an Ollama model's system prompt and parameters"""
    try:
        data = request.get_json()
        system_prompt = data.get('system_prompt', '')
        temperature = data.get('temperature')
        top_p = data.get('top_p')
        description = data.get('description', '')
        
        if not system_prompt:
            return jsonify({
                'success': False,
                'error': 'System prompt is required'
            }), 400
        
        # Get the base model from the current model
        result = subprocess.run(['ollama', 'show', model_name], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Model {model_name} not found'
            }), 404
        
        # Extract base model from the output (look for FROM line)
        base_model = None
        for line in result.stdout.split('\n'):
            if line.strip().startswith('FROM '):
                base_model = line.strip().split('FROM ')[1].strip()
                break
        
        if not base_model:
            # Fallback: try to determine base model from model name
            if ':' in model_name:
                base_model = model_name.split(':')[0] + ':latest'
            else:
                base_model = 'llama3.1:latest'  # Default fallback
        
        # Create a new Modelfile with updated system prompt
        modelfile_content = f"""FROM {base_model}

SYSTEM "{system_prompt}"

# Parameters"""
        
        if temperature is not None:
            modelfile_content += f"\nPARAMETER temperature {temperature}"
        if top_p is not None:
            modelfile_content += f"\nPARAMETER top_p {top_p}"
        
        # Create temporary Modelfile
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.Modelfile', delete=False) as f:
            f.write(modelfile_content)
            temp_modelfile = f.name
        
        try:
            # Update the model using ollama create (this overwrites the existing model)
            result = subprocess.run(['ollama', 'create', model_name, '-f', temp_modelfile], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'Model {model_name} updated successfully',
                    'system_prompt': system_prompt,
                    'temperature': temperature,
                    'top_p': top_p,
                    'base_model': base_model
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Failed to update model: {result.stderr}'
                }), 500
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_modelfile):
                os.unlink(temp_modelfile)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models/<path:model_name>/avatar', methods=['POST'])
def upload_model_avatar(model_name):
    """Upload avatar for a model"""
    try:
        from werkzeug.utils import secure_filename
        import os
        import uuid
        from PIL import Image
        
        if 'avatar' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No avatar file provided'
            }), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
        
        # Create avatars directory
        avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{secure_filename(model_name)}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(avatars_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Resize image to standard avatar size (128x128)
        try:
            with Image.open(file_path) as img:
                img = img.convert('RGB')
                img = img.resize((128, 128), Image.Resampling.LANCZOS)
                img.save(file_path, 'JPEG', quality=85)
        except Exception as e:
            print(f"Warning: Could not resize image: {e}")
        
        # Generate URL
        avatar_url = f"/api/avatars/{unique_filename}"
        
        # Update or create model profile
        profile_data = {
            'model_name': model_name,
            'avatar_path': file_path,
            'avatar_url': avatar_url
        }
        
        # Check if profile exists
        existing_profile = db.get_model_profile(model_name)
        if existing_profile:
            # Update existing profile
            db.update_model_profile(model_name, {
                'avatar_path': file_path,
                'avatar_url': avatar_url
            })
        else:
            # Create new profile
            db.add_model_profile(profile_data)
        
        return jsonify({
            'success': True,
            'message': f'Avatar uploaded successfully for {model_name}',
            'avatar_url': avatar_url,
            'file_path': file_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/avatars/<filename>')
def serve_avatar(filename):
    """Serve avatar images"""
    try:
        from flask import send_from_directory
        import os
        
        avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
        return send_from_directory(avatars_dir, filename)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/api/models/<path:model_name>/details', methods=['GET'])
def get_model_details(model_name):
    """Get detailed information about a specific model"""
    try:
        print(f"🔍 DEBUG: Getting details for model: '{model_name}'")
        # Get model details using ollama show
        result = subprocess.run(['ollama', 'show', model_name], capture_output=True, text=True, timeout=10)
        print(f"🔍 DEBUG: Ollama command result: returncode={result.returncode}")
        print(f"🔍 DEBUG: Ollama stdout: {result.stdout[:200]}...")
        if result.stderr:
            print(f"🔍 DEBUG: Ollama stderr: {result.stderr}")
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Failed to get details for model: {model_name}'
            }), 404
        
        # Parse the output
        details = parse_model_details(result.stdout)
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'details': details
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout getting model details'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def parse_model_details(output):
    """Parse ollama show output into structured data"""
    details = {
        'architecture': None,
        'parameters': None,
        'context_length': None,
        'embedding_length': None,
        'quantization': None,
        'capabilities': [],
        'parameters_config': {},
        'license': None,
        'tokens': None,  # Will be calculated/estimated
        'training_data_size': None,
        'vocab_size': None
    }
    
    lines = output.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect sections
        if line == 'Model':
            current_section = 'model'
            continue
        elif line == 'Capabilities':
            current_section = 'capabilities'
            continue
        elif line == 'Parameters':
            current_section = 'parameters'
            continue
        elif line == 'License':
            current_section = 'license'
            continue
        
        # Parse content based on current section
        if current_section == 'model' and line.strip() and not line.startswith(' '):
            # Handle format: "architecture        llama" or "context length      131072"
            parts = line.split()
            if len(parts) >= 2:
                # Handle multi-word keys like "context length"
                if len(parts) >= 3 and parts[1] == 'length':
                    key = f"{parts[0]}_{parts[1]}".lower()
                    value = parts[2]
                else:
                    key = parts[0].lower().replace(' ', '_')
                    value = ' '.join(parts[1:]).strip()
                
                if key == 'architecture':
                    details['architecture'] = value
                elif key == 'parameters':
                    details['parameters'] = value
                elif key == 'context_length':
                    details['context_length'] = int(value)
                elif key == 'embedding_length':
                    details['embedding_length'] = int(value)
                elif key == 'quantization':
                    details['quantization'] = value
                
        elif current_section == 'capabilities':
            if line and not line.startswith(' ') and line.strip():
                details['capabilities'].append(line.strip())
                
        elif current_section == 'parameters' and ':' in line:
            key, value = line.split(':', 1)
            details['parameters_config'][key.strip()] = value.strip()
            
        elif current_section == 'license':
            if not details['license']:
                details['license'] = line
            else:
                details['license'] += ' ' + line
    
    # Estimate tokens and other metrics based on parameters
    if details['parameters']:
        try:
            param_str = details['parameters'].replace('B', '').replace('M', '')
            if 'B' in details['parameters']:
                params = float(param_str) * 1_000_000_000
            elif 'M' in details['parameters']:
                params = float(param_str) * 1_000_000
            else:
                params = float(param_str)
            
            # Rough estimations based on model size
            # Training tokens: typically 1-2 tokens per parameter
            estimated_tokens = int(params * 1.5)  # Conservative estimate
            details['tokens'] = f"{estimated_tokens:,}"
            
            # Training data size estimation
            if params > 10_000_000_000:  # >10B params
                details['training_data_size'] = "~2-3 trillion tokens"
            elif params > 1_000_000_000:  # >1B params
                details['training_data_size'] = "~200-500 billion tokens"
            elif params > 100_000_000:  # >100M params
                details['training_data_size'] = "~20-50 billion tokens"
            else:
                details['training_data_size'] = "~2-5 billion tokens"
            
            # Vocabulary size estimation
            if 'llama' in details.get('architecture', '').lower():
                details['vocab_size'] = "128,256"
            elif 'gemma' in details.get('architecture', '').lower():
                details['vocab_size'] = "256,000"
            else:
                details['vocab_size'] = "~50,000-256,000"
                
        except:
            details['tokens'] = 'Unknown'
            details['training_data_size'] = 'Unknown'
            details['vocab_size'] = 'Unknown'
    
    return details

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

@app.route('/api/training-jobs/<int:job_id>/progress', methods=['POST'])
def update_training_progress(job_id):
    """Update training progress for a specific job with detailed step information"""
    try:
        data = request.get_json()
        progress = data.get('progress', 0.0)
        
        # Prepare update data with detailed progress info
        update_data = {'progress': progress}
        
        # Add detailed progress information if available
        if 'current_step' in data:
            update_data['current_step'] = data['current_step']
        if 'total_steps' in data:
            update_data['total_steps'] = data['total_steps']
        if 'epoch' in data:
            update_data['current_epoch'] = data['epoch']
        if 'total_epochs' in data:
            update_data['total_epochs'] = data['total_epochs']
        if 'step_progress' in data:
            update_data['step_progress'] = data['step_progress']
        
        # Update the training job progress
        db.update_training_job(job_id, update_data)
        
        # Log the detailed progress
        step_info = ""
        if 'current_step' in data and 'total_steps' in data:
            step_info = f" (Step {data['current_step']}/{data['total_steps']})"
        
        # Emit real-time progress update via SocketIO
        socketio.emit('training_progress', {
            'job_id': job_id,
            'progress': progress,
            'current_step': data.get('current_step'),
            'total_steps': data.get('total_steps'),
            'epoch': data.get('epoch'),
            'total_epochs': data.get('total_epochs'),
            'step_progress': data.get('step_progress'),
            'message': f'Progress: {progress*100:.1f}%{step_info}'
        })
        
        return jsonify({
            'success': True,
            'message': f'Updated progress for job {job_id} to {progress*100:.1f}%{step_info}',
            'progress': progress,
            'details': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-jobs/<int:job_id>/output', methods=['POST'])
def update_training_output(job_id):
    """Update training job with real-time output"""
    try:
        data = request.get_json()
        output = data.get('output', '')
        timestamp = data.get('timestamp', '')
        
        # Emit real-time output to frontend via Socket.IO
        socketio.emit('training_output', {
            'job_id': job_id,
            'output': output,
            'timestamp': timestamp
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/detect-stuck-training', methods=['POST'])
def detect_stuck_training():
    """Detect and fix stuck training jobs"""
    try:
        import time
        from datetime import datetime, timedelta
        
        # Get all running training jobs
        jobs = db.get_training_jobs()
        stuck_jobs = []
        
        for job in jobs:
            if job['status'] == 'RUNNING':
                started_at = job.get('started_at')
                if started_at:
                    start_time = datetime.fromisoformat(started_at)
                    elapsed = datetime.now() - start_time
                    
                    # Check if job has been running too long
                    timeout_minutes = 30 if job['training_type'] == 'LoRA' else 10
                    
                    if elapsed > timedelta(minutes=timeout_minutes):
                        # Check if progress hasn't changed in last 5 minutes
                        if job['progress'] < 0.5:  # Less than 50% progress
                            stuck_jobs.append({
                                'job_id': job['id'],
                                'job_name': job['name'],
                                'elapsed_minutes': int(elapsed.total_seconds() / 60),
                                'progress': job['progress']
                            })
        
        # Mark stuck jobs as failed
        for stuck_job in stuck_jobs:
            db.update_training_job(stuck_job['job_id'], {
                'status': 'FAILED',
                'error_message': f'Training stuck for {stuck_job["elapsed_minutes"]} minutes with {stuck_job["progress"]*100:.1f}% progress'
            })
        
        return jsonify({
            'success': True,
            'stuck_jobs_found': len(stuck_jobs),
            'stuck_jobs': stuck_jobs,
            'message': f'Found and fixed {len(stuck_jobs)} stuck training jobs'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-history', methods=['GET'])
def get_training_history():
    """Get comprehensive training history with detailed information"""
    try:
        # Get all training jobs
        jobs = db.get_training_jobs()
        
        # Get all datasets for reference
        datasets = db.get_all_datasets()
        dataset_map = {d['id']: d for d in datasets}
        
        # Process each job with detailed information
        history = []
        for job in jobs:
            # Get dataset information
            dataset_info = None
            if job.get('dataset_id'):
                dataset_info = dataset_map.get(job['dataset_id'])
            
            # Calculate duration if completed
            duration = None
            if job['status'] == 'COMPLETED' and job.get('started_at') and job.get('completed_at'):
                try:
                    from datetime import datetime
                    start = datetime.fromisoformat(job['started_at'])
                    end = datetime.fromisoformat(job['completed_at'])
                    duration_seconds = (end - start).total_seconds()
                    duration = {
                        'seconds': int(duration_seconds),
                        'minutes': int(duration_seconds / 60),
                        'hours': int(duration_seconds / 3600),
                        'formatted': f"{int(duration_seconds // 3600)}h {int((duration_seconds % 3600) // 60)}m {int(duration_seconds % 60)}s"
                    }
                except:
                    duration = None
            
            # Parse configuration
            config = {}
            if job.get('config'):
                try:
                    config = json.loads(job['config']) if isinstance(job['config'], str) else job['config']
                except:
                    config = {}
            
            # Create detailed history entry
            history_entry = {
                'id': job['id'],
                'name': job['name'],
                'description': job.get('description', ''),
                'status': job['status'],
                'training_type': job.get('training_type', 'LoRA'),
                'model_name': job['model_name'],
                'base_model': job.get('base_model', ''),
                'created_at': job['created_at'],
                'started_at': job.get('started_at'),
                'completed_at': job.get('completed_at'),
                'duration': duration,
                'progress': job.get('progress', 0),
                'error_message': job.get('error_message'),
                'config': config,
                'dataset': {
                    'id': job.get('dataset_id'),
                    'name': dataset_info['name'] if dataset_info else 'Unknown Dataset',
                    'description': dataset_info.get('description', '') if dataset_info else '',
                    'sample_count': dataset_info.get('loaded_samples', 0) if dataset_info else 0,
                    'total_samples': dataset_info.get('total_samples', 0) if dataset_info else 0
                } if job.get('dataset_id') else None,
                'training_parameters': {
                    'epochs': config.get('epochs', 'N/A'),
                    'learning_rate': config.get('learning_rate', 'N/A'),
                    'batch_size': config.get('batch_size', 'N/A'),
                    'lora_rank': config.get('lora_rank', 'N/A'),
                    'lora_alpha': config.get('lora_alpha', 'N/A')
                },
                'performance': {
                    'final_loss': config.get('final_loss'),
                    'best_loss': config.get('best_loss'),
                    'convergence_epoch': config.get('convergence_epoch')
                }
            }
            
            history.append(history_entry)
        
        # Sort by creation date (newest first)
        history.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_jobs': len(history),
            'completed_jobs': len([h for h in history if h['status'] == 'COMPLETED']),
            'failed_jobs': len([h for h in history if h['status'] == 'FAILED']),
            'running_jobs': len([h for h in history if h['status'] == 'RUNNING'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-history/<int:job_id>', methods=['GET'])
def get_training_job_details(job_id):
    """Get detailed information for a specific training job"""
    try:
        job = db.get_training_job_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Training job not found'
            }), 404
        
        # Get dataset information
        dataset_info = None
        if job.get('dataset_id'):
            dataset_info = db.get_dataset_by_id(job['dataset_id'])
        
        # Parse configuration
        config = {}
        if job.get('config'):
            try:
                config = json.loads(job['config']) if isinstance(job['config'], str) else job['config']
            except:
                config = {}
        
        # Calculate detailed metrics
        details = {
            'id': job['id'],
            'name': job['name'],
            'description': job.get('description', ''),
            'status': job['status'],
            'training_type': job.get('training_type', 'LoRA'),
            'model_name': job['model_name'],
            'base_model': job.get('base_model', ''),
            'created_at': job['created_at'],
            'started_at': job.get('started_at'),
            'completed_at': job.get('completed_at'),
            'progress': job.get('progress', 0),
            'error_message': job.get('error_message'),
            'config': config,
            'dataset': dataset_info,
            'training_logs': config.get('training_logs', []),
            'metrics': {
                'final_loss': config.get('final_loss'),
                'best_loss': config.get('best_loss'),
                'convergence_epoch': config.get('convergence_epoch'),
                'total_epochs': config.get('epochs'),
                'learning_rate': config.get('learning_rate'),
                'batch_size': config.get('batch_size')
            },
            'system_info': {
                'gpu_used': config.get('gpu_used', False),
                'memory_peak': config.get('memory_peak'),
                'disk_usage': config.get('disk_usage')
            }
        }
        
        return jsonify({
            'success': True,
            'job_details': details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
    print("  SocketIO: training_progress - Real-time training updates")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
