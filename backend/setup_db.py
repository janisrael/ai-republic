#!/usr/bin/env python3
"""
Database Setup and Migration System for AI Refinement Dashboard
Handles database initialization, schema updates, and data migrations
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List

class DatabaseMigrator:
    def __init__(self, db_path: str = "ai_dashboard.db"):
        self.db_path = db_path
        self.migrations_dir = "migrations"
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
    
    def get_db_version(self) -> int:
        """Get current database version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.OperationalError:
            return 0
    
    def set_db_version(self, version: int):
        """Set database version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)",
                         (version, datetime.now().isoformat()))
            conn.commit()
    
    def create_schema_version_table(self):
        """Create schema version tracking table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def run_migration(self, version: int, description: str, migration_sql: str):
        """Run a single migration"""
        print(f"🔄 Running migration {version}: {description}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Execute migration SQL
            cursor.executescript(migration_sql)
            
            # Update schema version
            self.set_db_version(version)
            
            conn.commit()
        
        print(f"✅ Migration {version} completed")
    
    def run_all_migrations(self):
        """Run all pending migrations"""
        current_version = self.get_db_version()
        print(f"📊 Current database version: {current_version}")
        
        # Migration 1: Initial schema
        if current_version < 1:
            self.run_migration(1, "Initial database schema", '''
                -- Training Jobs Table
                CREATE TABLE IF NOT EXISTS training_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    job_type TEXT DEFAULT 'experimental',
                    maker TEXT,
                    version TEXT,
                    base_model TEXT,
                    model_name TEXT,
                    dataset_id INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    training_type TEXT DEFAULT 'lora',
                    progress REAL DEFAULT 0.0,
                    metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    config TEXT,
                    custom_capabilities TEXT,
                    temperature REAL DEFAULT 0.7,
                    top_p REAL DEFAULT 0.9,
                    context_length INTEGER DEFAULT 4096,
                    actual_model_name TEXT,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                );
                
                -- Datasets Table
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
                    tags TEXT,
                    source TEXT,
                    metadata TEXT,
                    is_favorite INTEGER DEFAULT 0,
                    is_public INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Evaluations Table
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    dataset_id INTEGER,
                    evaluation_type TEXT DEFAULT 'accuracy',
                    before_metrics TEXT,
                    after_metrics TEXT,
                    improvement REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    status TEXT DEFAULT 'PENDING',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                );
                
                -- Model Profiles Table
                CREATE TABLE IF NOT EXISTS model_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT UNIQUE NOT NULL,
                    training_job_id INTEGER,
                    avatar_path TEXT,
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (training_job_id) REFERENCES training_jobs(id)
                );
            ''')
        
        print(f"🎉 Database migration completed. Current version: {self.get_db_version()}")
    
    def reset_database(self):
        """Reset database (WARNING: This will delete all data!)"""
        print("⚠️  WARNING: This will delete all data!")
        confirm = input("Type 'RESET' to confirm: ")
        
        if confirm == "RESET":
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("🗑️  Database deleted")
            
            # Recreate schema
            self.create_schema_version_table()
            self.run_all_migrations()
            print("✅ Database reset completed")
        else:
            print("❌ Reset cancelled")
    
    def backup_database(self, backup_path: str = None):
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_ai_dashboard_{timestamp}.db"
        
        if os.path.exists(self.db_path):
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"💾 Database backed up to: {backup_path}")
        else:
            print("❌ Database file not found")
    
    def show_status(self):
        """Show database status and schema info"""
        print("📊 Database Status:")
        print(f"   Path: {self.db_path}")
        print(f"   Exists: {os.path.exists(self.db_path)}")
        print(f"   Version: {self.get_db_version()}")
        
        if os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"   Tables: {len(tables)}")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table[0]}: {count} records")

def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Refinement Dashboard Database Setup")
    parser.add_argument("--db-path", default="ai_dashboard.db", help="Database file path")
    parser.add_argument("--action", choices=["setup", "migrate", "reset", "backup", "status"], 
                       default="setup", help="Action to perform")
    parser.add_argument("--backup-path", help="Backup file path")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_path)
    
    if args.action == "setup":
        print("🚀 Setting up AI Refinement Dashboard database...")
        migrator.create_schema_version_table()
        migrator.run_all_migrations()
        migrator.show_status()
        
    elif args.action == "migrate":
        print("🔄 Running database migrations...")
        migrator.run_all_migrations()
        
    elif args.action == "reset":
        migrator.reset_database()
        
    elif args.action == "backup":
        migrator.backup_database(args.backup_path)
        
    elif args.action == "status":
        migrator.show_status()

if __name__ == "__main__":
    main()
