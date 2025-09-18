#!/usr/bin/env python3
"""
Fixed LoRA Training Script - Based on 2024 Best Practices
Addresses common LoRA fine-tuning failures
"""

import os
import json
import torch
import logging
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import load_dataset, Dataset
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("🚀 Starting Fixed LoRA training")
        
        # Model and data paths
        base_model = "microsoft/DialoGPT-medium"  # Use open model for testing
        train_data_path = "training_data/job_test/train.jsonl"
        val_data_path = "training_data/job_test/val.jsonl"
        output_dir = "models/Fixed_LoRA_Model"
        
        # Check if training data exists and has content
        if not os.path.exists(train_data_path) or os.path.getsize(train_data_path) == 0:
            logger.error(f"❌ Training data file is empty or missing: {train_data_path}")
            return
        
        logger.info(f"📊 Training data size: {os.path.getsize(train_data_path)} bytes")
        
        # Load model with 4-bit quantization (more stable than 8-bit)
        logger.info("📥 Loading base model...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16
        )
        
        tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        
        # Add padding token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
        
        # Prepare model for k-bit training
        model = prepare_model_for_kbit_training(model)
        
        # LoRA configuration - Updated for DialoGPT model
        lora_config = LoraConfig(
            r=16,  # Higher rank for better performance
            lora_alpha=32,  # Keep alpha = 2 * rank
            target_modules=["c_attn", "c_proj"],  # DialoGPT specific modules
            lora_dropout=0.1,  # Higher dropout for regularization
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            init_lora_weights=True
        )
        
        # Apply LoRA
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        # Load dataset
        logger.info("📊 Loading training data...")
        try:
            dataset = load_dataset(
                "json",
                data_files={
                    "train": train_data_path,
                    "validation": val_data_path
                },
                streaming=False
            )
            logger.info(f"✅ Loaded dataset: {len(dataset['train'])} train, {len(dataset['validation'])} val samples")
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            return
        
        # Tokenize function with better formatting
        def tokenize_function(examples):
            # Create instruction format following Alpaca style
            texts = []
            for i in range(len(examples["instruction"])):
                instruction = examples["instruction"][i]
                input_text = examples["input"][i] if examples["input"][i] else ""
                output = examples["output"][i]
                
                # Use Alpaca format
                if input_text:
                    text = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
                else:
                    text = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:\n{output}"
                
                texts.append(text)
            
            # Tokenize with proper settings
            tokenized = tokenizer(
                texts,
                truncation=True,
                padding=True,  # Enable padding for consistent tensor shapes
                max_length=512,
                return_tensors="pt"
            )
            
            # Set labels same as input_ids for causal LM
            tokenized["labels"] = tokenized["input_ids"].clone()
            return tokenized
        
        # Tokenize datasets
        logger.info("🔄 Tokenizing datasets...")
        train_dataset = dataset["train"].map(tokenize_function, batched=True, remove_columns=dataset["train"].column_names)
        val_dataset = dataset["validation"].map(tokenize_function, batched=True, remove_columns=dataset["validation"].column_names)
        
        # Data collator for dynamic padding
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # We're doing causal LM, not masked LM
        )
        
        # Training arguments - Updated based on 2024 best practices
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=2,  # Smaller batch size for stability
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=8,  # Simulate larger batch size
            num_train_epochs=3,
            learning_rate=0.0003,  # Slightly higher LR
            fp16=False,  # Use bfloat16 instead
            bf16=True,  # Better numerical stability
            logging_steps=10,
            eval_strategy="steps",
            eval_steps=50,
            save_steps=100,
            save_total_limit=3,
            load_best_model_at_end=True,
            report_to=None,  # Disable wandb/tensorboard
            remove_unused_columns=False,
            gradient_checkpointing=True,  # Save memory
            dataloader_pin_memory=False,  # Reduce memory usage
            warmup_steps=100,  # Add warmup
            lr_scheduler_type="cosine",  # Better learning rate schedule
            weight_decay=0.01,  # Add weight decay for regularization
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
        )
        
        # Start training
        logger.info("🏃 Starting training...")
        trainer.train()
        
        # Save model
        logger.info("💾 Saving trained model...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        logger.info("✅ LoRA training completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
