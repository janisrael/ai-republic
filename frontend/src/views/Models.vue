<template>
  <div class="models-container">
    <div class="page-header">
      <div>
      <h1>AI Models</h1>
      <p>Manage your machine learning models and their configurations</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModelModal = true">
        <i>🤖</i> New Model
      </button>
    </div>

    <!-- Model Actions -->
    <div class="models-actions">
      <div class="section-header">
        <h2>Model Management</h2>
      </div>
      
      <div class="actions-bar">
      <div class="search-box">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search models..." 
          v-model="searchQuery"
        />
        <span class="material-icons-round">search</span>
      </div>
      <div class="action-buttons">
        <select class="form-control" v-model="selectedType">
          <option value="">All Types</option>
          <option v-for="type in modelTypes" :key="type" :value="type">
            {{ type }}
          </option>
        </select>
          <button class="btn btn-secondary" @click="fetchLocalModels" :disabled="isLoadingModels">
            <span class="material-icons-round">{{ isLoadingModels ? 'refresh' : 'refresh' }}</span>
            <span>{{ isLoadingModels ? 'Loading...' : 'Refresh' }}</span>
        </button>
        </div>
      </div>
    </div>

    <!-- Model Filters -->
    <!-- <div class="filters-container card mb-4">
      <div class="card-body d-flex align-items-center flex-wrap gap-3 p-3">
        <div class="search-box position-relative flex-grow-1" style="max-width: 400px;">
          <input 
            type="text" 
            class="form-control ps-4" 
            placeholder="Search models..." 
            v-model="searchQuery"
          />
          <span class="material-icons-round position-absolute" style="left: 10px; top: 50%; transform: translateY(-50%); color: var(--dark);">
            search
          </span>
        </div>
        
        <div class="filter-group">
          <select class="form-select" v-model="selectedType">
            <option value="">All Types</option>
            <option v-for="type in modelTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <select class="form-select" v-model="sortBy">
            <option value="name">Name (A-Z)</option>
            <option value="date">Last Updated</option>
            <option value="accuracy">Accuracy</option>
          </select>
        </div>
      </div>
    </div> -->

    <!-- Loading State -->
    <div v-if="isLoadingModels" class="loading-state">
      <div class="loading-spinner">
        <span class="material-icons-round">refresh</span>
      </div>
      <p>Loading your local AI models...</p>
    </div>

    <!-- Models Section -->
    <div v-else class="models-section">
      <div class="section-header">
        <h2>Available Models</h2>
      </div>

    <div class="models-grid">
      <div 
        v-for="model in filteredModels" 
        :key="model.id" 
          class="model-card"
      >
          <div class="model-header">
            <h3>{{ model.name }}</h3>
            <span class="model-status" :class="model.type.toLowerCase()">
            {{ model.type }}
            </span>
            </div>
            <div class="model-details">
              <p>{{ model.description || 'No description provided' }}</p>
            <div class="model-meta">
              <span>{{ model.trainingTime }}</span>
              <span>{{ model.datasetSize }}</span>
          </div>
          
            <!-- Job Details Section -->
            <div v-if="model.jobDetails" class="job-details-section">
              <h4>Training Job Details</h4>
              <div class="job-metadata">
                <div class="metadata-row" v-if="model.jobDetails.jobName">
                  <span class="metadata-label">Job Name:</span>
                  <span class="metadata-value">{{ model.jobDetails.jobName }}</span>
            </div>
                <div class="metadata-row" v-if="model.jobDetails.description">
                  <span class="metadata-label">Description:</span>
                  <span class="metadata-value">{{ model.jobDetails.description }}</span>
            </div>
                <div class="metadata-row" v-if="model.jobDetails.jobType">
                  <span class="metadata-label">Type:</span>
                  <span class="metadata-value">{{ model.jobDetails.jobType }}</span>
            </div>
                <div class="metadata-row" v-if="model.jobDetails.maker">
                  <span class="metadata-label">Maker:</span>
                  <span class="metadata-value">{{ model.jobDetails.maker }}</span>
          </div>
                <div class="metadata-row" v-if="model.jobDetails.version">
                  <span class="metadata-label">Version:</span>
                  <span class="metadata-value">{{ model.jobDetails.version }}</span>
            </div>
                <div class="metadata-row" v-if="model.jobDetails.modelFile">
                  <span class="metadata-label">Model File:</span>
                  <span class="metadata-value model-file">{{ model.jobDetails.modelFile }}</span>
            </div>
          </div>
            </div>
          </div>
          <div class="model-actions">
            <button class="btn-icon" @click="viewModelDetails(model)">👁️</button>
            <button class="btn-icon" @click="deployModel(model)">🚀</button>
            <button class="btn-icon" @click="testModel(model)">▶️</button>
            <button class="btn-icon" @click="deleteModel(model.id)">🗑️</button>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredModels.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <h3>No models found</h3>
        <p>Get started by creating your first AI model or refreshing to load local models</p>
          <button class="btn btn-primary" @click="showCreateModelModal = true">
          <i>🤖</i> Create Model
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Model Modal -->
    <div v-if="showCreateModelModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content neumorphic-card">
        <div class="modal-header">
          <h2>{{ editingModel ? 'Edit Model' : 'Create New Model' }}</h2>
          <button class="btn-icon" @click="closeModal">
            ✕
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Model Name</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.name" 
              placeholder="e.g., Sentiment Analysis v2.0"
            />
          </div>
          
          <div class="form-group">
            <label>Model Type</label>
            <select class="form-control" v-model="modelForm.type">
              <option v-for="type in modelTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Description (Optional)</label>
            <textarea 
              class="form-control" 
              v-model="modelForm.description"
              rows="3"
              placeholder="A brief description of your model..."
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Tags (comma separated)</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="modelForm.tags"
              placeholder="e.g., nlp, classification, sentiment"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">
            Cancel
          </button>
          <button class="btn btn-primary" @click="saveModel">
            {{ editingModel ? 'Update Model' : 'Create Model' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content neumorphic-card">
        <div class="modal-header">
          <h2>Delete Model</h2>
          <button class="btn-icon" @click="showDeleteModal = false">
            ✕
          </button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ modelToDelete?.name }}</strong>? This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteModal = false">
            Cancel
          </button>
          <button class="btn btn-danger" @click="confirmDelete">
            Delete Permanently
          </button>
        </div>
      </div>
    </div>

    <!-- Model Deployment Modal -->
    <div v-if="showDeployModal" class="modal-overlay" @click.self="closeDeployModal">
      <div class="modal-content neumorphic-card">
        <div class="modal-header">
          <h2>Deploy Model: {{ selectedModel?.name }}</h2>
          <button class="btn-icon" @click="closeDeployModal">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="deployment-options">
            <h3>Deployment Options</h3>
            <div class="deployment-cards">
              <label class="deployment-card" :class="{ active: deploymentConfig.type === 'local' }">
                <input type="radio" v-model="deploymentConfig.type" value="local" hidden>
                <div class="deployment-icon">🖥️</div>
                <h4>Local Deployment</h4>
                <p>Deploy to local Ollama/llama.cpp instance</p>
                <div class="deployment-details">
                  <div class="form-group">
                    <label>Model Name</label>
                    <input type="text" v-model="deploymentConfig.modelName" class="form-control" placeholder="e.g., agimat-debugger">
                  </div>
                  <div class="form-group">
                    <label>Port</label>
                    <input type="number" v-model="deploymentConfig.port" class="form-control" placeholder="11434">
                  </div>
                </div>
              </label>
              
              <label class="deployment-card" :class="{ active: deploymentConfig.type === 'api' }">
                <input type="radio" v-model="deploymentConfig.type" value="api" hidden>
                <div class="deployment-icon">🌐</div>
                <h4>API Endpoint</h4>
                <p>Deploy as REST API service</p>
                <div class="deployment-details">
                  <div class="form-group">
                    <label>API Endpoint</label>
                    <input type="text" v-model="deploymentConfig.endpoint" class="form-control" placeholder="http://localhost:8000/api">
                  </div>
                  <div class="form-group">
                    <label>API Key</label>
                    <input type="password" v-model="deploymentConfig.apiKey" class="form-control" placeholder="Optional API key">
                  </div>
                </div>
              </label>
            </div>
          </div>
          
          <div class="deployment-settings">
            <h3>Deployment Settings</h3>
            <div class="settings-grid">
              <div class="form-group">
                <label>Max Tokens</label>
                <input type="number" v-model="deploymentConfig.maxTokens" class="form-control" placeholder="2048">
              </div>
              <div class="form-group">
                <label>Temperature</label>
                <input type="number" v-model="deploymentConfig.temperature" step="0.1" min="0" max="2" class="form-control" placeholder="0.7">
              </div>
              <div class="form-group">
                <label>Context Window</label>
                <input type="number" v-model="deploymentConfig.contextWindow" class="form-control" placeholder="4096">
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeDeployModal">Cancel</button>
          <button class="btn btn-primary" @click="deployModelNow" :disabled="!canDeploy">
            <span class="emoji">🚀</span> Deploy Model
          </button>
        </div>
      </div>
    </div>

    <!-- Model Testing Modal -->
    <div v-if="showTestModal" class="modal-overlay" @click.self="closeTestModal">
      <div class="modal-content neumorphic-card test-modal">
        <div class="modal-header">
          <h2>Test Model: {{ selectedModel?.name }}</h2>
          <button class="btn-icon" @click="closeTestModal">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="test-input">
            <div class="form-group">
              <label>Input Text</label>
              <textarea 
                v-model="testInput" 
                class="form-control" 
                rows="4"
                placeholder="Enter your test input here..."
              ></textarea>
            </div>
            
            <div class="test-options">
              <div class="form-group">
                <label>Temperature</label>
                <input type="range" v-model="testConfig.temperature" min="0" max="2" step="0.1" class="form-control">
                <span class="range-value">{{ testConfig.temperature }}</span>
              </div>
              <div class="form-group">
                <label>Max Tokens</label>
                <input type="number" v-model="testConfig.maxTokens" class="form-control" placeholder="100">
              </div>
            </div>
            
            <button class="btn btn-primary" @click="runTest" :disabled="!testInput.trim() || isTesting">
              <span v-if="isTesting" class="emoji">⏳</span>
              <span v-else class="emoji">▶️</span>
              {{ isTesting ? 'Testing...' : 'Run Test' }}
            </button>
          </div>
          
          <div v-if="testResult" class="test-result">
            <h3>Test Result</h3>
            <div class="result-content">
              <div class="result-text">{{ testResult.output }}</div>
              <div class="result-meta">
                <span class="meta-item">
                  <span class="emoji">⏱️</span>
                  Response Time: {{ testResult.responseTime }}ms
                </span>
                <span class="meta-item">
                  <span class="emoji">🔢</span>
                  Tokens: {{ testResult.tokens }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelsView',
  data() {
    return {
      searchQuery: '',
      selectedType: '',
      sortBy: 'name',
      activeDropdown: null,
      showCreateModelModal: false,
      showDeleteModal: false,
      showDeployModal: false,
      showTestModal: false,
      editingModel: null,
      modelToDelete: null,
      selectedModel: null,
      isTesting: false,
      testInput: '',
      testResult: null,
      testConfig: {
        temperature: 0.7,
        maxTokens: 100
      },
      deploymentConfig: {
        type: 'local',
        modelName: '',
        port: 11434,
        endpoint: '',
        apiKey: '',
        maxTokens: 2048,
        temperature: 0.7,
        contextWindow: 4096
      },
      models: [],
      modelTypes: ['NLP', 'Code', 'Image', 'Text', 'Audio', 'Video'],
      modelForm: {
        name: '',
        type: 'Image',
        description: '',
        tags: ''
      },
      modelCategories: [
        'Text Classification',
        'Image Classification',
        'Object Detection',
        'Text Generation',
        'Translation',
        'Summarization',
        'Question Answering',
        'Sentiment Analysis'
      ],
      isLoadingModels: false
    };
  },
  computed: {
    canDeploy() {
      if (this.deploymentConfig.type === 'local') {
        return this.deploymentConfig.modelName.trim() !== '';
      } else if (this.deploymentConfig.type === 'api') {
        return this.deploymentConfig.endpoint.trim() !== '';
      }
      return false;
    },
    filteredModels() {
      let filtered = [...this.models];
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(model => 
          model.name.toLowerCase().includes(query) ||
          model.description.toLowerCase().includes(query) ||
          (model.tags && model.tags.some(tag => tag.toLowerCase().includes(query)))
        );
      }
      
      // Filter by type
      if (this.selectedType) {
        filtered = filtered.filter(model => model.type === this.selectedType);
      }
      
      // Sort models
      return filtered.sort((a, b) => {
        if (this.sortBy === 'name') {
          return a.name.localeCompare(b.name);
        } else if (this.sortBy === 'date') {
          return new Date(b.updatedAt) - new Date(a.updatedAt);
        } else if (this.sortBy === 'accuracy') {
          return b.accuracy - a.accuracy;
        }
        return 0;
      });
    }
  },
  methods: {
    formatTimeAgo(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const now = new Date();
      const seconds = Math.floor((now - date) / 1000);
      
      const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
      };
      
      for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
          return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
        }
      }
      
      return 'just now';
    },
    getTypeBadgeClass(type) {
      const classes = {
        'Image': 'bg-primary bg-opacity-10 text-primary',
        'Text': 'bg-success bg-opacity-10 text-success',
        'Audio': 'bg-info bg-opacity-10 text-info',
        'Video': 'bg-warning bg-opacity-10 text-warning',
        'NLP': 'bg-danger bg-opacity-10 text-danger'
      };
      return classes[type] || 'bg-secondary bg-opacity-10 text-secondary';
    },
    getTypeColor(type) {
      const colors = {
        'Image': 'primary',
        'Text': 'success',
        'Audio': 'info',
        'Video': 'warning',
        'NLP': 'danger'
      };
      return colors[type] || 'secondary';
    },
    getModelIcon(type) {
      const icons = {
        'Image': 'image',
        'Text': 'text_fields',
        'Audio': 'mic',
        'Video': 'videocam',
        'NLP': 'psychology'
      };
      return icons[type] || 'model_training';
    },
    
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    toggleDropdown(event, modelId) {
      event.stopPropagation();
      this.activeDropdown = this.activeDropdown === modelId ? null : modelId;
    },
    
    closeDropdown() {
      this.activeDropdown = null;
    },
    
    viewModelDetails(model) {
      // In a real app, this would navigate to a detailed view
      console.log('Viewing model:', model.name);
    },
    
    toggleModelFavorite(model) {
      model.isFavorite = !model.isFavorite;
      // In a real app, you would update this in the backend
    },
    
    editModel(model) {
      this.editingModel = model;
      this.modelForm = {
        name: model.name,
        type: model.type,
        description: model.description,
        tags: model.tags.join(', ')
      };
      this.showCreateModelModal = true;
      this.closeDropdown();
    },
    
    duplicateModel(model) {
      const newModel = {
        ...model,
        id: Math.max(...this.models.map(m => m.id)) + 1,
        name: `${model.name} (Copy)`,
        isFavorite: false,
        updatedAt: new Date().toISOString()
      };
      this.models.unshift(newModel);
      this.closeDropdown();
    },
    
    deployModel(model) {
      this.selectedModel = model;
      this.deploymentConfig.modelName = model.name.toLowerCase().replace(/\s+/g, '-');
      this.showDeployModal = true;
      this.closeDropdown();
    },
    
    testModel(model) {
      this.selectedModel = model;
      this.testInput = '';
      this.testResult = null;
      this.showTestModal = true;
      this.closeDropdown();
    },
    
    async deployModelNow() {
      try {
        // Simulate deployment process
        const deploymentData = {
          modelId: this.selectedModel.id,
          modelName: this.deploymentConfig.modelName,
          type: this.deploymentConfig.type,
          config: { ...this.deploymentConfig }
        };
        
        console.log('Deploying model:', deploymentData);
        
        // In a real app, this would call your backend API
        // await this.$http.post('/api/models/deploy', deploymentData);
        
        // Simulate deployment success
        alert(`Model "${this.selectedModel.name}" deployed successfully as "${this.deploymentConfig.modelName}"!`);
        
        this.closeDeployModal();
      } catch (error) {
        console.error('Deployment failed:', error);
        alert('Deployment failed. Please check your configuration.');
      }
    },
    
    async runTest() {
      if (!this.testInput.trim()) return;
      
      this.isTesting = true;
      this.testResult = null;
      
      try {
        // Simulate API call to test the model
        const testData = {
          modelId: this.selectedModel.id,
          input: this.testInput,
          config: { ...this.testConfig }
        };
        
        console.log('Testing model:', testData);
        
        // Simulate API response
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        this.testResult = {
          output: this.generateTestResponse(this.testInput, this.selectedModel.type),
          responseTime: Math.floor(Math.random() * 1000) + 500,
          tokens: Math.floor(Math.random() * 50) + 20
        };
        
      } catch (error) {
        console.error('Test failed:', error);
        alert('Test failed. Please check your model deployment.');
      } finally {
        this.isTesting = false;
      }
    },
    
    generateTestResponse(input, modelType) {
      const responses = {
        'Image': `Based on the image analysis, I can identify several key features and patterns. The image appears to contain ${input.toLowerCase().includes('cat') ? 'feline' : 'various'} elements with high confidence scores.`,
        'Text': `Analysis of the text "${input.substring(0, 50)}..." shows sentiment patterns and linguistic features. The content appears to be ${input.length > 100 ? 'comprehensive' : 'concise'} with notable characteristics.`,
        'NLP': `Natural language processing analysis reveals semantic structures, entity relationships, and contextual understanding. The text demonstrates ${input.includes('?') ? 'interrogative' : 'declarative'} patterns.`,
        'Audio': `Audio analysis indicates ${input.toLowerCase().includes('music') ? 'musical' : 'speech'} content with clear frequency patterns and temporal characteristics.`,
        'Video': `Video content analysis shows ${input.toLowerCase().includes('motion') ? 'dynamic' : 'static'} visual elements with temporal consistency and spatial relationships.`
      };
      
      return responses[modelType] || `Model processed the input "${input.substring(0, 30)}..." successfully with appropriate analysis and insights.`;
    },
    
    closeDeployModal() {
      this.showDeployModal = false;
      this.selectedModel = null;
      this.deploymentConfig = {
        type: 'local',
        modelName: '',
        port: 11434,
        endpoint: '',
        apiKey: '',
        maxTokens: 2048,
        temperature: 0.7,
        contextWindow: 4096
      };
    },
    
    closeTestModal() {
      this.showTestModal = false;
      this.selectedModel = null;
      this.testInput = '';
      this.testResult = null;
      this.isTesting = false;
    },
    
    deleteModel(id) {
      this.modelToDelete = this.models.find(m => m.id === id);
      this.showDeleteModal = true;
      this.closeDropdown();
    },
    
    confirmDelete() {
      if (this.modelToDelete) {
        this.models = this.models.filter(m => m.id !== this.modelToDelete.id);
        this.showDeleteModal = false;
        this.modelToDelete = null;
      }
    },
    
    closeModal() {
      this.showCreateModelModal = false;
      this.editingModel = null;
      this.modelForm = {
        name: '',
        type: 'Text Classification',
        description: '',
        tags: ''
      };
    },
    
    saveModel() {
      if (!this.modelForm.name.trim()) return;
      
      if (this.editingModel) {
        // Update existing model
        const index = this.models.findIndex(m => m.id === this.editingModel.id);
        if (index !== -1) {
          this.models[index] = {
            ...this.models[index],
            name: this.modelForm.name,
            type: this.modelForm.type,
            description: this.modelForm.description,
            tags: this.modelForm.tags.split(',').map(tag => tag.trim()).filter(Boolean),
            updatedAt: new Date().toISOString()
          };
        }
      } else {
        // Create new model
        const newModel = {
          id: Math.max(0, ...this.models.map(m => m.id)) + 1,
          name: this.modelForm.name,
          type: this.modelForm.type,
          description: this.modelForm.description,
          accuracy: 0,
          trainingTime: '0m',
          datasetSize: '0',
          tags: this.modelForm.tags.split(',').map(tag => tag.trim()).filter(Boolean),
          isFavorite: false,
          updatedAt: new Date().toISOString()
        };
        this.models.unshift(newModel);
      }
      
      this.closeModal();
    },
    
    // Close dropdown when clicking outside
    handleClickOutside(event) {
      if (!event.target.closest('.dropdown')) {
        this.closeDropdown();
      }
    },
    
    async fetchLocalModels() {
      this.isLoadingModels = true;
      try {
        // Fetch models from our backend API
        const response = await fetch('http://localhost:5000/api/models');
        const data = await response.json();
        
        if (data.success) {
          // Transform backend models to our format
          this.models = data.models.map((model, index) => ({
            id: index + 1,
            name: model.name,
            type: this.getModelType(model.name),
            description: this.getModelDescription(model.name),
            accuracy: this.getModelAccuracy(model.name),
            trainingTime: this.formatModelSize(model.size),
            datasetSize: this.getModelSize(model.size),
              updatedAt: this.parseModelDate(model.modified),
            tags: this.getModelTags(model.name),
            isFavorite: this.isFavoriteModel(model.name),
            capabilities: model.capabilities || [],
            ollamaModel: model // Keep original backend data
          }));
        } else {
          console.error('Failed to fetch models:', data.error);
          this.models = [];
        }
        
        console.log('Loaded local models:', this.models);
        console.log('Models loaded successfully:', this.models.length);
      } catch (error) {
        console.error('Failed to fetch local models:', error);
        console.error('Error details:', error.message);
        // Don't fallback to sample models, keep empty array
        this.models = [];
      } finally {
        this.isLoadingModels = false;
      }
    },
    
    getModelType(name) {
      const typeMap = {
        'agimat': 'NLP',
        'claude': 'NLP', 
        'llava': 'Image',
        'qwen2.5-coder': 'Code',
        'codellama': 'Code',
        'llama3.1': 'NLP',
        'hf.co/reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12b': 'NLP'
      };
      
      for (const [key, type] of Object.entries(typeMap)) {
        if (name.toLowerCase().includes(key)) {
          return type;
        }
      }
      return 'NLP';
    },
    
    getModelDescription(name) {
      const descriptions = {
        'agimat': 'Advanced AI assistant specialized in debugging and code analysis',
        'claude': 'Claude 3.7 Sonnet Reasoning - Advanced reasoning capabilities',
        'llava': 'Large Language and Vision Assistant for multimodal tasks',
        'qwen2.5-coder': 'Qwen2.5 Coder - Specialized for code generation and analysis',
        'codellama': 'Code Llama - Specialized for code completion and generation',
        'llama3.1': 'Llama 3.1 - General purpose language model'
      };
      
      for (const [key, desc] of Object.entries(descriptions)) {
        if (name.toLowerCase().includes(key)) {
          return desc;
        }
      }
      return 'Local AI model';
    },
    
    getModelAccuracy(name) {
      // Simulate accuracy based on model type
      const baseAccuracy = {
        'agimat': 95.2,
        'claude': 94.8,
        'llava': 89.3,
        'qwen2.5-coder': 92.1,
        'codellama': 91.7,
        'llama3.1': 88.9
      };
      
      for (const [key, acc] of Object.entries(baseAccuracy)) {
        if (name.toLowerCase().includes(key)) {
          return acc;
        }
      }
      return 85.0;
    },
    
    formatModelSize(size) {
      if (!size) return 'Unknown';
      const gb = size / (1024 * 1024 * 1024);
      return `${gb.toFixed(1)} GB`;
    },
    
    getModelSize(size) {
      if (!size) return 'Unknown';
      const gb = size / (1024 * 1024 * 1024);
      return `${gb.toFixed(1)}GB`;
    },
    
    getModelTags(name) {
      const tagMap = {
        'agimat': ['Debugging', 'Code Analysis', 'Assistant'],
        'claude': ['Reasoning', 'Advanced', 'Sonnet'],
        'llava': ['Vision', 'Multimodal', 'Image'],
        'qwen2.5-coder': ['Code', 'Generation', 'Qwen'],
        'codellama': ['Code', 'Completion', 'Llama'],
        'llama3.1': ['General', 'Language', 'Llama'],
        'hf.co/reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12b': ['Reasoning', 'Advanced', 'Sonnet', 'Gemma']
      };
      
      for (const [key, tags] of Object.entries(tagMap)) {
        if (name.toLowerCase().includes(key)) {
          return tags;
        }
      }
      return ['Local', 'AI'];
    },
    
    isFavoriteModel(name) {
      // Mark Agimat as favorite by default
      return name.toLowerCase().includes('agimat');
    },
    
    parseModelDate(dateString) {
      // Handle different date formats from backend
      if (!dateString) return new Date().toISOString();
      
      // If it's already a valid date string, use it
      const date = new Date(dateString);
      if (!isNaN(date.getTime())) {
        return date.toISOString();
      }
      
      // If it's a relative time string like "30 hours ago", calculate approximate date
      const now = new Date();
      if (dateString.includes('hours ago')) {
        const hours = parseInt(dateString.match(/\d+/)[0]);
        const pastDate = new Date(now.getTime() - (hours * 60 * 60 * 1000));
        return pastDate.toISOString();
      } else if (dateString.includes('days ago')) {
        const days = parseInt(dateString.match(/\d+/)[0]);
        const pastDate = new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
        return pastDate.toISOString();
      }
      
      // Default to current time if we can't parse it
      return now.toISOString();
    },
    
    loadSampleModels() {
      // Fallback sample models if Ollama is not available
      this.models = [
        {
          id: 1,
          name: 'agimat:latest',
          type: 'NLP',
          description: 'Advanced AI assistant specialized in debugging and code analysis',
          accuracy: 95.2,
          trainingTime: '12 GB',
          datasetSize: '12GB',
          updatedAt: new Date().toISOString(),
          tags: ['Debugging', 'Code Analysis', 'Assistant'],
          isFavorite: true
        },
        {
          id: 2,
          name: 'claude-3.7-sonnet-reasoning-gemma3-12B:Q8_0',
          type: 'NLP',
          description: 'Claude 3.7 Sonnet Reasoning - Advanced reasoning capabilities',
          accuracy: 94.8,
          trainingTime: '12 GB',
          datasetSize: '12GB',
          updatedAt: new Date().toISOString(),
          tags: ['Reasoning', 'Advanced', 'Sonnet'],
          isFavorite: false
        }
      ];
    }
  },
  
  async mounted() {
    document.addEventListener('click', this.handleClickOutside);
    await this.fetchLocalModels();
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
.models-container {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.8rem;
  color: var(--text-color);
}

.page-header p {
  margin: 0;
  color: var(--secondary);
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-color);
}

.models-actions {
  margin-bottom: 2rem;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.neumorphic-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}
  .search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
  }
  
.search-box input {
    width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: none;
  border-radius: 8px;
  background: var(--card-bg);
  box-shadow: inset 3px 3px 6px var(--shadow-dark), 
              inset -3px -3px 6px var(--shadow-light);
  color: var(--text-color);
}

.search-box .material-icons-round {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary);
  font-size: 1.25rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.model-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.model-card:hover {
  transform: translateY(-3px);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.model-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.model-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.model-status.image { background: rgba(66, 135, 245, 0.1); color: #4287f5; }
.model-status.text { background: rgba(40, 167, 69, 0.1); color: #28a745; }
.model-status.audio { background: rgba(111, 66, 193, 0.1); color: #6f42c1; }
.model-status.video { background: rgba(220, 53, 69, 0.1); color: #dc3545; }
.model-status.nlp { background: rgba(255, 193, 7, 0.1); color: #ffc107; }

.model-details {
  margin-bottom: 1rem;
}

.model-details p {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.9rem;
}

.model-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--secondary);
}

.model-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg);
  border: none;
  color: var(--secondary);
  cursor: pointer;
  box-shadow: 3px 3px 6px var(--shadow-dark), 
              -3px -3px 6px var(--shadow-light);
  transition: all 0.2s ease;
}

.btn-icon:hover {
  color: var(--primary);
  transform: translateY(-2px);
}

/* Button Styles */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--secondary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.btn-danger {
  background: #e74a3b;
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-danger:hover {
  background: #d52a1a;
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(3px);
}

.modal {
  background: var(--card-bg);
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
    flex-direction: column;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-color);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex-grow: 1;
}
.model-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.model-card:hover {
  transform: translateY(-3px);
}
.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 0.95rem;
  background: var(--card-bg);
  color: var(--text-color);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(78, 115, 223, 0.2);
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: var(--secondary);
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
  margin: 2rem 0;
}

.loading-spinner {
  margin-bottom: 1rem;
}

.loading-spinner .material-icons-round {
  font-size: 3rem;
  color: var(--primary);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin: 0;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem 1rem;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
}

.empty-state .material-icons-round {
  font-size: 3rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

/* Job Details Section */
.job-details-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius);
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.job-details-section h4 {
  margin: 0 0 0.75rem 0;
  color: var(--primary);
  font-size: 1rem;
}

.job-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metadata-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.metadata-row:last-child {
  margin-bottom: 0;
}

.metadata-label {
  font-weight: 500;
  color: var(--text-color);
  min-width: 100px;
  margin-right: 0.5rem;
}

.metadata-value {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.model-file {
  font-family: 'Courier New', monospace;
  background: rgba(78, 115, 223, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  color: var(--primary);
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .action-buttons {
    width: 100%;
  }
  
  .action-buttons select,
  .action-buttons .btn {
    width: 100%;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
}
</style>
