<template>
  <div class="datasets-container">
    <!-- Header with title and action buttons -->
    <div class="datasets-header">
      <h1>Datasets</h1>
      <div class="header-actions">
        <div class="sort-controls">
          <label for="sortBy">Sort by:</label>
          <select id="sortBy" v-model="sortBy" class="sort-select">
            <option value="name">Name</option>
            <option value="date">Date Added</option>
            <option value="samples">Sample Count</option>
          </select>
          <button 
            class="btn-icon sort-direction" 
            @click="sortDescending = !sortDescending"
            :title="sortDescending ? 'Sort descending' : 'Sort ascending'"
          >
            {{ sortDescending ? '↓' : '↑' }}
          </button>
        </div>
        <button class="btn btn-primary" @click="showUploadModal = true">
          <i>+</i> Upload Dataset
        </button>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="search-filter-bar">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search datasets..."
          class="search-input"
        >
        <span class="search-icon">🔍</span>
      </div>
      
      <div class="filters">
        <select v-model="selectedType" class="filter-select">
          <option value="">All Types</option>
          <option v-for="type in datasetTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        
        <select v-model="sortBy" class="filter-select">
          <option value="name">Sort by Name</option>
          <option value="date">Sort by Date</option>
          <option value="size">Sort by Size</option>
        </select>
      </div>
    </div>

    <!-- Datasets Grid -->
    <div class="datasets-grid">
      <div v-for="dataset in filteredDatasets" :key="dataset.id" class="dataset-card">
        <div class="dataset-header">
          <div class="dataset-icon">
            <span v-if="dataset.type === 'Image'" class="emoji">🖼️</span>
            <span v-else-if="dataset.type === 'Text'" class="emoji">📄</span>
            <span v-else class="emoji">📊</span>
          </div>
          <div class="dataset-actions">
            <button 
              class="btn-icon" 
              :class="{ 'favorite': dataset.isFavorite }"
              @click="toggleFavorite(dataset.id)"
            >
              {{ dataset.isFavorite ? '⭐' : '☆' }}
            </button>
            <div class="dropdown">
              <button class="btn-icon">⋮</button>
              <div class="dropdown-content">
                <a href="#" @click.prevent="viewDataset(dataset)">View Details</a>
                <a href="#" @click.prevent="editDataset(dataset)">Edit</a>
                <a href="#" @click.prevent="confirmDelete(dataset)" class="danger">Delete</a>
              </div>
            </div>
          </div>
        </div>
        
        <h3>{{ dataset.name }}</h3>
        <p class="dataset-description">{{ dataset.description }}</p>
        
        <div class="dataset-stats">
          <div class="stat">
            <span class="emoji">📊</span>
            <span>{{ dataset.samples.toLocaleString() }} samples</span>
          </div>
          <div class="stat">
            <span class="emoji">📅</span>
            <span>{{ formatDate(dataset.createdAt) }}</span>
          </div>
        </div>
        
        <div class="dataset-tags">
          <span class="tag" :class="dataset.type.toLowerCase()">{{ dataset.type }}</span>
          <span class="tag" v-if="dataset.isPublic">Public</span>
        </div>
      </div>
    </div>

    <!-- Upload Dataset Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Upload New Dataset</h2>
          <button class="btn-icon" @click="showUploadModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Dataset Name</label>
            <input type="text" v-model="newDataset.name" placeholder="Enter dataset name">
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newDataset.description" placeholder="Enter dataset description"></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Type</label>
              <select v-model="newDataset.type">
                <option v-for="type in datasetTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Visibility</label>
              <select v-model="newDataset.isPublic">
                <option :value="true">Public</option>
                <option :value="false">Private</option>
              </select>
            </div>
          </div>
          
          <div class="file-upload">
            <label>Upload Files</label>
            <div class="upload-area" @dragover.prevent @drop="handleDrop">
              <input 
                type="file" 
                ref="fileInput" 
                multiple 
                @change="handleFileSelect"
                style="display: none;"
              >
              <p>Drag & drop files here or <a href="#" @click.prevent="$refs.fileInput.click()">browse</a></p>
              <p v-if="files.length > 0" class="file-list">
                {{ files.length }} file(s) selected
              </p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showUploadModal = false">Cancel</button>
          <button class="btn btn-primary" @click="uploadDataset" :disabled="!canUpload">
            {{ isUploading ? 'Uploading...' : 'Upload Dataset' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Delete Dataset</h2>
          <button class="btn-icon" @click="showDeleteModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete the dataset "{{ datasetToDelete?.name }}"? This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn btn-danger" @click="deleteDataset">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DatasetsView',
  data() {
    return {
      searchQuery: '',
      selectedType: '',
      sortBy: 'date',
      showUploadModal: false,
      showDeleteModal: false,
      isUploading: false,
      files: [],
      datasetToDelete: null,
      newDataset: {
        name: '',
        description: '',
        type: 'Image',
        isPublic: true
      },
      // Sample data - replace with API call in production
      datasets: [
        {
          id: '1',
          name: 'Cats vs Dogs',
          description: 'A collection of labeled images of cats and dogs for classification',
          type: 'Image',
          type: 'Text',
          description: 'Customer reviews with sentiment labels for training sentiment analysis models.',
          sampleCount: 12500,
          createdAt: '2023-05-15T10:30:00Z',
          tags: ['sentiment', 'reviews', 'e-commerce'],
          isFavorite: true,
          lastModified: '2023-05-15T10:30:00Z',
          size: '2.4 GB',
          format: 'CSV',
          license: 'CC BY 4.0'
        },
        {
          id: 2,
          name: 'Product Images',
          type: 'Image',
          description: 'Collection of product images with object detection annotations.',
          sampleCount: 8500,
          createdAt: '2023-06-22T14:15:00Z',
          tags: ['images', 'object-detection', 'e-commerce'],
          isFavorite: false,
          lastModified: '2023-06-22T14:15:00Z',
          size: '5.7 GB',
          format: 'JPEG/PNG',
          license: 'Commercial'
        },
        {
          id: 3,
          name: 'Speech Commands',
          type: 'Audio',
          description: 'Audio recordings of spoken commands for voice recognition training.',
          sampleCount: 65000,
          createdAt: '2023-07-10T09:45:00Z',
          tags: ['audio', 'speech', 'commands'],
          isFavorite: true,
          lastModified: '2023-07-10T09:45:00Z',
          size: '8.2 GB',
          format: 'WAV',
          license: 'MIT'
        },
        {
          id: 4,
          name: 'Video Clips',
          type: 'Video',
          description: 'Short video clips for action recognition model training.',
          sampleCount: 1200,
          createdAt: '2023-08-05T16:20:00Z',
          tags: ['video', 'action-recognition'],
          isFavorite: false,
          lastModified: '2023-08-05T16:20:00Z',
          size: '15.3 GB',
          format: 'MP4',
          license: 'Custom'
        },
        {
          id: 5,
          name: 'Tabular Sales Data',
          type: 'Tabular',
          description: 'Historical sales data with multiple features for time series forecasting.',
          sampleCount: 50000,
          createdAt: '2023-04-18T11:10:00Z',
          tags: ['time-series', 'sales', 'forecasting'],
          isFavorite: false,
          lastModified: '2023-04-18T11:10:00Z',
          size: '1.2 GB',
          format: 'Parquet',
          license: 'Apache 2.0'
        }
      ],
      datasetTypes: ['Text', 'Image', 'Audio', 'Video', 'Tabular', 'Time Series', 'Other'],
      tagInput: ''
    };
  },
  computed: {
    filteredDatasets() {
      let filtered = this.datasets;
      
      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(dataset => 
          dataset.name.toLowerCase().includes(query) ||
          dataset.description.toLowerCase().includes(query) ||
          dataset.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      
      // Apply type filter
      if (this.selectedType) {
        filtered = filtered.filter(dataset => dataset.type === this.selectedType);
      }
      
      // Apply favorites filter
      if (this.showFavorites) {
        filtered = filtered.filter(dataset => dataset.isFavorite);
      }
      
      // Apply sorting
      return [...filtered].sort((a, b) => {
        let comparison = 0;
        
        switch (this.sortBy) {
          case 'name':
            comparison = a.name.localeCompare(b.name);
            break;
          case 'date':
            comparison = new Date(a.createdAt) - new Date(b.createdAt);
            break;
          case 'samples':
            comparison = a.sampleCount - b.sampleCount;
            break;
          default:
            comparison = 0;
        }
        
        return this.sortDescending ? -comparison : comparison;
      });
    },
    canUpload() {
      return this.newDataset.name && 
             this.newDataset.type && 
             this.newDataset.file && 
             !this.isUploading;
    },
    uploadProgressStyle() {
      return { width: `${this.uploadProgress}%` };
    }
  },
  methods: {
    formatDate(dateString) {
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      return new Date(dateString).toLocaleString(undefined, options);
    },
    
    toggleFavorite(id) {
      const dataset = this.datasets.find(d => d.id === id);
      if (dataset) {
        dataset.isFavorite = !dataset.isFavorite;
        this.showSuccessMessage(`${dataset.name} ${dataset.isFavorite ? 'added to' : 'removed from'} favorites`);
      }
    },
    
    viewDataset(id) {
      // In a real app, this would navigate to a detailed view
      const dataset = this.datasets.find(d => d.id === id);
      console.log('Viewing dataset:', dataset);
      // For now, just show an alert
      alert(`Viewing dataset: ${dataset.name}\n\n` +
            `Type: ${dataset.type}\n` +
            `Samples: ${dataset.sampleCount.toLocaleString()}\n` +
            `Created: ${this.formatDate(dataset.createdAt)}`);
    },
    
    confirmDelete(dataset) {
      this.datasetToDelete = dataset;
    },
    
    async deleteDataset() {
      if (!this.datasetToDelete) return;
      
      const datasetName = this.datasetToDelete.name;
      
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        this.datasets = this.datasets.filter(d => d.id !== this.datasetToDelete.id);
        this.datasetToDelete = null;
        
        this.showSuccessMessage(`"${datasetName}" has been deleted`);
      } catch (error) {
        console.error('Error deleting dataset:', error);
        this.showError('Failed to delete dataset. Please try again.');
      }
    },
    
    // File handling methods
    handleDrop(e) {
      e.preventDefault();
      this.dragOver = false;
      const files = e.dataTransfer.files;
      if (files.length) {
        this.handleFile(files[0]);
      }
    },
    
    handleFileSelect(e) {
      const files = e.target.files;
      if (files.length) {
        this.handleFile(files[0]);
      }
    },
    
    handleFile(file) {
      // Validate file type and size (e.g., 2GB max)
      const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
      
      if (file.size > maxSize) {
        this.showError('File size exceeds 2GB limit');
        return;
      }
      
      this.newDataset.file = file;
      
      // Create a preview if it's an image
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.newDataset.filePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        this.newDataset.filePreview = null;
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    
    // Tag management
    addTag() {
      const tag = this.tagInput.trim();
      if (tag && !this.newDataset.tags.includes(tag)) {
        this.newDataset.tags.push(tag);
      }
      this.tagInput = '';
    },
    
    removeTag(index) {
      this.newDataset.tags.splice(index, 1);
    },
    
    handleTagKeydown(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.addTag();
      } else if (e.key === 'Backspace' && !this.tagInput && this.newDataset.tags.length > 0) {
        this.newDataset.tags.pop();
      }
    },
    
    // Upload methods
    async uploadDataset() {
      if (!this.canUpload) return;
      
      this.isUploading = true;
      this.uploadError = null;
      this.uploadProgress = 0;
      
      try {
        // Simulate upload progress
        const progressInterval = setInterval(() => {
          this.uploadProgress = Math.min(this.uploadProgress + Math.random() * 10, 90);
        }, 200);
        
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        clearInterval(progressInterval);
        this.uploadProgress = 100;
        
        // Create new dataset
        const newId = Math.max(...this.datasets.map(d => d.id), 0) + 1;
        const newDataset = {
          id: newId,
          name: this.newDataset.name,
          type: this.newDataset.type,
          description: this.newDataset.description,
          sampleCount: Math.floor(Math.random() * 10000) + 1000,
          createdAt: new Date().toISOString(),
          lastModified: new Date().toISOString(),
          tags: [...this.newDataset.tags],
          isFavorite: false,
          size: this.formatFileSize(this.newDataset.file.size),
          format: this.newDataset.file.name.split('.').pop().toUpperCase(),
          license: 'Custom'
        };
        
        // Add to the beginning of the list
        this.datasets.unshift(newDataset);
        
        // Reset form
        this.resetForm();
        this.showUploadModal = false;
        
        // Show success message
        this.showSuccessMessage(`"${newDataset.name}" uploaded successfully!`);
        
        // Reset progress after a short delay
        setTimeout(() => {
          this.uploadProgress = 0;
        }, 500);
        
      } catch (error) {
        console.error('Error uploading dataset:', error);
        this.showError('Failed to upload dataset. Please try again.');
      } finally {
        this.isUploading = false;
        clearInterval(this.progressInterval);
      }
    },
    
    resetForm() {
      this.newDataset = {
        name: '',
        type: '',
        description: '',
        tags: [],
        file: null,
        filePreview: null
      };
      this.tagInput = '';
      this.uploadError = null;
      
      // Reset file input
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    
    // UI helpers
    showSuccessMessage(message) {
      this.successMessage = message;
      this.showSuccess = true;
      setTimeout(() => {
        this.showSuccess = false;
      }, 5000);
    },
    
    showError(message) {
      this.uploadError = message;
      setTimeout(() => {
        this.uploadError = null;
      }, 5000);
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    closeModal() {
      this.showUploadModal = false;
      this.resetForm();
    }
  }
};
</script>

<style scoped>
.datasets-container {
  padding: 2rem;
  /* max-width: 1400px; */
  margin: 0 auto;
}

/* Header styles */
.datasets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.datasets-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sort-controls label {
  font-size: 0.9rem;
  color: #555;
}

.sort-select {
  padding: 0.6rem 2rem 0.6rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  cursor: pointer;
  min-width: 120px;
}

.sort-direction {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-direction:hover {
  background-color: #eee;
  border-color: #ccc;
}

/* Search and filter bar */
.datasets-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background-color: white;
}

.search-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #777;
  pointer-events: none;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.6rem 2rem 0.6rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  cursor: pointer;
  min-width: 120px;
}

.filter-select:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

/* Button styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  white-space: nowrap;
}

.btn i {
  margin-right: 0.5rem;
  font-style: normal;
}

.btn-primary {
  background-color: #4a6cf7;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3a5ce4;
}

.btn-primary:disabled {
  background-color: #a8b8f8;
  cursor: not-allowed;
  opacity: 0.8;
}

.btn-outline {
  background-color: white;
  border: 1px solid #ddd;
  color: #555;
}

.btn-outline:hover:not(:disabled),
.btn-outline.active {
  background-color: #f8f9fa;
  border-color: #ccc;
}

.btn-outline.active {
  color: #4a6cf7;
  border-color: #4a6cf7;
  background-color: rgba(74, 108, 247, 0.1);
}

.btn-danger {
  background-color: #f44336;
  color: white;
  border: none;
}

.btn-danger:hover:not(:disabled) {
  background-color: #e53935;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1.1rem;
  color: #777;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background-color: #f0f0f0;
  color: #333;
}

/* Dataset cards grid */
.datasets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.dataset-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
  border: 1px solid #eee;
  position: relative;
  overflow: hidden;
}

.dataset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dataset-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.dataset-card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
  flex: 1;
  margin-right: 0.5rem;
  word-break: break-word;
}

.dataset-description {
  color: #666;
  font-size: 0.9rem;
  margin: 0 0 1.25rem 0;
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dataset-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #777;
  margin-bottom: 1rem;
}

.dataset-type {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.dataset-samples,
.dataset-date {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
}

.dataset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.tag {
  background-color: #f0f4f8;
  color: #486581;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s;
}

.tag:hover {
  background-color: #e0e7f1;
}

.dataset-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid #f0f0f0;
}

/* Favorite button */
.favorite-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #ffc107;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  opacity: 0.8;
}

.favorite-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.favorite-btn.favorited {
  color: #ffc107;
  opacity: 1;
  text-shadow: 0 0 8px rgba(255, 193, 7, 0.5);
}

/* Empty state */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 2rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: modalFadeIn 0.2s ease-out;
  overflow: hidden;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.delete-confirm .modal-body {
  padding: 2rem 1.5rem;
  text-align: center;
}

.delete-confirm .modal-body p {
  margin: 0 0 1.5rem;
  color: #444;
  line-height: 1.6;
}

/* Form styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #444;
  font-size: 0.9rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  background-color: white;
}

.form-control:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* Upload area */
.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  margin-bottom: 1.5rem;
  background-color: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #4a6cf7;
  background-color: rgba(74, 108, 247, 0.05);
}

.upload-area i {
  font-size: 2.5rem;
  color: #4a6cf7;
  margin-bottom: 1rem;
  display: block;
}

.upload-area p {
  margin: 0.5rem 0 0.25rem;
  color: #444;
  font-size: 1rem;
}

.upload-area small {
  color: #777;
  font-size: 0.85rem;
}

.upload-area a {
  color: #4a6cf7;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.upload-area a:hover {
  text-decoration: underline;
  color: #3a5ce4;
}

/* File preview */
.file-preview {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-preview-icon {
  font-size: 2rem;
  color: #4a6cf7;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 0.85rem;
  color: #666;
}

.remove-file {
  color: #f44336;
  cursor: pointer;
  padding: 0.5rem;
  margin: -0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.remove-file:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

/* Progress bar */
.progress-container {
  margin-top: 1rem;
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #4a6cf7;
  transition: width 0.3s ease;
  width: 0%;
}

/* Error message */
.error-message {
  color: #f44336;
  font-size: 0.85rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Success message */
.success-message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #4caf50;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1100;
  animation: slideIn 0.3s ease-out;
  max-width: 90%;
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Tag input */
.tag-input-container {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 0.5rem;
  min-height: 44px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  background-color: white;
}

.tag-input-container:focus-within {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.tag-input {
  flex: 1;
  min-width: 120px;
  border: none;
  outline: none;
  padding: 0.25rem 0.5rem;
  font-size: 0.9rem;
  background: transparent;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .datasets-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .sort-controls {
    justify-content: space-between;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters > * {
    width: 100%;
  }
  
  .datasets-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    margin: 1rem;
    max-height: 90vh;
  }
}

/* Animation for dataset cards */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dataset-card {
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
}

/* Add delay for each card */
.dataset-card:nth-child(1) { animation-delay: 0.05s; }
.dataset-card:nth-child(2) { animation-delay: 0.1s; }
.dataset-card:nth-child(3) { animation-delay: 0.15s; }
.dataset-card:nth-child(4) { animation-delay: 0.2s; }
.dataset-card:nth-child(5) { animation-delay: 0.25s; }
.dataset-card:nth-child(6) { animation-delay: 0.3s; }
</style>
