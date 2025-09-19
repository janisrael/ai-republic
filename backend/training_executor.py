#!/usr/bin/env python3
"""
Real Training Executor for AI Refinement Dashboard
Implements actual LoRA fine-tuning and RAG training based on convo.md instructions
"""

import os
import json
import threading
import subprocess
import re
from datetime import datetime
from typing import Dict, Any, Optional
from database import db
from chromadb_service import chromadb_service
from lora_script_generator import LoRAScriptGenerator


class TrainingExecutor:
    def __init__(self):
        self.running_jobs = {}

    def start_training(self, job_id: int, job_data: Dict[str, Any]) -> bool:
        """Start real training for a job"""
        try:
            db.update_training_job(job_id, {
                'status': 'RUNNING',
                'started_at': datetime.now().isoformat(),
                'progress': 0.0
            })

            training_thread = threading.Thread(
                target=self._execute_training,
                args=(job_id, job_data)
            )
            training_thread.daemon = True
            training_thread.start()

            self.running_jobs[job_id] = {
                'thread': training_thread,
                'status': 'RUNNING',
                'started_at': datetime.now()
            }

            return True

        except Exception as e:
            print(f"Error starting training for job {job_id}: {e}")
            db.update_training_job(job_id, {
                'status': 'FAILED',
                'error_message': str(e)
            })
            return False

    def _execute_training(self, job_id: int, job_data: Dict[str, Any]):
        """Execute the actual training process"""
        try:
            training_type = job_data.get('training_type', 'lora')
            if training_type.lower() == 'rag':
                self._execute_rag_training(job_id, job_data)
            elif training_type.lower() == 'lora':
                self._execute_lora_training(job_id, job_data)
            else:
                raise ValueError(f"Unsupported training type: {training_type}")
        except Exception as e:
            print(f"Training failed for job {job_id}: {e}")
            db.update_training_job(job_id, {
                'status': 'FAILED',
                'error_message': str(e),
                'completed_at': datetime.now().isoformat()
            })
        finally:
            # Clean up running jobs dictionary
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    # ====== RAG TRAINING ======
    def _execute_rag_training(self, job_id: int, job_data: Dict[str, Any]):
        try:
            job_name = job_data.get('name', f'job-{job_id}')
            config_str = job_data.get('config', '{}')
            config = json.loads(config_str) if isinstance(config_str, str) else config_str

            db.update_training_job(job_id, {'progress': 0.1})
            self._create_modelfile(job_name, job_data.get('base_model'), config)
            db.update_training_job(job_id, {'progress': 0.3})

            if config.get('selectedDatasets'):
                self._ingest_knowledge_base(job_id, config)
            db.update_training_job(job_id, {'progress': 0.6})

            self._create_ollama_model(job_name)
            db.update_training_job(job_id, {'progress': 0.9})

            db.update_training_job(job_id, {
                'status': 'COMPLETED',
                'progress': 1.0,
                'completed_at': datetime.now().isoformat()
            })
        except Exception as e:
            raise Exception(f"RAG training failed: {str(e)}")
        finally:
            # Clean up running jobs dictionary
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    # ====== LoRA TRAINING ======
    def _execute_lora_training(self, job_id: int, job_data: Dict[str, Any]):
        try:
            job_name = job_data.get('name', f'job-{job_id}')
            base_model = job_data.get('base_model')
            config_str = job_data.get('config', '{}')
            config = json.loads(config_str) if isinstance(config_str, str) else config_str

            db.update_training_job(job_id, {'progress': 0.1})
            self._prepare_lora_data(job_id, config)
            db.update_training_job(job_id, {'progress': 0.2})

            self._run_lora_training(job_id, job_name, base_model, config)
            db.update_training_job(job_id, {'progress': 0.8})

            self._create_ollama_model_from_lora(job_name, base_model)
            db.update_training_job(job_id, {'progress': 0.95})

            db.update_training_job(job_id, {
                'status': 'COMPLETED',
                'progress': 1.0,
                'completed_at': datetime.now().isoformat()
            })
        except Exception as e:
            raise Exception(f"LoRA training failed: {str(e)}")
        finally:
            # Clean up running jobs dictionary
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    # ====== SUPPORTING FUNCTIONS ======
    def _create_modelfile(self, job_name: str, base_model: str, config: Dict[str, Any]):
        role_definition = config.get('roleDefinition',
                                     f'You are {job_name}, an advanced AI assistant with a comprehensive knowledge base.')
        modelfile_content = f"""FROM {base_model}

SYSTEM "{role_definition}"
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9
"""
        modelfile_path = f"models/{job_name}/Modelfile"
        os.makedirs(os.path.dirname(modelfile_path), exist_ok=True)
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)

    def _ingest_knowledge_base(self, job_id: int, config: Dict[str, Any]):
        dataset_ids = config.get('selectedDatasets', [])
        if not dataset_ids:
            return
        all_samples = []
        for dataset_id in dataset_ids:
            dataset = next((ds for ds in db.get_all_datasets() if ds['id'] == int(dataset_id)), None)
            if dataset:
                samples = self._extract_dataset_samples_for_chromadb(dataset)
                all_samples.extend(samples)
        if all_samples:
            chromadb_service.create_knowledge_base(job_id, all_samples)

    def _extract_dataset_samples_for_chromadb(self, dataset: Dict[str, Any]) -> list:
        chromadb_samples = []
        # Use all_samples if available, otherwise fall back to samples_preview
        dataset_samples = dataset.get('metadata', {}).get('all_samples', 
                                                         dataset.get('metadata', {}).get('samples_preview', []))
        for sample in dataset_samples:
            combined_text = "\n".join(
                f"{k.capitalize()}: {v}" for k, v in sample.items() if v
            )
            if combined_text.strip():
                chromadb_samples.append({
                    'output': combined_text,
                    'instruction': sample.get('instruction', ''),
                    'input': sample.get('input', ''),
                    'system': sample.get('system', ''),
                    'source': dataset['name'],
                    'type': dataset.get('type', 'text'),
                    'dataset_id': dataset['id']
                })
        return chromadb_samples

    def _create_ollama_model(self, model_name: str):
        sanitized_name = re.sub(r'[^a-zA-Z0-9.-]', '-', model_name.lower())
        if not sanitized_name.endswith(':latest'):
            sanitized_name += ':latest'
        modelfile_path = os.path.abspath(f"models/{model_name}/Modelfile")
        if not os.path.exists(modelfile_path):
            raise FileNotFoundError(f"Modelfile not found: {modelfile_path}")
        subprocess.run(['ollama', 'create', sanitized_name, '-f', modelfile_path],
                       check=True, text=True)

    def _prepare_lora_data(self, job_id: int, config: Dict[str, Any]):
        dataset_ids = config.get('selectedDatasets', [])
        if not dataset_ids:
            raise ValueError("No datasets selected for LoRA training")
        train_samples, val_samples = [], []
        valid_datasets = []
        for dataset_id in dataset_ids:
            dataset = next((ds for ds in db.get_all_datasets() if ds['id'] == int(dataset_id)), None)
            if dataset:
                samples = self._convert_dataset_to_lora_format(dataset)
                if samples:
                    split_idx = int(len(samples) * 0.8)
                    train_samples.extend(samples[:split_idx])
                    val_samples.extend(samples[split_idx:])
                    valid_datasets.append(dataset['name'])
        if not train_samples:
            raise Exception(f"No training samples found. Valid datasets: {valid_datasets}")
        os.makedirs(f"training_data/job_{job_id}", exist_ok=True)
        self._save_jsonl(train_samples, f"training_data/job_{job_id}/train.jsonl")
        self._save_jsonl(val_samples, f"training_data/job_{job_id}/val.jsonl")

    def _convert_dataset_to_lora_format(self, dataset: Dict[str, Any]) -> list:
        samples = []
        # Use all_samples if available, otherwise fall back to samples_preview
        dataset_samples = dataset.get('metadata', {}).get('all_samples', 
                                                         dataset.get('metadata', {}).get('samples_preview', []))
        
        for sample in dataset_samples:
            # Handle standard format (Codealpaca, etc.)
            if 'instruction' in sample and 'output' in sample:
                instr = sample.get('instruction', '')
                output = sample.get('output', '')
                if instr and output:
                    samples.append({
                        'instruction': instr,
                        'input': sample.get('input', ''),
                        'output': output,
                        'system': sample.get('system', '')
                    })
            
            # Handle Devops format (content field with stringified JSON)
            elif 'content' in sample:
                try:
                    import ast
                    content_str = sample.get('content', '')
                    # Parse the stringified dictionary
                    content_dict = ast.literal_eval(content_str)
                    
                    instruction = content_dict.get('Instruction', '')
                    response = content_dict.get('Response', '')
                    prompt = content_dict.get('Prompt', '')
                    
                    if instruction and response:
                        samples.append({
                            'instruction': instruction,
                            'input': prompt,
                            'output': response,
                            'system': ''
                        })
                except (ValueError, SyntaxError) as e:
                    print(f"Warning: Could not parse Devops sample: {e}")
                    continue
        
        print(f"✅ Converted {len(samples)} samples from dataset '{dataset.get('name', 'Unknown')}'")
        return samples

    def _save_jsonl(self, data: list, filepath: str):
        with open(filepath, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')

    def _run_lora_training(self, job_id: int, job_name: str, base_model: str, config: Dict[str, Any]):
        script_path = f"training_scripts/job_{job_id}_train.py"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        lora_generator = LoRAScriptGenerator()
        script_content = lora_generator.generate_lora_script(job_name, base_model, config, job_id)
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        subprocess.run(['python', script_path], check=True, text=True)

    def _create_ollama_model_from_lora(self, model_name: str, base_model: str):
        clean_name = re.sub(r'[^a-zA-Z0-9\-_]', '-', model_name.lower())
        # Check both sanitized and original names for the model path
        merged_path_sanitized = f"models/{clean_name}_lora_merged"
        regular_path_sanitized = f"models/{clean_name}_lora"
        merged_path_original = f"models/{model_name}_lora_merged"
        regular_path_original = f"models/{model_name}_lora"
        
        # Try sanitized paths first, then original paths
        if os.path.exists(merged_path_sanitized):
            model_path = merged_path_sanitized
        elif os.path.exists(regular_path_sanitized):
            model_path = regular_path_sanitized
        elif os.path.exists(merged_path_original):
            model_path = merged_path_original
        elif os.path.exists(regular_path_original):
            model_path = regular_path_original
        else:
            model_path = merged_path_sanitized  # Default for error message
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")
        modelfile_content = f"""FROM {base_model}

SYSTEM "You are {clean_name}, fine-tuned using LoRA."
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
"""
        modelfile_path = os.path.join(model_path, "Modelfile")
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        subprocess.run(['ollama', 'create', clean_name, '-f', modelfile_path], check=True, text=True)

    def stop_training(self, job_id: int) -> bool:
        if job_id in self.running_jobs:
            db.update_training_job(job_id, {
                'status': 'STOPPED',
                'completed_at': datetime.now().isoformat()
            })
            del self.running_jobs[job_id]
            return True
        return False

    def get_training_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        if job_id in self.running_jobs:
            job_info = self.running_jobs[job_id]
            return {
                'status': job_info['status'],
                'started_at': job_info['started_at'].isoformat(),
                'running': True
            }
        else:
            job_record = db.get_training_job(job_id)
            if job_record:
                return {
                    'status': job_record.get('status'),
                    'progress': job_record.get('progress'),
                    'running': False
                }
            return None
