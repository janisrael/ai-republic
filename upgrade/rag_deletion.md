# RAG Dataset Deletion Enhancement

## Current Problem

The current RAG system has a limitation where multiple datasets are merged into a single ChromaDB collection, making it impossible to remove individual datasets from a RAG model.

### Current Architecture Issues:
- All datasets get combined into one collection (`job_{id}_kb`)
- No separation between datasets in the collection
- No metadata to identify document sources
- Deletion is all-or-nothing at the collection level

## Proposed Solutions

### Solution 1: Separate Collections Per Dataset

#### Overview
Create individual ChromaDB collections for each dataset, allowing granular deletion.

#### Implementation:
```python
# Current approach
collection_name = f"job_{job_id}_kb"
chromadb_service.create_knowledge_base(job_id, all_samples)

# New approach
for dataset_id in dataset_ids:
    collection_name = f"job_{job_id}_dataset_{dataset_id}_kb"
    dataset_samples = get_dataset_samples(dataset_id)
    chromadb_service.create_knowledge_base(job_id, dataset_samples, collection_name)
```

#### Benefits:
- ✅ Individual dataset deletion
- ✅ Granular control over knowledge base
- ✅ Better organization
- ✅ Easier debugging and management

#### Drawbacks:
- ❌ More complex collection management
- ❌ Potential performance impact with multiple collections
- ❌ Requires RAG model to query multiple collections

#### Required Changes:
1. **ChromaDB Service**: Modify `create_knowledge_base()` to accept custom collection names
2. **RAG Training**: Update training logic to create separate collections
3. **RAG Model**: Update Modelfile to query multiple collections
4. **API Endpoints**: Add endpoints to manage individual dataset collections
5. **Frontend**: Update UI to show individual dataset management

### Solution 2: Document-Level Metadata Enhancement

#### Overview
Add metadata to each document indicating its source dataset, enabling selective deletion.

#### Implementation:
```python
def ingest_dataset_with_metadata(self, collection_name: str, dataset_data: List[Dict], dataset_id: str):
    """Ingest dataset with source metadata"""
    documents = []
    metadatas = []
    ids = []
    
    for i, item in enumerate(dataset_data):
        # Extract text content
        text_content = self._extract_text_content(item)
        
        documents.append(text_content)
        metadatas.append({
            "source_dataset": dataset_id,
            "source_type": "rag_training",
            "job_id": job_id,
            "original_index": i
        })
        ids.append(f"{dataset_id}_{i}")
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
```

#### Benefits:
- ✅ Single collection per job (simpler)
- ✅ Selective document deletion possible
- ✅ Better traceability
- ✅ Maintains current architecture

#### Drawbacks:
- ❌ Requires ChromaDB metadata filtering
- ❌ More complex deletion logic
- ❌ Potential performance impact on large collections

#### Required Changes:
1. **ChromaDB Service**: Add metadata support to ingestion
2. **Deletion API**: Implement metadata-based filtering
3. **Database Schema**: Track dataset-to-collection mapping
4. **Frontend**: Add individual dataset deletion UI

### Solution 3: Hybrid Approach (Recommended)

#### Overview
Combine both approaches: separate collections for major datasets, metadata for fine-grained control.

#### Implementation:
```python
class RAGKnowledgeManager:
    def __init__(self):
        self.collections = {}
        self.dataset_mapping = {}
    
    def create_knowledge_base(self, job_id: int, datasets: List[str]):
        """Create knowledge base with dataset separation"""
        for dataset_id in datasets:
            collection_name = f"job_{job_id}_ds_{dataset_id}_kb"
            self.collections[dataset_id] = collection_name
            self.dataset_mapping[collection_name] = dataset_id
            
            # Create collection with metadata
            self._create_collection_with_metadata(collection_name, dataset_id, job_id)
    
    def delete_dataset(self, job_id: int, dataset_id: str):
        """Delete specific dataset from knowledge base"""
        collection_name = f"job_{job_id}_ds_{dataset_id}_kb"
        return chromadb_service.delete_collection(collection_name)
    
    def get_available_datasets(self, job_id: int):
        """Get list of datasets in knowledge base"""
        return list(self.collections.keys())
```

## Implementation Plan

### Phase 1: Backend Enhancement
1. **ChromaDB Service Updates**
   - Add metadata support
   - Implement collection naming strategy
   - Add dataset-specific deletion methods

2. **API Endpoints**
   ```python
   # New endpoints
   GET    /api/rag/jobs/{job_id}/datasets          # List datasets in job
   DELETE /api/rag/jobs/{job_id}/datasets/{ds_id}  # Delete specific dataset
   GET    /api/rag/jobs/{job_id}/collections       # List collections
   ```

3. **Database Schema Updates**
   ```sql
   CREATE TABLE rag_dataset_mapping (
       id INTEGER PRIMARY KEY,
       job_id INTEGER,
       dataset_id INTEGER,
       collection_name TEXT,
       created_at TIMESTAMP,
       FOREIGN KEY (job_id) REFERENCES training_jobs(id)
   );
   ```

### Phase 2: Frontend Enhancement
1. **RAG Management UI**
   - Dataset list in RAG model details
   - Individual dataset deletion buttons
   - Confirmation dialogs

2. **Training Job Updates**
   - Show dataset breakdown in job details
   - Add dataset management section

### Phase 3: Migration Strategy
1. **Existing Jobs**
   - Create migration script for existing collections
   - Preserve current functionality during transition

2. **Backward Compatibility**
   - Support both old and new collection structures
   - Gradual migration of existing RAG models

## Example Usage

### Current (Problematic):
```bash
# Can only delete entire knowledge base
DELETE /api/chromadb/collections/job_4_kb
# Result: All datasets removed
```

### Enhanced (Proposed):
```bash
# List datasets in RAG job
GET /api/rag/jobs/4/datasets
# Response: ["5", "7", "12"]

# Delete specific dataset
DELETE /api/rag/jobs/4/datasets/5
# Result: Only dataset 5 removed, datasets 7 and 12 remain

# Check remaining datasets
GET /api/rag/jobs/4/datasets
# Response: ["7", "12"]
```

## Benefits of Enhancement

1. **Granular Control**: Remove individual datasets without affecting others
2. **Better Management**: Clear visibility into which datasets are used
3. **Flexibility**: Add/remove datasets dynamically
4. **Debugging**: Easier to identify problematic datasets
5. **User Experience**: More intuitive dataset management

## Technical Considerations

1. **Performance**: Multiple collections vs single collection with metadata
2. **Storage**: Additional metadata overhead
3. **Complexity**: More complex deletion and management logic
4. **Migration**: Handling existing RAG models
5. **API Design**: Clean, intuitive endpoints for dataset management

## Conclusion

The **Hybrid Approach** provides the best balance of functionality and maintainability, allowing both dataset-level and document-level control while maintaining system performance and simplicity.
