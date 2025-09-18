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
                    maker TEXT,
                    version TEXT,
                    base_model TEXT NOT NULL,
                    model_name TEXT,  -- The actual model name that will be created
                    dataset_id INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    training_type TEXT DEFAULT 'LoRA',
                    progress REAL DEFAULT 0.0,
                    metrics TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    config TEXT,  -- JSON object for training configuration
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
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
    
    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets from the database"""
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
                dataset['metadata'] = json.loads(dataset['metadata']) if dataset['metadata'] else {}
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
            
            cursor.execute('''
                INSERT INTO training_jobs (
                    name, description, job_type, maker, version, base_model, model_name,
                    dataset_id, status, training_type, progress, metrics, config
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('name'),
                job_data.get('description', ''),
                job_data.get('job_type', 'experimental'),
                job_data.get('maker', ''),
                job_data.get('version', ''),
                job_data.get('base_model'),
                job_data.get('model_name'),
                job_data.get('dataset_id'),
                job_data.get('status', 'PENDING'),
                job_data.get('training_type', 'LoRA'),
                job_data.get('progress', 0.0),
                metrics_json,
                config_json
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
                    after_metrics, improvement, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                eval_data.get('model_name'),
                eval_data.get('dataset_id'),
                eval_data.get('evaluation_type', 'accuracy'),
                before_metrics_json,
                after_metrics_json,
                eval_data.get('improvement'),
                eval_data.get('notes')
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
