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
        <button class="btn btn-secondary" @click="showHuggingFaceModal = true" :disabled="isLoadingHF">
          <i>{{ isLoadingHF ? '⏳' : '🤗' }}</i> {{ isLoadingHF ? 'Loading...' : 'Load from Hugging Face' }}
        </button>
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
            <span>{{ dataset.sampleCount.toLocaleString() }} samples</span>
          </div>
          <div class="stat">
            <span class="emoji">📅</span>
            <span>{{ formatDate(dataset.createdAt) }}</span>
          </div>
          <div class="stat" v-if="dataset.formatAnalysis">
            <span class="emoji">{{ getFormatEmoji(dataset.formatAnalysis.format_type) }}</span>
            <span>{{ getFormatStatus(dataset.formatAnalysis) }}</span>
          </div>
        </div>
        
        <div class="dataset-tags">
          <span class="tag" :class="dataset.type.toLowerCase()">{{ dataset.type }}</span>
          <span class="tag" v-if="dataset.isPublic">Public</span>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoadingHF" class="loading-state">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading dataset from Hugging Face...</p>
        <small>This may take a few moments for large datasets</small>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="datasets.length === 0" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>No datasets yet</h3>
      <p>Get started by loading a dataset from Hugging Face or uploading your own data.</p>
      <div class="empty-actions">
        <button class="btn btn-secondary" @click="showHuggingFaceModal = true">
          <i>🤗</i> Load from Hugging Face
        </button>
        <button class="btn btn-primary" @click="showUploadModal = true">
          <i>+</i> Upload Dataset
        </button>
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
    
    <!-- Hugging Face Dataset Modal -->
    <div v-if="showHuggingFaceModal" class="modal-overlay" @click.self="showHuggingFaceModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>🤗 Load from Hugging Face</h2>
          <button class="btn-icon" @click="showHuggingFaceModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="hf-intro">
            <p>Load datasets directly from Hugging Face Datasets library. You can use any public dataset by providing its ID.</p>
            <div class="code-example">
              <code>from datasets import load_dataset<br>ds = load_dataset("your-dataset-id")</code>
            </div>
          </div>
          
          <!-- Popular Datasets -->
          <div class="popular-datasets">
            <h3>📊 Popular Datasets</h3>
            <div class="dataset-grid">
              <div class="dataset-card" @click="loadSpecificDataset('sahil2801/CodeAlpaca-20k')">
                <div class="dataset-icon">💻</div>
                <h4>CodeAlpaca-20k</h4>
                <p>20K code instruction-following examples</p>
                <span class="dataset-id">sahil2801/CodeAlpaca-20k</span>
              </div>
              <div class="dataset-card" @click="loadSpecificDataset('HuggingFaceH4/CodeAlpaca_20K')">
                <div class="dataset-icon">🐍</div>
                <h4>CodeAlpaca 20K</h4>
                <p>Python code generation dataset</p>
                <span class="dataset-id">HuggingFaceH4/CodeAlpaca_20K</span>
              </div>
              <div class="dataset-card" @click="loadSpecificDataset('iamtarun/python_code_instructions_18k_alpaca')">
                <div class="dataset-icon">🔧</div>
                <h4>Python Instructions</h4>
                <p>18K Python code instructions</p>
                <span class="dataset-id">iamtarun/python_code_instructions_18k_alpaca</span>
              </div>
              <div class="dataset-card" @click="loadSpecificDataset('code_x_glue_cc_defect_detection')">
                <div class="dataset-icon">🐛</div>
                <h4>Defect Detection</h4>
                <p>Code bug detection dataset</p>
                <span class="dataset-id">code_x_glue_cc_defect_detection</span>
              </div>
              <div class="dataset-card" @click="loadSpecificDataset('openai_humaneval')">
                <div class="dataset-icon">🧠</div>
                <h4>HumanEval</h4>
                <p>Code evaluation problems</p>
                <span class="dataset-id">openai_humaneval</span>
              </div>
              <div class="dataset-card" @click="loadSpecificDataset('flytech/python-codes-25k')">
                <div class="dataset-icon">⚡</div>
                <h4>Python Codes 25K</h4>
                <p>25K Python code examples</p>
                <span class="dataset-id">flytech/python-codes-25k</span>
              </div>
            </div>
          </div>
          
          <!-- Custom Dataset Input -->
          <div class="custom-dataset">
            <h3>🔗 Custom Dataset</h3>
            <div class="form-group">
              <label>Dataset Name <span class="required">*</span></label>
              <input 
                type="text" 
                v-model="customDataset.name" 
                placeholder="e.g., My Custom Code Dataset"
                class="dataset-input"
                required
              >
              <small>Give your dataset a descriptive name</small>
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="customDataset.description" 
                placeholder="Describe what this dataset contains and its purpose..."
                class="dataset-input"
                rows="3"
              ></textarea>
              <small>Optional description of the dataset content and use case</small>
            </div>
            
            <div class="form-group">
              <label>Hugging Face Dataset ID <span class="required">*</span></label>
              <input 
                type="text" 
                v-model="customDataset.datasetId" 
                placeholder="e.g., sahil2801/CodeAlpaca-20k"
                class="dataset-input"
                required
              >
              <small>Find datasets at <a href="https://huggingface.co/datasets" target="_blank">huggingface.co/datasets</a></small>
            </div>
            
            <button 
              class="btn btn-secondary" 
              @click="loadCustomDataset"
              :disabled="!customDataset.name.trim() || !customDataset.datasetId.trim() || isLoadingHF"
            >
              <i>{{ isLoadingHF ? '⏳' : '📥' }}</i> Load Custom Dataset
            </button>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showHuggingFaceModal = false">Cancel</button>
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
      isLoadingHF: false,
      showHuggingFaceModal: false,
      customDatasetId: '',
      customDataset: {
        name: '',
        description: '',
        datasetId: ''
      },
      files: [],
      datasetToDelete: null,
      newDataset: {
        name: '',
        description: '',
        type: 'Image',
        isPublic: true
      },
      // Real datasets loaded from Hugging Face or uploaded by user
      datasets: [],
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
  async mounted() {
    // Load datasets from API when component mounts
    await this.fetchDatasets();
  },
  methods: {
    async fetchDatasets() {
      try {
        console.log('Fetching datasets from API...');
        const response = await fetch('http://localhost:5000/api/datasets');
        const result = await response.json();
        
        if (result.success) {
          // Transform database format to frontend format
          this.datasets = result.datasets.map(dataset => {
            // Parse metadata to get format analysis
            let formatAnalysis = null;
            if (dataset.metadata) {
              try {
                const metadata = typeof dataset.metadata === 'string' 
                  ? JSON.parse(dataset.metadata) 
                  : dataset.metadata;
                formatAnalysis = metadata.format_analysis || null;
              } catch (e) {
                console.warn('Failed to parse dataset metadata:', e);
              }
            }
            
            return {
              id: dataset.id.toString(),
              name: dataset.name,
              description: dataset.description,
              type: dataset.type,
              sampleCount: dataset.sample_count,
              createdAt: dataset.created_at,
              tags: dataset.tags || [],
              isFavorite: Boolean(dataset.is_favorite),
              lastModified: dataset.last_modified,
              size: dataset.size,
              format: dataset.format,
              license: dataset.license,
              datasetId: dataset.dataset_id,
              source: dataset.source,
              formatAnalysis: formatAnalysis
            };
          });
          
          console.log(`Loaded ${this.datasets.length} datasets from API`);
        } else {
          console.error('Failed to fetch datasets:', result.error);
          this.showError('Failed to load datasets from server');
        }
      } catch (error) {
        console.error('Error fetching datasets:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
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
    
    viewDataset(dataset) {
      // In a real app, this would navigate to a detailed view
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
    
    getFormatEmoji(formatType) {
      const formatEmojis = {
        'standard_lora': '✅',
        'devops_format': '🔄',
        'qa_format': '❓',
        'unknown_format': '⚠️',
        'empty': '❌'
      };
      return formatEmojis[formatType] || '📋';
    },
    
    getFormatStatus(formatAnalysis) {
      if (!formatAnalysis) return 'Unknown Format';
      
      if (formatAnalysis.format_type === 'standard_lora') {
        return 'LoRA Ready';
      } else if (formatAnalysis.conversion_applied) {
        return `Converted (${formatAnalysis.format_type})`;
      } else if (formatAnalysis.is_lora_compatible) {
        return 'LoRA Compatible';
      } else {
        return 'Format Issue';
      }
    },
    
    closeModal() {
      this.showUploadModal = false;
      this.resetForm();
    },
    
    async loadFromHuggingFace() {
      this.isLoadingHF = true;
      try {
        // Show dataset selection modal
        const datasetChoice = await this.showDatasetSelectionModal();
        if (!datasetChoice) {
          this.isLoadingHF = false;
          return;
        }
        
        // Call backend API to load dataset
        const response = await fetch('http://localhost:5000/api/load-dataset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ dataset: datasetChoice })
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Add the new dataset to our local list
          const newDataset = {
            id: `hf-${Date.now()}`,
            name: result.message.includes('python') ? 'Python Code Dataset' : 'JavaScript Dataset',
            description: result.message.includes('python') 
              ? 'Python code snippets with instructions and outputs from Hugging Face'
              : 'JavaScript code snippets from Hugging Face',
            type: 'Text',
            sampleCount: result.message.includes('python') ? 559515 : 10000,
            createdAt: new Date().toISOString(),
            tags: result.message.includes('python') 
              ? ['python', 'code', 'huggingface', 'debugging']
              : ['javascript', 'code', 'huggingface'],
            isFavorite: true,
            lastModified: new Date().toISOString(),
            size: result.message.includes('python') ? '559 MB' : '45 MB',
            format: 'JSONL',
            license: 'Hugging Face'
          };
          
          this.datasets.unshift(newDataset);
          this.showSuccessMessage(`Successfully loaded ${newDataset.name} from Hugging Face!`);
        } else {
          this.showError(`Failed to load dataset: ${result.error}`);
        }
      } catch (error) {
        console.error('Error loading from Hugging Face:', error);
        this.showError('Failed to connect to backend. Make sure the API server is running.');
      } finally {
        this.isLoadingHF = false;
      }
    },
    
    async loadCustomDataset() {
      if (!this.customDataset.name.trim() || !this.customDataset.datasetId.trim()) {
        this.showError('Please provide both dataset name and Hugging Face dataset ID');
        return;
      }
      
      this.isLoadingHF = true;
      this.showHuggingFaceModal = false;
      
      try {
        console.log(`Loading custom dataset: ${this.customDataset.datasetId}`);
        
        // Call backend API to load dataset with custom name and description
        const response = await fetch('http://localhost:5000/api/load-dataset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            dataset_id: this.customDataset.datasetId,
            custom_name: this.customDataset.name,
            custom_description: this.customDataset.description
          })
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Store the name before resetting
          const datasetName = this.customDataset.name;
          
          // Reset the form
          this.customDataset = {
            name: '',
            description: '',
            datasetId: ''
          };
          
          // Refresh datasets list
          await this.fetchDatasets();
          this.showSuccessMessage(`Successfully loaded "${datasetName}" from Hugging Face!`);
        } else {
          this.showError(`Failed to load dataset: ${result.error}`);
        }
      } catch (error) {
        console.error('Error loading custom dataset:', error);
        this.showError('Failed to connect to backend. Make sure the API server is running.');
      } finally {
        this.isLoadingHF = false;
      }
    },
    
    async loadSpecificDataset(datasetId) {
      if (!datasetId || !datasetId.trim()) {
        this.showError('Please provide a valid dataset ID');
        return;
      }
      
      this.isLoadingHF = true;
      this.showHuggingFaceModal = false;
      
      try {
        console.log(`Loading dataset: ${datasetId}`);
        
        // Call backend API to load dataset
        const response = await fetch('http://localhost:5000/api/load-dataset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ dataset_id: datasetId })
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccessMessage(`Successfully loaded "${result.dataset.name}" with ${result.dataset.loaded_samples} samples!`);
          
          // Clear custom dataset input
          this.customDatasetId = '';
          
          // Refresh the datasets list from the API
          await this.fetchDatasets();
          
        } else {
          this.showError(result.error || 'Failed to load dataset from Hugging Face');
        }
        
      } catch (error) {
        console.error('Error loading dataset:', error);
        this.showError('Failed to load dataset. Please check the dataset ID and try again.');
      } finally {
        this.isLoadingHF = false;
      }
    },
    
    async showDatasetSelectionModal() {
      return new Promise((resolve) => {
        // Create a simple modal for dataset selection
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
          <div class="modal">
            <div class="modal-header">
              <h2>Select Hugging Face Dataset</h2>
              <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">✕</button>
            </div>
            <div class="modal-body">
              <div class="dataset-options">
                <label class="dataset-option">
                  <input type="radio" name="dataset" value="python" checked>
                  <div class="option-card">
                    <span class="emoji">🐍</span>
                    <div>
                      <strong>Python Code Dataset</strong>
                      <p>559K Python code snippets with instructions</p>
                    </div>
                  </div>
                </label>
                <label class="dataset-option">
                  <input type="radio" name="dataset" value="javascript">
                  <div class="option-card">
                    <span class="emoji">🌐</span>
                    <div>
                      <strong>JavaScript Dataset</strong>
                      <p>JavaScript code snippets and examples</p>
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
              <button class="btn btn-primary" onclick="
                const selected = document.querySelector('input[name=dataset]:checked').value;
                this.closest('.modal-overlay').remove();
                window.datasetSelection = selected;
              ">Load Dataset</button>
            </div>
          </div>
        `;
        
        document.body.appendChild(modal);
        
        // Wait for selection
        const checkSelection = () => {
          if (window.datasetSelection) {
            const selection = window.datasetSelection;
            delete window.datasetSelection;
            resolve(selection);
          } else {
            setTimeout(checkSelection, 100);
          }
        };
        
        // Handle modal close
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            modal.remove();
            resolve(null);
          }
        });
        
        checkSelection();
      });
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
  background: var(--card-bg);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light);
    transition: transform 0.3s 
ease;
}

.dataset-card:hover {
  transform: translateY(-3px);
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
  line-clamp: 3;
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
.dataset-date,
.dataset-format {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
}

.dataset-format {
  color: #4a6cf7;
  font-weight: 500;
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
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  z-index: 1000 !important;
  padding: 1rem;
  backdrop-filter: blur(2px);
  box-sizing: border-box;
}

.modal {
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
  position: relative;
  margin: auto;
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

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalFadeIn 0.3s ease-out;
  overflow: hidden;
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

/* Dataset Selection Modal */
.dataset-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.dataset-option {
  cursor: pointer;
}

.dataset-option input[type="radio"] {
  display: none;
}

.dataset-option .option-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: white;
}

.dataset-option input[type="radio"]:checked + .option-card {
  border-color: #4a6cf7;
  background: rgba(74, 108, 247, 0.05);
}

.dataset-option .option-card:hover {
  border-color: #4a6cf7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dataset-option .option-card .emoji {
  font-size: 2rem;
}

.dataset-option .option-card div {
  flex: 1;
}

.dataset-option .option-card strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #333;
}

.dataset-option .option-card p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
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

/* Hugging Face Modal Styles */
.hf-intro {
  margin-bottom: 2rem;
}

.hf-intro p {
  margin-bottom: 1rem;
  color: #666;
  line-height: 1.5;
}

.code-example {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  margin-bottom: 1rem;
}

.code-example code {
  color: #d63384;
  font-size: 0.9rem;
}

.popular-datasets {
  margin-bottom: 2rem;
}

.popular-datasets h3 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.2rem;
}

.dataset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}


/* 
.dataset-grid .dataset-card:hover {
  border-color: #4a6cf7;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(74, 108, 247, 0.15);
} */

.dataset-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.dataset-grid .dataset-card h4 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.1rem;
}

.dataset-grid .dataset-card p {
  margin: 0 0 1rem;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.dataset-id {
  display: inline-block;
  background: #f8f9fa;
  color: #6c757d;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.custom-dataset {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.required {
  color: #e74c3c;
  font-weight: bold;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #666;
  font-size: 0.85rem;
}

.dataset-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.dataset-input:focus {
  outline: none;
  border-color: #4e73df;
  box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
}

.dataset-input[required] {
  border-left: 4px solid #e74c3c;
}

.custom-dataset h3 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.2rem;
}

.dataset-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
  margin-bottom: 0.5rem;
}

.dataset-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.custom-dataset small {
  display: block;
  color: #6c757d;
  margin-bottom: 1rem;
}

.custom-dataset small a {
  color: #4a6cf7;
  text-decoration: none;
}

.custom-dataset small a:hover {
  text-decoration: underline;
}

/* Loading State */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  padding: 2rem;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a6cf7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.1rem;
}

.loading-spinner small {
  color: #666;
  font-size: 0.9rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: #f8f9fa;
  border-radius: 12px;
  margin-top: 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.empty-state h3 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1.5rem;
}

.empty-state p {
  margin: 0 0 2rem;
  color: #666;
  font-size: 1.1rem;
  line-height: 1.5;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.empty-actions .btn {
  min-width: 200px;
}
</style>
