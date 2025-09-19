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
        <select class="form-control" v-model="selectedCapability">
          <option value="">All Capabilities</option>
          <option v-for="capability in availableCapabilities" :key="capability" :value="capability">
            {{ capability }}
          </option>
        </select>
        <select class="form-control" v-model="sortBy">
          <option value="ranking">Ranking</option>
          <option value="name">Name (A-Z)</option>
          <option value="size">Size</option>
          <option value="parameters">Parameters</option>
          <option value="context">Context Length</option>
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

      <!-- Model Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">smart_toy</span>
          </div>
          <div class="card-content">
            <h3>{{ models.length }}</h3>
            <p>Total Models</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">trending_up</span>
          </div>
          <div class="card-content">
            <h3>{{ topModel?.name || 'N/A' }}</h3>
            <p>Top Model</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">memory</span>
          </div>
          <div class="card-content">
            <h3>{{ averageParameters }}</h3>
            <p>Avg Parameters</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">speed</span>
          </div>
          <div class="card-content">
            <h3>{{ averageContextLength }}</h3>
            <p>Avg Context</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">category</span>
          </div>
          <div class="card-content">
            <h3>{{ uniqueArchitectures }}</h3>
            <p>Architectures</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">code</span>
          </div>
          <div class="card-content">
            <h3>{{ codingModels }}</h3>
            <p>Coding Models</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <span class="material-icons-round">visibility</span>
          </div>
          <div class="card-content">
            <h3>{{ visionModels }}</h3>
            <p>Vision Models</p>
          </div>
        </div>
      </div>

      <!-- Model Rankings (Main Display) -->
      <div class="rankings-section">
        <div class="section-header">
          <h3>
            <span class="material-icons-round">emoji_events</span>
            AI Models
          </h3>
          <p>{{ filteredAndSortedModels.length }} models available</p>
        </div>
        
        <div class="rankings-grid">
          <div 
            v-for="(model, index) in filteredAndSortedModels" 
            :key="model.name"
            class="ranking-card clickable-card"
            :class="{ 'top-rank': index === 0 }"
            @click="viewModelDetails(model)"
          >
            <div class="rank-number">
              <span class="rank-badge" :class="getRankClass(index)">{{ index + 1 }}</span>
              <button class="chat-test-btn" @click.stop="openChatModal(model)" title="Test Model">
                <span class="material-icons-round">chat</span>
              </button>
            </div>
            <div class="model-info">
              <h4>{{ model.name }}</h4>
              <div class="model-stats">
                <span class="stat">
                  <span class="material-icons-round">memory</span>
                  {{ model.details?.parameters || 'N/A' }}
                </span>
                <span class="stat">
                  <span class="material-icons-round">speed</span>
                  {{ formatNumber(model.details?.context_length) }}
                </span>
                <span class="stat">
                  <span class="material-icons-round">tune</span>
                  {{ model.details?.quantization || 'N/A' }}
                </span>
              </div>
              <div class="model-capabilities">
                <span 
                  v-for="capability in model.details?.capabilities?.slice(0, 4)" 
                  :key="capability"
                  class="capability-tag"
                >
                  {{ capability }}
                </span>
                <span v-if="model.details?.capabilities?.length > 4" class="capability-more">
                  +{{ model.details.capabilities.length - 4 }} more
                </span>
              </div>
              <div class="model-params" v-if="model.details?.temperature || model.details?.top_p">
                <span class="param">
                  <span class="material-icons-round">thermostat</span>
                  T: {{ model.details.temperature }}
                </span>
                <span class="param">
                  <span class="material-icons-round">filter_alt</span>
                  P: {{ model.details.top_p }}
                </span>
              </div>
            </div>
            <div class="rank-score">
              <div class="score">{{ calculateModelScore(model) }}</div>
              <div class="score-label">Score</div>
            </div>
          </div>
        </div>
      </div>

    <!-- Old models-grid section - keeping for reference but not displaying -->
    <div class="models-grid" style="display: none;">
      <div 
        v-for="model in filteredAndSortedModels" 
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
              <span>{{ model.details?.parameters || 'Unknown' }}</span>
              <span>{{ model.details?.context_length || 'Unknown' }} ctx</span>
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
      <div v-if="filteredAndSortedModels.length === 0" class="empty-state">
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

    <!-- Model Details Modal -->
    <div v-if="showModelDetailsModal" class="modal-overlay" @click.self="showModelDetailsModal = false">
      <div class="modal-content neumorphic-card model-details-modal">
        <div class="modal-header">
          <h2>Model Details: {{ selectedModelForDetails?.name }}</h2>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="toggleEditMode" v-if="!isEditingModel">
              <span class="material-icons-round">edit</span>
              Edit
            </button>
            <button class="btn btn-primary" @click="saveModelChanges" v-if="isEditingModel">
              <span class="material-icons-round">save</span>
              Save
            </button>
            <button class="btn btn-secondary" @click="cancelEditMode" v-if="isEditingModel">
              <span class="material-icons-round">cancel</span>
              Cancel
            </button>
            <button class="btn-icon" @click="showModelDetailsModal = false">✕</button>
          </div>
        </div>
        
        <div class="modal-body">
          <div v-if="selectedModelForDetails" class="model-details-content">
            <!-- Basic Information -->
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Name:</span>
                  <span class="value">{{ selectedModelForDetails.name }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Type:</span>
                  <span class="value">{{ selectedModelForDetails.type }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Architecture:</span>
                  <span class="value">{{ selectedModelForDetails.details?.architecture || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Parameters:</span>
                  <span class="value">{{ selectedModelForDetails.details?.parameters || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Context Length:</span>
                  <span class="value">{{ selectedModelForDetails.details?.context_length || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Quantization:</span>
                  <span class="value">{{ selectedModelForDetails.details?.quantization || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <!-- Configuration -->
            <div class="detail-section">
              <h4>Configuration</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Temperature:</span>
                  <span class="value">{{ selectedModelForDetails.details?.temperature || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Top P:</span>
                  <span class="value">{{ selectedModelForDetails.details?.top_p || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">License:</span>
                  <span class="value">{{ selectedModelForDetails.details?.license || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Size:</span>
                  <span class="value">{{ selectedModelForDetails.trainingTime || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <!-- Capabilities -->
            <div class="detail-section">
              <h4>Capabilities</h4>
              <div class="capabilities-grid">
                <span 
                  v-for="capability in selectedModelForDetails.details?.capabilities" 
                  :key="capability"
                  class="capability-tag large"
                >
                  {{ capability }}
                </span>
              </div>
            </div>

            <!-- System Prompt -->
            <div v-if="selectedModelForDetails.details?.system_prompt" class="detail-section">
              <h4>System Prompt</h4>
              <div class="system-prompt" v-if="!isEditingModel">
                <p>{{ selectedModelForDetails.details.system_prompt }}</p>
              </div>
              <div v-else class="editable-prompt">
                <textarea 
                  v-model="editableSystemPrompt"
                  class="form-control prompt-textarea"
                  rows="8"
                  placeholder="Enter system prompt..."
                ></textarea>
                <div class="prompt-actions">
                  <button class="btn btn-sm btn-secondary" @click="resetPrompt">
                    <span class="material-icons-round">refresh</span>
                    Reset
                  </button>
                  <span class="char-count">{{ editableSystemPrompt.length }} characters</span>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="detail-section">
              <h4>Description</h4>
              <div v-if="!isEditingModel">
                <p>{{ selectedModelForDetails.description || 'No description provided' }}</p>
              </div>
              <div v-else class="editable-description">
                <textarea 
                  v-model="editableDescription"
                  class="form-control"
                  rows="3"
                  placeholder="Enter model description..."
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModelDetailsModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- Chat Test Modal -->
    <div v-if="showChatModal" class="chat-modal-overlay" @click.self="closeChatModal">
      <div class="chat-modal-content">
        <div class="chat-header">
          <div class="chat-model-info">
            <span class="material-icons-round">smart_toy</span>
            <h3>{{ selectedChatModel?.name }}</h3>
            <span class="model-type">{{ selectedChatModel?.type }}</span>
          </div>
          <button class="btn-icon" @click="closeChatModal">✕</button>
        </div>
        
        <div class="chat-terminal">
          <div class="terminal-header">
            <div class="terminal-controls">
              <span class="control-dot red"></span>
              <span class="control-dot yellow"></span>
              <span class="control-dot green"></span>
            </div>
            <span class="terminal-title">Model Test Terminal</span>
          </div>
          
          <div class="terminal-body" ref="terminalBody">
            <div class="terminal-output">
              <div v-for="(message, index) in chatMessages" :key="index" class="message" :class="message.type">
                <span class="message-prefix">{{ message.prefix }}</span>
                <span class="message-content">{{ message.content }}</span>
              </div>
              <div v-if="isGenerating" class="message generating">
                <span class="message-prefix">{{ selectedChatModel?.name }}:</span>
                <span class="message-content typing-indicator">
                  <span class="typing-dot"></span>
                  <span class="typing-dot"></span>
                  <span class="typing-dot"></span>
                </span>
              </div>
            </div>
          </div>
          
          <div class="terminal-input">
            <div class="input-line">
              <span class="prompt-symbol">$</span>
              <input 
                v-model="chatInput" 
                @keyup.enter="sendMessage"
                :disabled="isGenerating"
                placeholder="Type your message..."
                class="terminal-input-field"
                ref="chatInput"
              />
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
      selectedCapability: '',
      sortBy: 'ranking',
      activeDropdown: null,
      showCreateModelModal: false,
      showDeleteModal: false,
      showDeployModal: false,
      showTestModal: false,
      showModelDetailsModal: false,
      selectedModelForDetails: null,
      isEditingModel: false,
      editableSystemPrompt: '',
      editableDescription: '',
      originalSystemPrompt: '',
      originalDescription: '',
      showChatModal: false,
      selectedChatModel: null,
      chatMessages: [],
      chatInput: '',
      isGenerating: false,
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
      isLoadingModels: false,
      modelDetails: {} // Store detailed model information
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
    
    // Summary Cards Computed Properties
    topModel() {
      const modelsWithDetails = this.modelsWithDetails;
      console.log('Computing topModel from', modelsWithDetails.length, 'models');
      if (modelsWithDetails.length === 0) return null;
      const top = modelsWithDetails.reduce((top, model) => {
        const currentScore = this.calculateModelScore(model);
        const topScore = this.calculateModelScore(top);
        return currentScore > topScore ? model : top;
      });
      console.log('Top model:', top?.name, 'Score:', this.calculateModelScore(top));
      return top;
    },
    
    averageParameters() {
      const modelsWithDetails = this.modelsWithDetails;
      console.log('Computing averageParameters from', modelsWithDetails.length, 'models');
      if (modelsWithDetails.length === 0) return 'N/A';
      const total = modelsWithDetails.reduce((sum, model) => {
        const params = this.parseParameters(model.details?.parameters || '0B');
        console.log(`Model ${model.name}: ${model.details?.parameters} -> ${params}`);
        return sum + params;
      }, 0);
      const avg = total / modelsWithDetails.length;
      const result = avg >= 1 ? `${avg.toFixed(1)}B` : `${(avg * 1000).toFixed(0)}M`;
      console.log('Average parameters:', result);
      return result;
    },
    
    averageContextLength() {
      if (this.modelsWithDetails.length === 0) return 'N/A';
      const total = this.modelsWithDetails.reduce((sum, model) => {
        return sum + (model.details?.context_length || 0);
      }, 0);
      const avg = total / this.modelsWithDetails.length;
      return this.formatNumber(Math.round(avg));
    },
    
    uniqueArchitectures() {
      const architectures = new Set();
      this.modelsWithDetails.forEach(model => {
        if (model.details?.architecture) {
          architectures.add(model.details.architecture);
        }
      });
      return architectures.size;
    },
    
    codingModels() {
      const modelsWithDetails = this.modelsWithDetails;
      const coding = modelsWithDetails.filter(model => {
        // Check both the basic capabilities and detailed capabilities
        const basicCaps = model.capabilities || [];
        const detailedCaps = model.details?.capabilities || [];
        const allCaps = [...basicCaps, ...detailedCaps];
        
        return allCaps.some(cap => 
          cap.toLowerCase().includes('code') || 
          cap.toLowerCase().includes('coding') ||
          cap.toLowerCase().includes('debug')
        );
      });
      console.log('Coding models:', coding.length, coding.map(m => m.name));
      return coding.length;
    },
    
    visionModels() {
      const modelsWithDetails = this.modelsWithDetails;
      const vision = modelsWithDetails.filter(model => {
        // Check both the basic capabilities and detailed capabilities
        const basicCaps = model.capabilities || [];
        const detailedCaps = model.details?.capabilities || [];
        const allCaps = [...basicCaps, ...detailedCaps];
        
        return allCaps.some(cap => 
          cap.toLowerCase().includes('visual') || 
          cap.toLowerCase().includes('vision') ||
          cap.toLowerCase().includes('image')
        );
      });
      console.log('Vision models:', vision.length, vision.map(m => m.name));
      return vision.length;
    },
    
    // Model Rankings
    rankedModels() {
      return [...this.modelsWithDetails].sort((a, b) => {
        const scoreA = this.calculateModelScore(a);
        const scoreB = this.calculateModelScore(b);
        return scoreB - scoreA; // Descending order (highest first)
      });
    },
    
    modelsWithDetails() {
      console.log('Computing modelsWithDetails:', this.models.length, 'models,', Object.keys(this.modelDetails).length, 'details');
      return this.models.map(model => {
        const details = this.modelDetails[model.name] || null;
        console.log(`Model ${model.name} details:`, details);
        return {
          ...model,
          details: details
        };
      });
    },
    availableCapabilities() {
      const capabilities = new Set();
      this.models.forEach(model => {
        if (model.details?.capabilities) {
          model.details.capabilities.forEach(cap => capabilities.add(cap));
        }
      });
      return Array.from(capabilities).sort();
    },
    
    filteredAndSortedModels() {
      if (!this.models || !Array.isArray(this.models)) {
        return [];
      }
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
      
      // Filter by capability
      if (this.selectedCapability) {
        filtered = filtered.filter(model => 
          model.details?.capabilities?.includes(this.selectedCapability)
        );
      }
      
      // Sort models
      return filtered.sort((a, b) => {
        if (this.sortBy === 'ranking') {
          return this.calculateModelScore(b) - this.calculateModelScore(a);
        } else if (this.sortBy === 'name') {
          return a.name.localeCompare(b.name);
        } else if (this.sortBy === 'size') {
          const aSize = this.parseModelSize(a.trainingTime);
          const bSize = this.parseModelSize(b.trainingTime);
          return bSize - aSize;
        } else if (this.sortBy === 'parameters') {
          const aParams = this.parseParameters(a.details?.parameters);
          const bParams = this.parseParameters(b.details?.parameters);
          return bParams - aParams;
        } else if (this.sortBy === 'context') {
          const aCtx = parseInt(a.details?.context_length) || 0;
          const bCtx = parseInt(b.details?.context_length) || 0;
          return bCtx - aCtx;
        }
        return 0;
      });
    }
  },
  methods: {
    // Model Details and Scoring Methods
    async loadModelDetails() {
      console.log('Loading model details for', this.models.length, 'models');
      for (const model of this.models) {
        try {
          console.log(`Loading details for: ${model.name}`);
          const response = await fetch(`http://localhost:5000/api/models/${model.name}/details`);
          const data = await response.json();
          if (data.success) {
            // Use Vue 3 reactivity
            this.modelDetails[model.name] = data.details;
            console.log(`Loaded details for ${model.name}:`, data.details);
          } else {
            console.error(`Failed to load details for ${model.name}:`, data.error);
          }
        } catch (error) {
          console.error(`Failed to load details for ${model.name}:`, error);
        }
      }
      console.log('All model details loaded:', this.modelDetails);
    },
    
    calculateModelScore(model) {
      if (!model.details) {
        console.log(`No details for ${model.name}, score: 0`);
        return 0;
      }
      
      let score = 0;
      
      // Parameter score (0-40 points)
      const params = this.parseParameters(model.details.parameters || '0B');
      const paramScore = Math.min(params * 2, 40);
      score += paramScore;
      
      // Context length score (0-30 points)
      const contextLength = model.details.context_length || 0;
      const contextScore = Math.min(contextLength / 10000, 30);
      score += contextScore;
      
      // Capabilities score (0-20 points)
      const basicCaps = model.capabilities || [];
      const detailedCaps = model.details.capabilities || [];
      const allCaps = [...basicCaps, ...detailedCaps];
      const capScore = Math.min(allCaps.length * 5, 20);
      score += capScore;
      
      // Architecture bonus (0-10 points)
      const architecture = model.details.architecture?.toLowerCase() || '';
      let archScore = 3;
      if (architecture.includes('llama')) archScore = 8;
      else if (architecture.includes('gemma')) archScore = 7;
      else if (architecture.includes('mistral')) archScore = 6;
      else if (architecture.includes('qwen')) archScore = 5;
      score += archScore;
      
      const finalScore = Math.round(score);
      console.log(`Score for ${model.name}: params=${paramScore}, context=${contextScore}, caps=${capScore}, arch=${archScore}, total=${finalScore}`);
      return finalScore;
    },
    
    getRankClass(index) {
      if (index === 0) return 'rank-gold';
      if (index === 1) return 'rank-silver';
      if (index === 2) return 'rank-bronze';
      return 'rank-normal';
    },
    
    parseParameters(paramStr) {
      if (!paramStr) return 0;
      const match = paramStr.match(/(\d+\.?\d*)([BM])/);
      if (match) {
        const value = parseFloat(match[1]);
        const unit = match[2];
        return unit === 'B' ? value : value / 1000;
      }
      return 0;
    },
    
    formatNumber(num) {
      if (!num) return 'N/A';
      return num.toLocaleString();
    },
    
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
      this.selectedModelForDetails = model;
      this.showModelDetailsModal = true;
      this.isEditingModel = false;
      // Initialize editable values
      this.editableSystemPrompt = model.details?.system_prompt || '';
      this.editableDescription = model.description || '';
      this.originalSystemPrompt = model.details?.system_prompt || '';
      this.originalDescription = model.description || '';
      console.log('Viewing model details:', model);
    },
    
    toggleEditMode() {
      this.isEditingModel = true;
    },
    
    cancelEditMode() {
      this.isEditingModel = false;
      // Reset to original values
      this.editableSystemPrompt = this.originalSystemPrompt;
      this.editableDescription = this.originalDescription;
    },
    
    resetPrompt() {
      this.editableSystemPrompt = this.originalSystemPrompt;
    },
    
    async saveModelChanges() {
      try {
        // Show loading state
        const saveButton = document.querySelector('.btn-primary');
        if (saveButton) {
          saveButton.disabled = true;
          saveButton.innerHTML = '<span class="material-icons-round">refresh</span> Saving...';
        }
        
        // Prepare data for API call
        const updateData = {
          system_prompt: this.editableSystemPrompt,
          temperature: this.selectedModelForDetails.details?.temperature,
          top_p: this.selectedModelForDetails.details?.top_p,
          description: this.editableDescription
        };
        
        // Call backend API to update the model
        const response = await fetch(`http://localhost:5000/api/models/${encodeURIComponent(this.selectedModelForDetails.name)}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateData)
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Update the model in the local array
          const modelIndex = this.models.findIndex(m => m.name === this.selectedModelForDetails.name);
          if (modelIndex !== -1) {
            // Update local model data
            this.models[modelIndex].description = this.editableDescription;
            if (this.models[modelIndex].details) {
              this.models[modelIndex].details.system_prompt = this.editableSystemPrompt;
            }
            
            // Update the selected model for display
            this.selectedModelForDetails.description = this.editableDescription;
            if (this.selectedModelForDetails.details) {
              this.selectedModelForDetails.details.system_prompt = this.editableSystemPrompt;
            }
            
            // Update original values
            this.originalSystemPrompt = this.editableSystemPrompt;
            this.originalDescription = this.editableDescription;
            
            this.isEditingModel = false;
            
            // Show success message
            console.log('Model changes saved successfully:', result.message);
            
            // Refresh the models list to get updated data
            await this.fetchLocalModels();
            
          } else {
            console.error('Model not found in local array');
          }
        } else {
          throw new Error(result.error || 'Failed to save model changes');
        }
        
      } catch (error) {
        console.error('Error saving model changes:', error);
        alert(`Failed to save changes: ${error.message}`);
      } finally {
        // Reset button state
        const saveButton = document.querySelector('.btn-primary');
        if (saveButton) {
          saveButton.disabled = false;
          saveButton.innerHTML = '<span class="material-icons-round">save</span> Save';
        }
      }
    },
    
    openChatModal(model) {
      this.selectedChatModel = model;
      this.showChatModal = true;
      this.chatMessages = [];
      this.chatInput = '';
      this.isGenerating = false;
      
      // Add welcome message
      this.chatMessages.push({
        type: 'system',
        prefix: 'System:',
        content: `Connected to ${model.name}. Type your message and press Enter to test the model.`
      });
      
      // Focus input after modal opens
      this.$nextTick(() => {
        if (this.$refs.chatInput) {
          this.$refs.chatInput.focus();
        }
      });
    },
    
    closeChatModal() {
      this.showChatModal = false;
      this.selectedChatModel = null;
      this.chatMessages = [];
      this.chatInput = '';
      this.isGenerating = false;
    },
    
    async sendMessage() {
      if (!this.chatInput.trim() || this.isGenerating) return;
      
      const userMessage = this.chatInput.trim();
      this.chatInput = '';
      
      // Add user message
      this.chatMessages.push({
        type: 'user',
        prefix: 'You:',
        content: userMessage
      });
      
      this.isGenerating = true;
      this.scrollToBottom();
      
      try {
        // Call Ollama API to generate response
        const response = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: this.selectedChatModel.name,
            prompt: userMessage,
            stream: false
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          const aiResponse = data.response || 'No response generated';
          
          // Add AI response
          this.chatMessages.push({
            type: 'ai',
            prefix: `${this.selectedChatModel.name}:`,
            content: aiResponse
          });
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
      } catch (error) {
        console.error('Error calling Ollama API:', error);
        this.chatMessages.push({
          type: 'error',
          prefix: 'Error:',
          content: `Failed to get response: ${error.message}`
        });
      } finally {
        this.isGenerating = false;
        this.scrollToBottom();
      }
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const terminalBody = this.$refs.terminalBody;
        if (terminalBody) {
          terminalBody.scrollTop = terminalBody.scrollHeight;
        }
      });
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
            trainingTime: this.formatModelSize(model.modified),
            datasetSize: this.getModelSize(model.modified),
            updatedAt: this.parseModelDate(model.modified),
            tags: this.getModelTags(model.name),
            isFavorite: this.isFavoriteModel(model.name),
            capabilities: model.capabilities || [],
            // Enhanced model details from ollama show
            details: {
              capabilities: model.capabilities || [],
              architecture: model.architecture || 'Unknown',
              parameters: model.parameters || 'Unknown',
              context_length: model.context_length || 'Unknown',
              quantization: model.quantization || 'Unknown',
              temperature: model.temperature || 0.7,
              top_p: model.top_p || 0.9,
              system_prompt: model.system_prompt || '',
              license: model.license || 'Unknown'
            },
            ollamaModel: model // Keep original backend data
          }));
        } else {
          console.error('Failed to fetch models:', data.error);
          this.models = [];
        }
        
        console.log('Loaded local models:', this.models);
        console.log('Models loaded successfully:', this.models.length);
        
        // Load model details after models are loaded
        await this.loadModelDetails();
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
    
    formatModelSize(modified) {
      if (!modified) return 'Unknown';
      // Extract size from modified field like "7.4 GB 49 minutes ago"
      const sizeMatch = modified.match(/(\d+\.?\d*)\s*GB/);
      if (sizeMatch) {
        return `${sizeMatch[1]} GB`;
      }
      return 'Unknown';
    },
    
    getModelSize(modified) {
      if (!modified) return 'Unknown';
      // Extract size from modified field like "7.4 GB 49 minutes ago"
      const sizeMatch = modified.match(/(\d+\.?\d*)\s*GB/);
      if (sizeMatch) {
        return `${sizeMatch[1]}GB`;
      }
      return 'Unknown';
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
    
    parseModelSize(sizeString) {
      if (!sizeString) return 0;
      const match = sizeString.match(/(\d+\.?\d*)\s*GB/);
      return match ? parseFloat(match[1]) : 0;
    },
    
    parseParameters(paramString) {
      if (!paramString) return 0;
      const match = paramString.match(/(\d+\.?\d*)\s*B/);
      return match ? parseFloat(match[1]) : 0;
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

/* Model Details Modal */
.model-details-modal {
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.model-details-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item .label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.detail-item .value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}

.capabilities-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.capability-tag.large {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-weight: 500;
}

.system-prompt {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #4e73df;
}

.system-prompt p {
  margin: 0;
  color: #333;
  line-height: 1.5;
  white-space: pre-wrap;
}

/* Modal Actions */
.modal-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Editable Prompt */
.editable-prompt {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.prompt-textarea {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.4;
  resize: vertical;
  min-height: 200px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  transition: border-color 0.3s ease;
}

.prompt-textarea:focus {
  border-color: #4e73df;
  outline: none;
  box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
}

.prompt-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

/* Editable Description */
.editable-description textarea {
  resize: vertical;
  min-height: 80px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 0.75rem;
  transition: border-color 0.3s ease;
}

.editable-description textarea:focus {
  border-color: #4e73df;
  outline: none;
  box-shadow: 0 0 0 3px rgba(78, 115, 223, 0.1);
}

/* Edit Mode Styling */
.detail-section.editing {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

/* Chat Test Button */
.chat-test-btn {
  position: absolute;
  top: -84px;
  left: -18px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #4e73df;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(78, 115, 223, 0.3);
  transition: all 0.3s ease;
  z-index: 10;
}

.chat-test-btn:hover {
  background: #3d5fc7;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(78, 115, 223, 0.4);
}

.chat-test-btn .material-icons-round {
  font-size: 16px;
}

.rank-number {
  position: relative;
}

/* Chat Modal */
.chat-modal-overlay {
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
}

.chat-modal-content {
  width: 90%;
  max-width: 800px;
  height: 80vh;
  background: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.chat-header {
  background: #2d2d2d;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #404040;
}

.chat-model-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.chat-model-info .material-icons-round {
  color: #4e73df;
}

.chat-model-info h3 {
  margin: 0;
  color: #fff;
  font-size: 1.1rem;
}

.model-type {
  background: #4e73df;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Terminal Styling */
.chat-terminal {
  height: calc(100% - 80px);
  display: flex;
  flex-direction: column;
}

.terminal-header {
  background: #333;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #404040;
}

.terminal-controls {
  display: flex;
  gap: 0.5rem;
}

.control-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.control-dot.red { background: #ff5f56; }
.control-dot.yellow { background: #ffbd2e; }
.control-dot.green { background: #27ca3f; }

.terminal-title {
  color: #ccc;
  font-size: 0.9rem;
  font-weight: 500;
}

.terminal-body {
  flex: 1;
  background: #1e1e1e;
  padding: 1rem;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
}

.terminal-output {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message {
  display: flex;
  gap: 0.5rem;
  line-height: 1.4;
}

.message-prefix {
  color: #888;
  font-weight: bold;
  min-width: 120px;
}

.message-content {
  color: #fff;
  flex: 1;
  white-space: pre-wrap;
}

.message.user .message-prefix {
  color: #4e73df;
}

.message.ai .message-prefix {
  color: #27ca3f;
}

.message.system .message-prefix {
  color: #ffbd2e;
}

.message.error .message-prefix {
  color: #ff5f56;
}

.message.error .message-content {
  color: #ff5f56;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.typing-dot {
  width: 6px;
  height: 6px;
  background: #4e73df;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Terminal Input */
.terminal-input {
  background: #2d2d2d;
  padding: 1rem;
  border-top: 1px solid #404040;
}

.input-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.prompt-symbol {
  color: #4e73df;
  font-weight: bold;
  font-family: 'Courier New', monospace;
}

.terminal-input-field {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 1rem;
  outline: none;
}

.terminal-input-field::placeholder {
  color: #666;
}

.terminal-input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  
  .summary-cards {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .rankings-grid {
    grid-template-columns: 1fr;
  }
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color, #e9ecef);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.card-icon .material-icons-round {
  color: white;
  font-size: 24px;
}

.card-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-color, #2c3e50);
  margin: 0 0 0.5rem 0;
}

.card-content p {
  color: var(--text-muted, #6c757d);
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Rankings Section */
.rankings-section {
  margin-bottom: 2rem;
}

.rankings-section .section-header {
  margin-bottom: 1.5rem;
}

.rankings-section .section-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-color, #2c3e50);
}

.rankings-section .section-header p {
  color: var(--text-muted, #6c757d);
  margin: 0;
  font-size: 0.9rem;
}

.rankings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.ranking-card {
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color, #e9ecef);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ranking-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.clickable-card {
  cursor: pointer;
}

.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-color: var(--primary, #4e73df);
}

.ranking-card.top-rank {
  border: 2px solid #ffd700;
  background: linear-gradient(135deg, #fff9e6, #ffffff);
}

.rank-number {
  flex-shrink: 0;
}

.rank-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #8b6914;
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #666;
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #daa520);
  color: white;
}

.rank-normal {
  background: linear-gradient(135deg, #6c757d, #868e96);
  color: white;
}

.model-info {
  flex: 1;
}

.model-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color, #2c3e50);
  font-size: 1.1rem;
  font-weight: 600;
}

.model-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.stat .material-icons-round {
  font-size: 16px;
}

.model-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-tag {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.capability-more {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.model-params {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.param {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6c757d;
}

.param .material-icons-round {
  font-size: 14px;
}

.rank-score {
  text-align: center;
  flex-shrink: 0;
}

.score {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color, #007bff);
  margin: 0;
}

.score-label {
  font-size: 0.75rem;
  color: var(--text-muted, #6c757d);
  margin: 0;
}
</style>
