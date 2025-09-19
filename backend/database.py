#!/usr/bin/env python3
"""
Database module for AI Refinement Dashboard
Handles SQLite database operations for datasets and training jobs
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'ai_dashboard.db')

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create datasets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    dataset_id TEXT UNIQUE,
                    type TEXT DEFAULT 'Text',
                    sample_count INTEGER DEFAULT 0,
                    loaded_samples INTEGER DEFAULT 0,
                    size TEXT,
                    format TEXT,
                    license TEXT,
                    tags TEXT,  -- JSON array
                    is_favorite BOOLEAN DEFAULT FALSE,
                    is_public BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    metadata TEXT  -- JSON object for additional data
                )
            ''')
            
            # Create training_jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    job_type TEXT DEFAULT 'experimental',
                    custom_capabilities TEXT,  -- JSON array of custom capabilities
                    maker TEXT,
                    version TEXT,
                    base_model TEXT NOT NULL,
                    model_name TEXT,  -- The actual model name that will be created
                    dataset_id INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    training_type TEXT DEFAULT 'LoRA',
                    progress REAL DEFAULT 0.0,
                    metrics TEXT,  -- JSON object
                    temperature REAL DEFAULT 0.7,
                    top_p REAL DEFAULT 0.9,
                    context_length INTEGER DEFAULT 4096,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    config TEXT,  -- JSON object for training configuration
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            ''')
            
            # Add new columns to existing table if they don't exist
            self.migrate_training_jobs_table()
            
            # Create model_profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT UNIQUE NOT NULL,
                    training_job_id INTEGER,
                    avatar_path TEXT,
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (training_job_id) REFERENCES training_jobs (id)
                )
            ''')
            
            # Create evaluations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    dataset_id INTEGER,
                    evaluation_type TEXT DEFAULT 'accuracy',
                    before_metrics TEXT,  -- JSON object
                    after_metrics TEXT,   -- JSON object
                    improvement REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            ''')
            
            conn.commit()
            print(f"✅ Database initialized at {self.db_path}")
    
    def add_dataset(self, dataset_data: Dict[str, Any]) -> int:
        """Add a new dataset to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare data
            tags_json = json.dumps(dataset_data.get('tags', []))
            metadata_json = json.dumps(dataset_data.get('metadata', {}))
            
            cursor.execute('''
                INSERT INTO datasets (
                    name, description, dataset_id, type, sample_count, loaded_samples,
                    size, format, license, tags, is_favorite, is_public, source, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_data.get('name'),
                dataset_data.get('description'),
                dataset_data.get('dataset_id'),
                dataset_data.get('type', 'Text'),
                dataset_data.get('sample_count', 0),
                dataset_data.get('loaded_samples', 0),
                dataset_data.get('size'),
                dataset_data.get('format'),
                dataset_data.get('license'),
                tags_json,
                dataset_data.get('is_favorite', False),
                dataset_data.get('is_public', True),
                dataset_data.get('source'),
                metadata_json
            ))
            
            dataset_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Dataset '{dataset_data.get('name')}' added with ID {dataset_id}")
            return dataset_id
    
    def migrate_training_jobs_table(self):
        """Add new columns to training_jobs table if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if columns exist and add them if they don't
            cursor.execute("PRAGMA table_info(training_jobs)")
            columns = [column[1] for column in cursor.fetchall()]
            
            new_columns = [
                ('custom_capabilities', 'TEXT'),
                ('temperature', 'REAL DEFAULT 0.7'),
                ('top_p', 'REAL DEFAULT 0.9'),
                ('context_length', 'INTEGER DEFAULT 4096')
            ]
            
            for column_name, column_def in new_columns:
                if column_name not in columns:
                    try:
                        cursor.execute(f'ALTER TABLE training_jobs ADD COLUMN {column_name} {column_def}')
                        print(f"✅ Added column {column_name} to training_jobs table")
                    except sqlite3.Error as e:
                        print(f"⚠️ Could not add column {column_name}: {e}")
            
            conn.commit()
    
    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets from the database (lightweight version for API)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM datasets ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            datasets = []
            for row in rows:
                dataset = dict(row)
                # Parse JSON fields
                dataset['tags'] = json.loads(dataset['tags']) if dataset['tags'] else []
                
                # Parse metadata but remove heavy fields for API response
                metadata = json.loads(dataset['metadata']) if dataset['metadata'] else {}
                
                # Keep only essential metadata fields
                lightweight_metadata = {
                    'loaded_at': metadata.get('loaded_at'),
                    'split_used': metadata.get('split_used'),
                    'format_analysis': metadata.get('format_analysis'),  # Include format analysis!
                    'samples_preview': metadata.get('samples_preview', [])[:5]  # Only first 5 samples for preview
                }
                
                dataset['metadata'] = lightweight_metadata
                datasets.append(dataset)
            
            return datasets
    
    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific dataset by its Hugging Face ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM datasets WHERE dataset_id = ?', (dataset_id,))
            row = cursor.fetchone()
            
            if row:
                dataset = dict(row)
                dataset['tags'] = json.loads(dataset['tags']) if dataset['tags'] else []
                dataset['metadata'] = json.loads(dataset['metadata']) if dataset['metadata'] else {}
                return dataset
            
            return None
    
    def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Update a dataset"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update fields
            update_fields = []
            values = []
            
            for key, value in updates.items():
                if key == 'tags':
                    update_fields.append(f"{key} = ?")
                    values.append(json.dumps(value))
                elif key == 'metadata':
                    update_fields.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("last_modified = CURRENT_TIMESTAMP")
            values.append(dataset_id)
            
            query = f"UPDATE datasets SET {', '.join(update_fields)} WHERE dataset_id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM datasets WHERE dataset_id = ?', (dataset_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def toggle_favorite(self, dataset_id: str) -> bool:
        """Toggle favorite status of a dataset"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE datasets 
                SET is_favorite = NOT is_favorite, last_modified = CURRENT_TIMESTAMP 
                WHERE dataset_id = ?
            ''', (dataset_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_training_job(self, job_data: Dict[str, Any]) -> int:
        """Add a new training job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            metrics_json = json.dumps(job_data.get('metrics', {}))
            config_json = json.dumps(job_data.get('config', {}))
            
            # Handle custom capabilities
            custom_capabilities_json = json.dumps(job_data.get('custom_capabilities', []))
            
            cursor.execute('''
                INSERT INTO training_jobs (
                    name, description, job_type, custom_capabilities, maker, version, base_model, model_name,
                    dataset_id, status, training_type, progress, metrics, config, temperature, top_p, context_length
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('name'),
                job_data.get('description', ''),
                job_data.get('job_type', 'experimental'),
                custom_capabilities_json,
                job_data.get('maker', ''),
                job_data.get('version', ''),
                job_data.get('base_model'),
                job_data.get('model_name'),
                job_data.get('dataset_id'),
                job_data.get('status', 'PENDING'),
                job_data.get('training_type', 'LoRA'),
                job_data.get('progress', 0.0),
                metrics_json,
                config_json,
                job_data.get('temperature', 0.7),
                job_data.get('top_p', 0.9),
                job_data.get('context_length', 4096)
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            return job_id
    
    def get_training_jobs(self) -> List[Dict[str, Any]]:
        """Get all training jobs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM training_jobs ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            jobs = []
            for row in rows:
                job = dict(row)
                job['metrics'] = json.loads(job['metrics']) if job['metrics'] else {}
                job['config'] = json.loads(job['config']) if job['config'] else {}
                jobs.append(job)
            
            return jobs
    
    def get_all_training_jobs(self) -> List[Dict[str, Any]]:
        """Get all training jobs (alias for get_training_jobs)"""
        return self.get_training_jobs()
    
    def get_training_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a training job by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM training_jobs WHERE id = ?', (job_id,))
            row = cursor.fetchone()
            
            if row:
                job = dict(row)
                job['metrics'] = json.loads(job['metrics']) if job['metrics'] else {}
                job['config'] = json.loads(job['config']) if job['config'] else {}
                return job
            
            return None
    
    def get_training_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a training job by ID (alias for get_training_job_by_id)"""
        return self.get_training_job_by_id(job_id)
    
    def update_training_job(self, job_id: int, updates: Dict[str, Any]) -> bool:
        """Update a training job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update fields
            update_fields = []
            values = []
            
            for key, value in updates.items():
                if key in ['metrics', 'config']:
                    update_fields.append(f"{key} = ?")
                    values.append(json.dumps(value) if isinstance(value, (dict, list)) else value)
                else:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            values.append(job_id)
            query = f"UPDATE training_jobs SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            
            # Check if training job was marked as COMPLETED and create automatic evaluation
            if 'status' in updates and updates['status'] == 'COMPLETED':
                self._create_automatic_evaluation(job_id)
            
            return cursor.rowcount > 0
    
    def delete_training_job(self, job_id: int) -> bool:
        """Delete a training job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM training_jobs WHERE id = ?", (job_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_evaluation(self, eval_data: Dict[str, Any]) -> int:
        """Add a new evaluation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            before_metrics_json = json.dumps(eval_data.get('before_metrics', {}))
            after_metrics_json = json.dumps(eval_data.get('after_metrics', {}))
            
            cursor.execute('''
                INSERT INTO evaluations (
                    model_name, dataset_id, evaluation_type, before_metrics,
                    after_metrics, improvement, notes, status, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                eval_data.get('model_name'),
                eval_data.get('dataset_id'),
                eval_data.get('evaluation_type', 'accuracy'),
                before_metrics_json,
                after_metrics_json,
                eval_data.get('improvement'),
                eval_data.get('notes'),
                eval_data.get('status', 'PENDING'),
                eval_data.get('completed_at')
            ))
            
            eval_id = cursor.lastrowid
            conn.commit()
            return eval_id
    
    def get_evaluations(self) -> List[Dict[str, Any]]:
        """Get all evaluations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM evaluations ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            evaluations = []
            for row in rows:
                eval_data = dict(row)
                eval_data['before_metrics'] = json.loads(eval_data['before_metrics']) if eval_data['before_metrics'] else {}
                eval_data['after_metrics'] = json.loads(eval_data['after_metrics']) if eval_data['after_metrics'] else {}
                evaluations.append(eval_data)
            
            return evaluations
    
    def update_evaluation(self, eval_id: int, updates: Dict[str, Any]) -> bool:
        """Update an evaluation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update fields
            update_fields = []
            values = []
            
            for key, value in updates.items():
                if key in ['before_metrics', 'after_metrics']:
                    update_fields.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(eval_id)
            
            query = f"UPDATE evaluations SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
    
    # Model Profile Methods
    def add_model_profile(self, profile_data: Dict[str, Any]) -> int:
        """Add a new model profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO model_profiles (model_name, training_job_id, avatar_path, avatar_url)
                VALUES (?, ?, ?, ?)
            ''', (
                profile_data['model_name'],
                profile_data.get('training_job_id'),
                profile_data.get('avatar_path'),
                profile_data.get('avatar_url')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_model_profile(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model profile by model name"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM model_profiles WHERE model_name = ?
            ''', (model_name,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_model_profiles(self) -> List[Dict[str, Any]]:
        """Get all model profiles"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM model_profiles ORDER BY created_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_model_profile(self, model_name: str, updates: Dict[str, Any]) -> bool:
        """Update model profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update fields
            update_fields = []
            update_values = []
            
            for key, value in updates.items():
                if key in ['avatar_path', 'avatar_url']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(model_name)
            
            query = f"UPDATE model_profiles SET {', '.join(update_fields)} WHERE model_name = ?"
            cursor.execute(query, update_values)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_model_profile(self, model_name: str) -> bool:
        """Delete model profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM model_profiles WHERE model_name = ?", (model_name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _create_automatic_evaluation(self, job_id: int):
        """Create automatic evaluation when training job completes"""
        try:
            # Get the completed training job
            job = self.get_training_job_by_id(job_id)
            if not job:
                print(f"❌ Could not find training job {job_id} for automatic evaluation")
                return
            
            model_name = job.get('model_name')
            if not model_name:
                print(f"❌ Training job {job_id} has no model_name for evaluation")
                return
            
            # Get the actual Ollama model name from the training job
            actual_model_name = job.get('actual_model_name')
            if not actual_model_name:
                # Fallback: convert model name to actual Ollama model name (replace version with :latest)
                if ':' in model_name:
                    base_name = model_name.split(':')[0]
                    actual_model_name = f"{base_name}:latest"
                else:
                    actual_model_name = model_name
                print(f"⚠️ No actual_model_name found, using fallback: {model_name} -> {actual_model_name}")
            else:
                print(f"✅ Using stored actual model name: {actual_model_name}")
            
            # Verify the model exists in Ollama
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
                if actual_model_name not in result.stdout:
                    print(f"⚠️ Model {actual_model_name} not found in Ollama, using fallback")
                    if ':' in model_name:
                        base_name = model_name.split(':')[0]
                        actual_model_name = f"{base_name}:latest"
                    else:
                        actual_model_name = model_name
            except:
                print(f"⚠️ Could not verify model existence, using {actual_model_name}")
            
            # Parse config to get dataset information
            config = {}
            if job.get('config'):
                try:
                    config = json.loads(job['config']) if isinstance(job['config'], str) else job['config']
                except:
                    config = {}
            
            # Get the first selected dataset for evaluation
            selected_datasets = config.get('selectedDatasets', [])
            if not selected_datasets:
                print(f"❌ Training job {job_id} has no selected datasets for evaluation")
                return
            
            dataset_id = selected_datasets[0]  # Use first dataset
            
            # Get base model from training job config
            base_model = config.get('baseModel', 'llama3.2:latest')
            
            # Create evaluation data
            eval_data = {
                'model_name': actual_model_name,  # Use actual Ollama model name
                'base_model': base_model,  # Base model for before/after comparison
                'dataset_id': dataset_id,
                'evaluation_type': 'accuracy',
                'notes': f'Automatic evaluation after {job.get("training_type", "training")} completion'
            }
            
            # Add evaluation to database
            eval_id = self.add_evaluation(eval_data)
            print(f"✅ Created automatic evaluation {eval_id} for model {model_name}")
            
            # Start the evaluation
            try:
                from evaluation_executor import evaluation_executor
                success = evaluation_executor.start_evaluation(eval_id, eval_data)
                if success:
                    print(f"🚀 Started automatic evaluation {eval_id} for {model_name}")
                else:
                    print(f"❌ Failed to start automatic evaluation {eval_id}")
            except Exception as e:
                print(f"❌ Error starting automatic evaluation {eval_id}: {e}")
                
        except Exception as e:
            print(f"❌ Error creating automatic evaluation for job {job_id}: {e}")

# Global database instance
db = Database()

if __name__ == '__main__':
    # Test the database
    print("Testing database...")
    
    # Add a test dataset
    test_dataset = {
        'name': 'Test Dataset',
        'description': 'A test dataset',
        'dataset_id': 'test/test-dataset',
        'type': 'Text',
        'sample_count': 1000,
        'loaded_samples': 100,
        'size': '10 MB',
        'format': 'JSONL',
        'license': 'MIT',
        'tags': ['test', 'example'],
        'source': 'Test Source'
    }
    
    dataset_id = db.add_dataset(test_dataset)
    print(f"Added test dataset with ID: {dataset_id}")
    
    # Get all datasets
    datasets = db.get_all_datasets()
    print(f"Found {len(datasets)} datasets")
    
    for dataset in datasets:
        print(f"- {dataset['name']} ({dataset['sample_count']} samples)")
