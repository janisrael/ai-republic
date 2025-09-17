"""
ChromaDB Service for AI Refinement Dashboard
Provides professional-grade vector database operations for RAG training
"""

import os
import json
import math
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class ChromaDBService:
    """Service class for ChromaDB vector operations"""
    
    def __init__(self, persist_directory: str = None):
        """Initialize ChromaDB service"""
        if persist_directory is None:
            persist_directory = os.path.join(os.path.dirname(__file__), 'chromadb_data')
        
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        print(f"✅ ChromaDB initialized at {persist_directory}")
    
    def create_collection(self, collection_name: str, description: str = "") -> bool:
        """Create a new collection"""
        try:
            # Check if collection already exists
            try:
                existing_collection = self.client.get_collection(collection_name)
                print(f"📁 Collection '{collection_name}' already exists")
                return True
            except:
                pass
            
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": description}
            )
            print(f"✅ Created collection '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error creating collection '{collection_name}': {e}")
            return False
    
    def get_collection(self, collection_name: str):
        """Get existing collection"""
        try:
            return self.client.get_collection(collection_name)
        except Exception as e:
            print(f"❌ Error getting collection '{collection_name}': {e}")
            return None
    
    def ingest_dataset(self, collection_name: str, dataset_data: List[Dict[str, Any]], 
                      batch_size: int = 512) -> bool:
        """Ingest dataset into ChromaDB collection"""
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return False
            
            # Extract text content from dataset
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(dataset_data):
                # Extract text content (prioritize 'output', then 'instruction', then 'code')
                text_content = ""
                if 'output' in item:
                    text_content = item['output']
                elif 'instruction' in item:
                    text_content = item['instruction']
                elif 'code' in item:
                    text_content = item['code']
                elif 'text' in item:
                    text_content = item['text']
                else:
                    # Fallback: convert entire item to string
                    text_content = str(item)
                
                if text_content.strip():
                    documents.append(text_content)
                    metadatas.append({
                        "source": item.get('source', 'dataset'),
                        "type": item.get('type', 'text'),
                        "index": i
                    })
                    ids.append(f"doc-{i}")
            
            if not documents:
                print("❌ No valid documents found in dataset")
                return False
            
            print(f"📊 Ingesting {len(documents)} documents into '{collection_name}'")
            
            # Process in batches to avoid memory issues
            num_batches = math.ceil(len(documents) / batch_size)
            
            for batch_idx in range(num_batches):
                start = batch_idx * batch_size
                end = min((batch_idx + 1) * batch_size, len(documents))
                
                batch_docs = documents[start:end]
                batch_metadatas = metadatas[start:end]
                batch_ids = ids[start:end]
                
                # Generate embeddings
                batch_embeddings = self.embed_model.encode(
                    batch_docs, 
                    show_progress_bar=True
                ).tolist()
                
                # Add to collection
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids,
                    embeddings=batch_embeddings
                )
                
                print(f"✅ Batch {batch_idx+1}/{num_batches} ingested ({len(batch_docs)} docs)")
            
            print(f"🎉 Successfully ingested {len(documents)} documents into '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error ingesting dataset: {e}")
            return False
    
    def query_collection(self, collection_name: str, query_text: str, 
                        n_results: int = 5) -> List[Dict[str, Any]]:
        """Query collection for similar documents"""
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return []
            
            # Generate query embedding
            query_embedding = self.embed_model.encode([query_text]).tolist()
            
            # Query collection
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else f"result-{i}"
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error querying collection '{collection_name}': {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return {}
            
            count = collection.count()
            return {
                'name': collection_name,
                'count': count,
                'metadata': collection.metadata
            }
            
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return {}
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            print(f"✅ Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"❌ Error deleting collection '{collection_name}': {e}")
            return False
    
    def create_knowledge_base(self, job_id: int, dataset_data: List[Dict[str, Any]]) -> bool:
        """Create a knowledge base for a specific training job"""
        collection_name = f"job_{job_id}_kb"
        
        # Create collection
        if not self.create_collection(collection_name, f"Knowledge base for training job {job_id}"):
            return False
        
        # Ingest dataset
        return self.ingest_dataset(collection_name, dataset_data)
    
    def query_knowledge_base(self, job_id: int, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query knowledge base for a specific training job"""
        collection_name = f"job_{job_id}_kb"
        return self.query_collection(collection_name, query, n_results)


# Global instance
chromadb_service = ChromaDBService()


if __name__ == "__main__":
    # Test the service
    print("🧪 Testing ChromaDB Service...")
    
    # Test data
    test_data = [
        {
            "output": "def hello_world():\n    print('Hello, World!')",
            "instruction": "Create a simple hello world function",
            "source": "test"
        },
        {
            "output": "def add_numbers(a, b):\n    return a + b",
            "instruction": "Create a function to add two numbers",
            "source": "test"
        }
    ]
    
    # Test collection creation and ingestion
    if chromadb_service.create_collection("test_collection", "Test collection"):
        if chromadb_service.ingest_dataset("test_collection", test_data):
            # Test query
            results = chromadb_service.query_collection("test_collection", "hello world function", 2)
            print(f"🔍 Query results: {len(results)} documents found")
            for result in results:
                print(f"  - {result['document'][:50]}...")
    
    print("✅ ChromaDB Service test completed!")
