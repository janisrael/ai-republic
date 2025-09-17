<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>AI Models</h1>
      <p>Manage your machine learning models and their configurations</p>
    </div>

    <!-- Model Actions -->
    <div class="dashboard-actions mb-4">
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
          <span>{{ isLoadingModels ? 'Loading...' : 'Refresh Models' }}</span>
        </button>
        <button class="btn btn-primary" @click="showCreateModelModal = true">
          <span class="material-icons-round">add</span>
          <span>New Model</span>
        </button>
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

    <!-- Models Grid -->
    <div v-else class="models-grid">
      <div 
        v-for="model in filteredModels" 
        :key="model.id" 
        class="model-card neumorphic-card"
      >
        <div class="model-card-header">
          <div class="model-type" :class="model.type.toLowerCase()">
            {{ model.type }}
          </div>
          <div class="model-actions">
            <button 
              class="btn-icon" 
              :class="{ 'active': model.isFavorite }"
              @click.stop="toggleModelFavorite(model)"
              aria-label="Toggle favorite"
            >
              <span class="material-icons-round">{{ model.isFavorite ? 'star' : 'star_border' }}</span>
            </button>
            <div class="dropdown">
              <button 
                class="btn-icon" 
                @click.stop="toggleDropdown($event, model.id)"
                aria-label="More options"
              >
                <span class="material-icons-round">more_vert</span>
              </button>
              <div class="dropdown-menu" :class="{ 'show': activeDropdown === model.id }">
                <button class="dropdown-item" @click="viewModelDetails(model)">
                  <span class="material-icons-round">visibility</span>
                  <span>View Details</span>
                </button>
                <button class="dropdown-item" @click="editModel(model)">
                  <span class="material-icons-round">edit</span>
                  <span>Edit</span>
                </button>
                <button class="dropdown-item" @click="duplicateModel(model)">
                  <span class="material-icons-round">content_copy</span>
                  <span>Duplicate</span>
                </button>
                <button class="dropdown-item" @click="deployModel(model)">
                  <span class="material-icons-round">rocket_launch</span>
                  <span>Deploy</span>
                </button>
                <button class="dropdown-item" @click="testModel(model)">
                  <span class="material-icons-round">play_arrow</span>
                  <span>Test Model</span>
                </button>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item text-danger" @click="deleteModel(model.id)">
                  <span class="material-icons-round">delete</span>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="model-card-body" @click="viewModelDetails(model)">
          <div class="model-info">
            <div class="model-icon" :class="model.type.toLowerCase()">
              <span class="material-icons-round">{{ getModelIcon(model.type) }}</span>
            </div>
            <div class="model-details">
              <h3>{{ model.name }}</h3>
              <p>{{ model.description || 'No description provided' }}</p>
            </div>
          </div>
          
          <div class="model-stats">
            <div class="stat-item">
              <div class="stat-value">{{ model.accuracy }}%</div>
              <div class="stat-label">Accuracy</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ model.trainingTime }}</div>
              <div class="stat-label">Training</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ model.datasetSize }}</div>
              <div class="stat-label">Samples</div>
            </div>
          </div>
          
          <div class="model-footer">
            <div class="model-tags">
              <span 
                v-for="(tag, index) in model.tags.slice(0, 3)" 
                :key="index" 
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
            <div class="model-updated">
              <span class="material-icons-round">schedule</span>
              <span>{{ formatTimeAgo(model.updatedAt) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div class="col-12" v-if="filteredModels.length === 0">
        <div class="text-center py-5 bg-light rounded-3">
          <div class="mb-3">
            <i class="material-icons-round display-4 text-muted">inventory_2</i>
          </div>
          <h4 class="mb-2">No models found</h4>
          <p class="text-muted mb-4">Get started by creating your first AI model</p>
          <button class="btn btn-primary" @click="showCreateModelModal = true">
            <i class="material-icons-round me-1">add</i>
            Create Model
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
      models: [
        {
          id: 1,
          name: 'Image Classifier V1',
          type: 'Image',
          description: 'ResNet50 model for image classification',
          accuracy: 92.5,
          trainingTime: '2h 15m',
          datasetSize: '50K',
          updatedAt: '2023-04-15T14:30:00Z',
          tags: ['CNN', 'Computer Vision', 'ResNet'],
          isFavorite: true
        },
        {
          id: 2,
          name: 'Sentiment Analysis',
          type: 'NLP',
          description: 'BERT model for sentiment analysis',
          accuracy: 88.2,
          trainingTime: '4h 30m',
          datasetSize: '100K',
          updatedAt: '2023-04-10T09:15:00Z',
          tags: ['NLP', 'BERT', 'Sentiment'],
          isFavorite: false
        }
      ],
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
      models: [],
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
          model.tags.some(tag => tag.toLowerCase().includes(query))
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
        // Fetch models from Ollama API
        const response = await fetch('http://localhost:11434/api/tags');
        const data = await response.json();
        
        // Transform Ollama models to our format
        this.models = data.models.map((model, index) => ({
          id: index + 1,
          name: model.name,
          type: this.getModelType(model.name),
          description: this.getModelDescription(model.name),
          accuracy: this.getModelAccuracy(model.name),
          trainingTime: this.formatModelSize(model.size),
          datasetSize: this.getModelSize(model.size),
          updatedAt: new Date(model.modified_at).toISOString(),
          tags: this.getModelTags(model.name),
          isFavorite: this.isFavoriteModel(model.name),
          ollamaModel: model // Keep original Ollama data
        }));
        
        console.log('Loaded local models:', this.models);
      } catch (error) {
        console.error('Failed to fetch local models:', error);
        // Fallback to sample models if Ollama is not running
        this.loadSampleModels();
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
        'llama3.1': 'NLP'
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
        'llama3.1': ['General', 'Language', 'Llama']
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
/* Neumorphic Card */
.neumorphic-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.neumorphic-card:hover {
  transform: translateY(-2px);
  box-shadow: 10px 10px 20px var(--shadow-dark), 
              -10px -10px 20px var(--shadow-light);
}

/* Dashboard Layout */
.dashboard-container {
  padding: 2rem;
  /* max-width: 1400px; */
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
  margin: 0;
}

/* Dashboard Actions */
.dashboard-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
  flex-wrap: wrap;
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
  color: var(--text-primary);
}

.search-box .material-icons-round {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1.25rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Models Grid */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.model-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.model-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.model-type {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-type.image { background: rgba(66, 135, 245, 0.1); color: #4287f5; }
.model-type.text { background: rgba(40, 167, 69, 0.1); color: #28a745; }
.model-type.audio { background: rgba(111, 66, 193, 0.1); color: #6f42c1; }
.model-type.video { background: rgba(220, 53, 69, 0.1); color: #dc3545; }
.model-type.nlp { background: rgba(255, 193, 7, 0.1); color: #ffc107; }

.model-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--card-bg);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 3px 3px 6px var(--shadow-dark), 
              -3px -3px 6px var(--shadow-light);
}

.btn-icon:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.btn-icon.active {
  color: #ffc107;
  box-shadow: inset 2px 2px 4px var(--shadow-dark), 
              inset -2px -2px 4px var(--shadow-light);
}

/* Dropdown Menu */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1000;
  min-width: 200px;
  padding: 0.5rem 0;
  margin: 0.125rem 0 0;
  background: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.2s ease;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.dropdown-item .material-icons-round {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.dropdown-divider {
  height: 1px;
  margin: 0.5rem 0;
  background: var(--border-color);
  border: none;
}

/* Model Card Body */
.model-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.model-info {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.model-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.5rem;
  color: white;
}

.model-icon.image { background: #4287f5; }
.model-icon.text { background: #28a745; }
.model-icon.audio { background: #6f42c1; }
.model-icon.video { background: #dc3545; }
.model-icon.nlp { background: #ffc107; }

.model-details h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}

.model-details p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
  text-overflow: ellipsis;
  max-height: 2.8em;
}

/* Model Stats */
.model-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: inset 3px 3px 6px var(--shadow-dark), 
              inset -3px -3px 6px var(--shadow-light);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Model Footer */
.model-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  white-space: nowrap;
}

.model-updated {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.model-updated .material-icons-round {
  font-size: 1rem;
  margin-right: 0.25rem;
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

/* Responsive Adjustments */
@media (max-width: 768px) {
  .dashboard-actions {
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
}

/* Dark Mode Variables */
:root {
  --card-bg: #f0f2f5;
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --border-color: #e2e8f0;
  --shadow-dark: #c9cdd3;
  --shadow-light: #ffffff;
  --hover-bg: #e9ecef;
  --primary: #4f46e5;
  --tag-bg: #e2e8f0;
}

[data-theme="dark"] {
  --card-bg: #2d3748;
  --text-primary: #f7fafc;
  --text-secondary: #a0aec0;
  --border-color: #4a5568;
  --shadow-dark: #1a202c;
  --shadow-light: #4a5568;
  --hover-bg: #4a5568;
  --tag-bg: #4a5568;
}
/* Base Styles */
:root {
  --model-card-bg: var(--card-bg);
  --model-card-shadow: var(--neumorph-shadow);
  --model-card-shadow-hover: var(--neumorph-shadow-hover);
  --model-card-padding: 1.5rem;
  --model-border-radius: var(--border-radius-lg);
  --model-transition: var(--transition);
}

/* Model Card Styles */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.model-card {
  position: relative;
  border-radius: var(--model-border-radius);
  transition: var(--model-transition);
  background: var(--model-card-bg);
  box-shadow: var(--model-card-shadow);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.model-card:hover {
  box-shadow: var(--model-card-shadow-hover);
  transform: translateY(-2px);
}

.model-card-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.model-card.is-favorite {
  border: 1px solid var(--primary-light);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.1), var(--model-card-shadow);
}

/* Header */
.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem 0.5rem;
  margin-bottom: 0.5rem;
}

.model-type {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  background: var(--light);
  color: var(--dark);
}

.model-type.image {
  background: #e3f2fd;
  color: #1565c0;
}

.model-type.text {
  background: #e8f5e9;
  color: #2e7d32;
}

.model-type.audio {
  background: #f3e5f5;
  color: #7b1fa2;
}

.model-type.video {
  background: #ffebee;
  color: #c62828;
}

.model-actions {
  display: flex;
  gap: 0.25rem;
}

/* Body */
.model-body {
  padding: 0 1.5rem 1rem;
  cursor: pointer;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.model-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  background: var(--light);
  color: var(--primary);
  font-size: 1.75rem;
  box-shadow: var(--neumorph-shadow-inset);
}

.model-avatar .material-icons-round {
  font-size: 2rem;
}

.model-avatar.image { background: #e3f2fd; color: #1565c0; }
.model-avatar.text { background: #e8f5e9; color: #2e7d32; }
.model-avatar.audio { background: #f3e5f5; color: #7b1fa2; }
.model-avatar.video { background: #ffebee; color: #c62828; }

.model-body h3 {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  text-align: center;
  line-height: 1.3;
}

.model-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 1.25rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 4.05em;
}

.model-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: auto;
}

.stat {
  text-align: center;
  padding: 0.75rem 0.5rem;
  background: var(--light);
  border-radius: var(--border-radius);
  transition: var(--model-transition);
}

.stat:hover {
  background: var(--light-hover);
  transform: translateY(-2px);
}

.stat-value {
  display: block;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Footer */
.model-footer {
  padding: 0.75rem 1.5rem 1.25rem;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag {
  font-size: 0.7rem;
  background: var(--light);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  line-height: 1.4;
}

.model-updated {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Buttons & Dropdown */
.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--light);
  color: var(--text-secondary);
  border: none;
  cursor: pointer;
  transition: var(--model-transition);
  position: relative;
  z-index: 1;
}

.btn-icon:hover {
  background: var(--light-hover);
  color: var(--primary);
  box-shadow: var(--neumorph-shadow-sm);
}

.btn-icon.active {
  background: var(--primary-light);
  color: var(--primary);
}

.favorite-btn.active {
  color: #ffc107;
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  padding: 0.5rem 0;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.2s ease;
  border: 1px solid var(--border-color);
}

.dropdown.active .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(5px);
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.5rem 1rem;
  text-align: left;
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: var(--light);
  color: var(--primary);
}

.dropdown-item .material-icons-round {
  font-size: 1.1rem;
  margin-right: 0.75rem;
  opacity: 0.8;
}

.dropdown-item.danger {
  color: #d32f2f;
}

.dropdown-item.danger:hover {
  background: #ffebee;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  background: var(--card-bg);
  border-radius: var(--model-border-radius);
  box-shadow: var(--model-card-shadow);
  margin: 1rem 0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.empty-state h3 {
  margin: 0 0 0.75rem;
  color: var(--text-color);
  font-size: 1.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .models-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  .model-card {
    margin-bottom: 1rem;
  }
  
  .filters-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: 100%;
  }
}

/* Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.model-card {
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
}

.model-card:nth-child(1) { animation-delay: 0.1s; }
.model-card:nth-child(2) { animation-delay: 0.15s; }
.model-card:nth-child(3) { animation-delay: 0.2s; }
.model-card:nth-child(4) { animation-delay: 0.25s; }
.model-card:nth-child(5) { animation-delay: 0.3s; }
.model-card:nth-child(6) { animation-delay: 0.35s; }
.models-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--neumorph-shadow);
  transition: var(--transition);
}

.page-header:hover {
  box-shadow: var(--neumorph-shadow-hover);
}

.header-content h1 {
  font-size: 1.8rem;
  margin: 0 0 0.5rem;
  color: var(--text-color);
  font-weight: 600;
  letter-spacing: -0.5px;
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  opacity: 0.9;
}

.filters-container {
  display: flex;
  gap: 1rem;
  margin: 0 0 2rem;
  flex-wrap: wrap;
  align-items: center;
  background: var(--card-bg);
  padding: 1.25rem 1.5rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--neumorph-shadow);
  transition: var(--transition);
}

.filters-container:hover {
  box-shadow: var(--neumorph-shadow-hover);
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.search-box input {
  padding-left: 2.5rem;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary);
  pointer-events: none;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
}

.filter-group label {
  white-space: nowrap;
  color: var(--secondary);
  font-size: 0.9rem;
}

.filter-group select {
  min-width: 150px;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.model-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.model-card:hover {
  transform: translateY(-5px);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  position: relative;
}

.model-type {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05);
}

.model-type.text {
  background: rgba(78, 115, 223, 0.1);
  color: #4e73df;
}

.model-type.image {
  background: rgba(28, 200, 138, 0.1);
  color: #1cc88a;
}

.model-type.nlp {
  background: rgba(230, 74, 25, 0.1);
  color: #e64a19;
}

.model-actions {
  display: flex;
  gap: 0.25rem;
  position: relative;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--secondary);
  transition: all 0.2s ease;
  font-size: 1.1rem;
  padding: 0;
}

.btn-icon:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-color);
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 180px;
  z-index: 1000;
  overflow: hidden;
  margin-top: 0.5rem;
}

.dropdown-menu button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.6rem 1rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  color: var(--text-color);
  transition: background 0.2s ease;
}

.dropdown-menu button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.dropdown-menu button i {
  font-size: 1rem;
  opacity: 0.8;
}

.dropdown-menu button.danger {
  color: #e74a3b;
}

.model-body {
  flex: 1;
  text-align: center;
  padding: 0.5rem 0;
}

.model-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.model-body h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  color: var(--text-color);
}

.model-description {
  color: var(--secondary);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-stats {
  display: flex;
  justify-content: space-around;
  margin: 1.5rem 0;
  padding: 1rem 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-color);
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: var(--secondary);
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-footer {
  margin-top: auto;
  padding-top: 1rem;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag {
  background: rgba(0, 0, 0, 0.05);
  color: var(--secondary);
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.model-updated {
  font-size: 0.75rem;
  color: var(--secondary);
  text-align: right;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  margin: 1rem 0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--text-color);
}

.empty-state p {
  margin: 0 0 1.5rem;
  color: var(--secondary);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

/* Modal Styles */
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

.modal-content {
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-color);
}

.modal-body {
  padding: 1rem 0;
}

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
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: var(--card-bg);
  color: var(--text-color);
  box-shadow: inset 2px 2px 5px var(--shadow-dark), 
              inset -2px -2px 5px var(--shadow-light);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.25);
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 1.5rem;
}

.btn-danger {
  background: #e74a3b;
  color: white;
}

.btn-danger:hover {
  background: #d52a1a;
}

/* Responsive Styles */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-group select {
    width: 100%;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    margin: 1rem;
  }
}

/* Deployment Modal Styles */
.deployment-options h3,
.deployment-settings h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.deployment-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.deployment-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
}

.deployment-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.deployment-card.active {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

.deployment-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.deployment-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.deployment-card p {
  margin: 0 0 1rem 0;
  color: var(--secondary);
  font-size: 0.9rem;
}

.deployment-details {
  margin-top: auto;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

/* Test Modal Styles */
.test-modal {
  max-width: 800px;
}

.test-input {
  margin-bottom: 2rem;
}

.test-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.range-value {
  display: inline-block;
  margin-left: 0.5rem;
  font-weight: 600;
  color: var(--primary);
}

.test-result {
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.test-result h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.result-content {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: var(--shadow-sm);
}

.result-text {
  color: var(--text-color);
  line-height: 1.6;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
  border-left: 4px solid var(--primary);
}

.result-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--secondary);
}

.meta-item .emoji {
  font-size: 1rem;
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

.btn-primary:hover:not(:disabled) {
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

/* Responsive adjustments for modals */
@media (max-width: 768px) {
  .deployment-cards {
    grid-template-columns: 1fr;
  }
  
  .settings-grid,
  .test-options {
    grid-template-columns: 1fr;
  }
  
  .result-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
