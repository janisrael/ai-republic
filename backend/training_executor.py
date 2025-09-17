#!/usr/bin/env python3
"""
Real Training Executor for AI Refinement Dashboard
Implements actual LoRA fine-tuning and RAG training based on convo.md instructions
"""

import os
import json
import time
import subprocess
import threading
import shlex
import re
from datetime import datetime
from typing import Dict, Any, Optional
from database import db
from chromadb_service import chromadb_service

class TrainingExecutor:
    def __init__(self):
        self.running_jobs = {}
        
    def start_training(self, job_id: int, job_data: Dict[str, Any]) -> bool:
        """Start real training for a job"""
        try:
            # Update job status to RUNNING
            db.update_training_job(job_id, {
                'status': 'RUNNING',
                'started_at': datetime.now().isoformat(),
                'progress': 0.0
            })
            
            # Start training in a separate thread
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
            job_name = job_data.get('name', f'job-{job_id}')
            base_model = job_data.get('base_model')
            training_type = job_data.get('training_type', 'lora')
            
            print(f"🚀 Starting real training for job: {job_name}")
            print(f"📊 Base model: {base_model}")
            print(f"🔧 Training type: {training_type}")
            
            if training_type.lower() == 'rag':
                self._execute_rag_training(job_id, job_data)
            elif training_type.lower() == 'lora':
                self._execute_lora_training(job_id, job_data)
            else:
                raise ValueError(f"Unsupported training type: {training_type}")
                
        except Exception as e:
            print(f"❌ Training failed for job {job_id}: {e}")
            db.update_training_job(job_id, {
                'status': 'FAILED',
                'error_message': str(e),
                'completed_at': datetime.now().isoformat()
            })
    
    def _execute_rag_training(self, job_id: int, job_data: Dict[str, Any]):
        """Execute RAG training - create Modelfile and ingest knowledge base"""
        try:
            job_name = job_data.get('name', f'job-{job_id}')
            base_model = job_data.get('base_model')
            config_str = job_data.get('config', '{}')
            config = json.loads(config_str) if isinstance(config_str, str) else config_str
            
            print(f"🔍 Starting RAG training for: {job_name}")
            
            # Update progress
            db.update_training_job(job_id, {'progress': 0.1})
            
            # Step 1: Create Modelfile with role definition
            self._create_modelfile(job_name, base_model, config)
            db.update_training_job(job_id, {'progress': 0.3})
            
            # Step 2: Ingest knowledge base (if datasets selected)
            if config.get('selectedDatasets'):
                self._ingest_knowledge_base(job_id, config)
            db.update_training_job(job_id, {'progress': 0.6})
            
            # Step 3: Create Ollama model
            self._create_ollama_model(job_name)
            db.update_training_job(job_id, {'progress': 0.9})
            
            # Step 4: Complete training
            db.update_training_job(job_id, {
                'status': 'COMPLETED',
                'progress': 1.0,
                'completed_at': datetime.now().isoformat()
            })
            
            print(f"✅ RAG training completed for: {job_name}")
            
        except Exception as e:
            raise Exception(f"RAG training failed: {str(e)}")
    
    def _execute_lora_training(self, job_id: int, job_data: Dict[str, Any]):
        """Execute LoRA fine-tuning training"""
        try:
            job_name = job_data.get('name', f'job-{job_id}')
            base_model = job_data.get('base_model')
            config_str = job_data.get('config', '{}')
            config = json.loads(config_str) if isinstance(config_str, str) else config_str
            
            print(f"🧠 Starting LoRA training for: {job_name}")
            
            # Update progress
            db.update_training_job(job_id, {'progress': 0.1})
            
            # Step 1: Prepare training data
            self._prepare_lora_data(job_id, config)
            db.update_training_job(job_id, {'progress': 0.2})
            
            # Step 2: Execute LoRA training
            self._run_lora_training(job_id, job_name, base_model, config)
            db.update_training_job(job_id, {'progress': 0.8})
            
            # Step 3: Create Ollama model from trained LoRA
            self._create_ollama_model_from_lora(job_name, base_model)
            db.update_training_job(job_id, {'progress': 0.95})
            
            # Step 4: Complete training
            db.update_training_job(job_id, {
                'status': 'COMPLETED',
                'progress': 1.0,
                'completed_at': datetime.now().isoformat()
            })
            
            print(f"✅ LoRA training completed for: {job_name}")
            
        except Exception as e:
            raise Exception(f"LoRA training failed: {str(e)}")
    
    def _create_modelfile(self, job_name: str, base_model: str, config: Dict[str, Any]):
        """Create Modelfile for ChromaDB RAG training"""
        role_definition = config.get('roleDefinition', 
            f'You are {job_name}, an advanced AI assistant with access to a comprehensive knowledge base. You provide helpful, accurate, and detailed responses based on your training data.')
        
        modelfile_content = f"""FROM {base_model}

SYSTEM \"{role_definition}

You have access to a vector-based knowledge base that contains relevant examples and training data. When answering questions, consider the context and examples from your knowledge base to provide accurate and helpful responses.

Your knowledge base contains various examples including:
- Code examples and solutions
- Instruction-response pairs
- System prompts and configurations
- Training data samples

Use this knowledge to provide contextually relevant and accurate responses.\"

# RAG Configuration
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9
"""
        
        # Save Modelfile
        modelfile_path = f"models/{job_name}/Modelfile"
        os.makedirs(os.path.dirname(modelfile_path), exist_ok=True)
        
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        print(f"📝 Created Modelfile for {job_name} with ChromaDB RAG capabilities")
    
    def _ingest_knowledge_base(self, job_id: int, config: Dict[str, Any]):
        """Ingest datasets into ChromaDB knowledge base for RAG"""
        try:
            print(f"🔍 Starting ChromaDB knowledge base ingestion for job {job_id}")
            
            # Get selected datasets
            dataset_ids = config.get('selectedDatasets', [])
            if not dataset_ids:
                print("⚠️ No datasets selected for RAG training")
                return
            
            print(f"📋 Processing datasets: {dataset_ids}")
            
            # Collect all dataset samples for ChromaDB ingestion
            all_dataset_samples = []
            
            # Process each dataset
            for dataset_id in dataset_ids:
                print(f"🔄 Processing dataset ID: {dataset_id}")
                # Get dataset by database ID, not Hugging Face ID
                all_datasets = db.get_all_datasets()
                dataset = None
                for ds in all_datasets:
                    if ds['id'] == dataset_id:
                        dataset = ds
                        break
                
                if dataset:
                    print(f"✅ Found dataset: {dataset['name']}")
                    samples = self._extract_dataset_samples_for_chromadb(dataset)
                    all_dataset_samples.extend(samples)
                    print(f"✅ Extracted {len(samples)} samples from: {dataset['name']}")
                else:
                    print(f"❌ Dataset not found: {dataset_id}")
            
            if all_dataset_samples:
                # Create ChromaDB knowledge base
                success = chromadb_service.create_knowledge_base(job_id, all_dataset_samples)
                if success:
                    print(f"🎉 ChromaDB knowledge base created for job {job_id} with {len(all_dataset_samples)} samples")
                else:
                    raise Exception("Failed to create ChromaDB knowledge base")
            else:
                print("⚠️ No samples found for knowledge base")
            
        except Exception as e:
            print(f"❌ Error ingesting knowledge base: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _extract_dataset_samples_for_chromadb(self, dataset: Dict[str, Any]) -> list:
        """Extract samples from dataset for ChromaDB ingestion"""
        try:
            print(f"🔄 Extracting samples from dataset: {dataset.get('name', 'Unknown')}")
            
            metadata = dataset.get('metadata', {})
            samples_preview = metadata.get('samples_preview', [])
            
            print(f"📊 Found {len(samples_preview)} sample previews")
            
            # Convert samples to ChromaDB format
            chromadb_samples = []
            
            for i, sample in enumerate(samples_preview):
                # Create a comprehensive text representation for embedding
                text_parts = []
                
                if 'instruction' in sample and sample['instruction']:
                    text_parts.append(f"Instruction: {sample['instruction']}")
                
                if 'input' in sample and sample['input']:
                    text_parts.append(f"Input: {sample['input']}")
                
                if 'output' in sample and sample['output']:
                    text_parts.append(f"Output: {sample['output']}")
                
                if 'system' in sample and sample['system']:
                    text_parts.append(f"System: {sample['system']}")
                
                # Combine all parts into a single text
                combined_text = "\n".join(text_parts)
                
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
            
            print(f"✅ Extracted {len(chromadb_samples)} samples from: {dataset['name']}")
            return chromadb_samples
            
        except Exception as e:
            print(f"❌ Error extracting samples from dataset {dataset.get('name', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_ollama_model(self, model_name: str):
        """Create Ollama model from Modelfile"""
        try:
            # Sanitize model name for Ollama (no spaces, special chars)
            sanitized_name = re.sub(r'[^a-zA-Z0-9.-]', '-', model_name.lower()).strip('-')
            if not sanitized_name.endswith(':latest'):
                sanitized_name += ':latest'
            
            modelfile_path = f"models/{model_name}/Modelfile"
            
            if not os.path.exists(modelfile_path):
                raise FileNotFoundError(f"Modelfile not found: {modelfile_path}")
            
            # Get absolute path
            abs_modelfile_path = os.path.abspath(modelfile_path)
            
            print(f"🔧 Creating Ollama model: {sanitized_name}")
            print(f"📁 Using Modelfile: {abs_modelfile_path}")
            
            # Use subprocess with proper argument list (not shell=True)
            cmd = ['ollama', 'create', sanitized_name, '-f', abs_modelfile_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=os.getcwd()
            )
            
            print(f"📤 Ollama command: {' '.join(cmd)}")
            print(f"📥 Return code: {result.returncode}")
            print(f"📝 Stdout: {result.stdout}")
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"Failed to create Ollama model: {result.stderr}")
            
            print(f"🎉 Created Ollama model: {sanitized_name}")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout creating Ollama model")
        except Exception as e:
            raise Exception(f"Error creating Ollama model: {str(e)}")
    
    def _prepare_lora_data(self, job_id: int, config: Dict[str, Any]):
        """Prepare training data for LoRA fine-tuning"""
        try:
            # Get selected datasets
            dataset_ids = config.get('selectedDatasets', [])
            if not dataset_ids:
                raise ValueError("No datasets selected for LoRA training")
            
            # Create training data directory
            train_dir = f"training_data/job_{job_id}"
            os.makedirs(train_dir, exist_ok=True)
            
            # Process datasets into JSONL format
            train_samples = []
            val_samples = []
            
            valid_datasets = []
            for dataset_id in dataset_ids:
                # Get dataset by database ID, not Hugging Face ID
                # Convert string ID to int for comparison
                dataset_id_int = int(dataset_id)
                all_datasets = db.get_all_datasets()
                dataset = None
                for ds in all_datasets:
                    if ds['id'] == dataset_id_int:
                        dataset = ds
                        break
                
                if dataset:
                    samples = self._convert_dataset_to_lora_format(dataset)
                    if samples:  # Only include datasets with actual samples
                        train_samples.extend(samples[:-len(samples)//5])  # 80% for training
                        val_samples.extend(samples[-len(samples)//5:])    # 20% for validation
                        valid_datasets.append(dataset['name'])
                        print(f"✅ Added {len(samples)} samples from: {dataset['name']}")
                    else:
                        print(f"⚠️ Skipping empty dataset: {dataset['name']}")
            
            if not train_samples:
                raise Exception(f"No training samples found. Valid datasets: {valid_datasets}")
            
            print(f"📊 Total samples: {len(train_samples)} training, {len(val_samples)} validation from {len(valid_datasets)} datasets")
            
            # Save training data
            self._save_jsonl(train_samples, os.path.join(train_dir, 'train.jsonl'))
            self._save_jsonl(val_samples, os.path.join(train_dir, 'val.jsonl'))
            
            print(f"📊 Prepared {len(train_samples)} training samples and {len(val_samples)} validation samples")
            
        except Exception as e:
            raise Exception(f"Error preparing LoRA data: {str(e)}")
    
    def _convert_dataset_to_lora_format(self, dataset: Dict[str, Any]) -> list:
        """Convert dataset to LoRA training format"""
        samples = []
        metadata = dataset.get('metadata', {})
        samples_preview = metadata.get('samples_preview', [])
        
        for sample in samples_preview:
            # Handle different dataset formats
            lora_sample = {
                "instruction": sample.get('instruction', sample.get('Instruction', '')),
                "input": sample.get('input', sample.get('Input', '')),
                "output": sample.get('output', sample.get('Response', '')),
                "system": sample.get('system', '')
            }
            
            # Handle datasets where data is stored as Python dict string in 'content' field
            if 'content' in sample and not lora_sample['instruction']:
                try:
                    import ast
                    content_data = ast.literal_eval(sample['content'])
                    lora_sample['instruction'] = content_data.get('Instruction', content_data.get('instruction', ''))
                    lora_sample['output'] = content_data.get('Response', content_data.get('output', ''))
                    lora_sample['input'] = content_data.get('Input', content_data.get('input', ''))
                except:
                    pass  # Skip if parsing fails
            
            # Skip samples with no instruction or output
            if lora_sample['instruction'] or lora_sample['output']:
                samples.append(lora_sample)
        
        return samples
    
    def _save_jsonl(self, data: list, filepath: str):
        """Save data to JSONL file"""
        with open(filepath, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
    
    def _run_lora_training(self, job_id: int, job_name: str, base_model: str, config: Dict[str, Any]):
        """Run actual LoRA fine-tuning"""
        try:
            # Create training script
            script_path = f"training_scripts/job_{job_id}_train.py"
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            # Generate training script based on convo.md instructions
            script_content = self._generate_lora_script(job_name, base_model, config, job_id)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Run training script
            print(f"🏃 Running LoRA training script for {job_name}")
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"LoRA training failed: {result.stderr}")
            
            print(f"✅ LoRA training completed for {job_name}")
            
        except subprocess.TimeoutExpired:
            raise Exception("LoRA training timed out")
        except Exception as e:
            raise Exception(f"Error running LoRA training: {str(e)}")
    
    def _generate_lora_script(self, job_name: str, base_model: str, config: Dict[str, Any], job_id: int) -> str:
        """Generate LoRA training script based on convo.md instructions"""
        lora_config = config.get('loraConfig', {})
        params = config.get('params', {})
        
        rank = lora_config.get('rank', 8)
        alpha = lora_config.get('alpha', 32)
        dropout = lora_config.get('dropout', 0.05)
        learning_rate = params.get('learningRate', 0.0002)
        batch_size = params.get('batchSize', 4)
        epochs = params.get('epochs', 3)
        
        # Map Ollama model names to Hugging Face model IDs
        hf_model_id = self._map_ollama_to_hf(base_model)
        
        script = f'''#!/usr/bin/env python3
"""
LoRA Training Script for {job_name}
Generated by AI Refinement Dashboard
"""

import os
import json
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("🚀 Starting LoRA training for {job_name}")
        
        # Model and data paths
        base_model = "{hf_model_id}"
        train_data_path = "training_data/job_{job_id}/train.jsonl"
        val_data_path = "training_data/job_{job_id}/val.jsonl"
        output_dir = f"models/{job_name}_lora"
        
        # Load model with 8-bit quantization (memory efficient)
        logger.info("📥 Loading base model...")
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_use_double_quant=True,
            bnb_8bit_quant_type="nf8",
            bnb_8bit_compute_dtype=torch.bfloat16
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        
        # Add padding token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Prepare model for k-bit training
        model = prepare_model_for_kbit_training(model)
        
        # LoRA configuration
        lora_config = LoraConfig(
            r={rank},
            lora_alpha={alpha},
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout={dropout},
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        # Apply LoRA
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        # Load dataset
        logger.info("📊 Loading training data...")
        dataset = load_dataset(
            "json",
            data_files={{
                "train": train_data_path,
                "validation": val_data_path
            }},
            streaming=False
        )
        
        # Tokenize function
        def tokenize_function(examples):
            # Create instruction format
            texts = []
            for i in range(len(examples["instruction"])):
                instruction = examples["instruction"][i]
                input_text = examples["input"][i] if examples["input"][i] else ""
                output = examples["output"][i]
                
                if input_text:
                    text = f"### Instruction:\\n{{instruction}}\\n\\n### Input:\\n{{input_text}}\\n\\n### Response:\\n{{output}}"
                else:
                    text = f"### Instruction:\\n{{instruction}}\\n\\n### Response:\\n{{output}}"
                
                texts.append(text)
            
            # Tokenize
            tokenized = tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Set labels same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()
            return tokenized
        
        # Tokenize datasets
        train_dataset = dataset["train"].map(tokenize_function, batched=True)
        val_dataset = dataset["validation"].map(tokenize_function, batched=True)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size={batch_size},
            per_device_eval_batch_size={batch_size},
            gradient_accumulation_steps=4,
            num_train_epochs={epochs},
            learning_rate={learning_rate},
            fp16=True,
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_steps=100,
            save_total_limit=3,
            load_best_model_at_end=True,
            report_to=None,  # Disable wandb/tensorboard
            remove_unused_columns=False,
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
        )
        
        # Start training with progress tracking
        logger.info("🏃 Starting training...")
        
        # Custom training loop with progress updates
        total_steps = trainer.get_train_dataloader().__len__() * {epochs}
        current_step = 0
        
        for epoch in range({epochs}):
            logger.info(f"📚 Starting epoch {{epoch + 1}}/{epochs}")
            epoch_steps = 0
            
            for step, batch in enumerate(trainer.get_train_dataloader()):
                # Training step
                trainer.training_step(trainer.model, batch)
                current_step += 1
                epoch_steps += 1
                
                # Update progress every 5 steps for more frequent updates
                if current_step % 5 == 0:
                    progress = 0.2 + (current_step / total_steps) * 0.6  # 20% to 80%
                    logger.info(f"📊 Progress: {{progress*100:.1f}}% (Step {{current_step}}/{{total_steps}})")
                    
                    # Update database progress with detailed info
                    import requests
                    try:
                        requests.post(f'http://localhost:5000/api/training-jobs/{job_id}/progress', 
                                    json={{
                                        'progress': progress,
                                        'current_step': current_step,
                                        'total_steps': total_steps,
                                        'epoch': epoch + 1,
                                        'total_epochs': {epochs},
                                        'step_progress': f"{{current_step}}/{{total_steps}}"
                                    }}, timeout=1)
                    except:
                        pass  # Don't fail training if progress update fails
            
            logger.info(f"✅ Completed epoch {{epoch + 1}}/{epochs}")
        
        # Save model
        logger.info("💾 Saving trained model...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        logger.info("✅ LoRA training completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {{str(e)}}")
        raise

if __name__ == "__main__":
    main()
'''
        
        return script
    
    def _map_ollama_to_hf(self, ollama_model: str) -> str:
        """Map Ollama model names to Hugging Face model IDs"""
        mapping = {
            # Non-gated models (no authentication required)
            'qwen2.5-coder:7b': 'Qwen/Qwen2.5-Coder-7B',
            'qwen2.5:7b': 'Qwen/Qwen2.5-7B',
            'qwen2.5:14b': 'Qwen/Qwen2.5-14B',
            'mistral:7b': 'mistralai/Mistral-7B-v0.1',
            'gemma2:9b': 'google/gemma-2-9b',
            'gemma2:27b': 'google/gemma-2-27b',
            'llava:13b': 'llava-hf/llava-1.5-13b-hf',
            
            # Gated models (require Hugging Face authentication)
            'llama3.1:8b': 'meta-llama/Meta-Llama-3.1-8B',
            'llama3.1:70b': 'meta-llama/Meta-Llama-3.1-70B',
            'codellama:13b': 'codellama/CodeLlama-13b-Python-hf',
            'codellama:7b': 'codellama/CodeLlama-7b-Python-hf'
        }
        
        # Remove :latest suffix if present
        clean_name = ollama_model.replace(':latest', '')
        
        if clean_name in mapping:
            return mapping[clean_name]
        else:
            # Default fallback - try to use the name as-is
            print(f"⚠️ Unknown Ollama model: {ollama_model}, using as Hugging Face ID")
            return clean_name
    
    def _create_ollama_model_from_lora(self, model_name: str, base_model: str):
        """Create Ollama model from trained LoRA weights"""
        try:
            # Create Modelfile for LoRA model
            modelfile_content = f"""FROM {base_model}

# Load LoRA weights
ADAPTER ./models/{model_name}_lora

SYSTEM "You are {model_name}, a fine-tuned AI assistant specialized for your specific use case."

PARAMETER num_ctx 4096
PARAMETER temperature 0.7
"""
            
            modelfile_path = f"models/{model_name}/Modelfile"
            os.makedirs(os.path.dirname(modelfile_path), exist_ok=True)
            
            with open(modelfile_path, 'w') as f:
                f.write(modelfile_content)
            
            # Sanitize model name for Ollama (no spaces, special chars)
            sanitized_name = re.sub(r'[^a-zA-Z0-9.-]', '-', model_name.lower()).strip('-')
            if not sanitized_name.endswith(':latest'):
                sanitized_name += ':latest'
            
            # Get absolute path
            abs_modelfile_path = os.path.abspath(modelfile_path)
            
            print(f"🔧 Creating Ollama model from LoRA: {sanitized_name}")
            print(f"📁 Using Modelfile: {abs_modelfile_path}")
            
            # Use subprocess with proper argument list (not shell=True)
            cmd = ['ollama', 'create', sanitized_name, '-f', abs_modelfile_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.getcwd()
            )
            
            print(f"📤 Ollama command: {' '.join(cmd)}")
            print(f"📥 Return code: {result.returncode}")
            print(f"📝 Stdout: {result.stdout}")
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"Failed to create Ollama model from LoRA: {result.stderr}")
            
            print(f"🎉 Created Ollama model from LoRA: {sanitized_name}")
            
        except Exception as e:
            raise Exception(f"Error creating Ollama model from LoRA: {str(e)}")
    
    def stop_training(self, job_id: int) -> bool:
        """Stop a running training job"""
        try:
            if job_id in self.running_jobs:
                # Update job status
                db.update_training_job(job_id, {
                    'status': 'STOPPED',
                    'completed_at': datetime.now().isoformat()
                })
                
                # Remove from running jobs
                del self.running_jobs[job_id]
                
                print(f"🛑 Stopped training job {job_id}")
                return True
            else:
                print(f"⚠️ Job {job_id} is not running")
                return False
                
        except Exception as e:
            print(f"Error stopping training job {job_id}: {e}")
            return False
    
    def get_training_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get current training status for a job"""
        if job_id in self.running_jobs:
            job_info = self.running_jobs[job_id]
            return {
                'status': job_info['status'],
                'started_at': job_info['started_at'].isoformat(),
                'running': True
            }
        else:
            # Get from database
            job = db.get_training_job_by_id(job_id)
            if job:
                return {
                    'status': job['status'],
                    'started_at': job.get('started_at'),
                    'completed_at': job.get('completed_at'),
                    'running': False
                }
            return None

# Global training executor instance
training_executor = TrainingExecutor()
