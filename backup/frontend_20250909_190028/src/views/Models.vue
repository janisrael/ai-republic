<template>
  <div class="models-container">
    <div class="page-header">
      <div>
        <h1>AI Models</h1>
        <p>Manage your machine learning models and their configurations</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModelModal = true">
        <i>+</i> Create New Model
      </button>
    </div>

    <!-- Model Filters -->
    <div class="filters-container">
      <div class="search-box">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search models..." 
          v-model="searchQuery"
        />
        <i>🔍</i>
      </div>
      
      <div class="filter-group">
        <label>Filter by Type:</label>
        <select class="form-control" v-model="selectedType">
          <option value="">All Types</option>
          <option v-for="type in modelTypes" :key="type" :value="type">
            {{ type }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Sort By:</label>
        <select class="form-control" v-model="sortBy">
          <option value="name">Name (A-Z)</option>
          <option value="date">Last Updated</option>
          <option value="accuracy">Accuracy</option>
        </select>
      </div>
    </div>

    <!-- Models Grid -->
    <div class="models-grid">
      <div 
        v-for="model in filteredModels" 
        :key="model.id" 
        class="model-card neumorphic-card"
        @click="viewModelDetails(model)"
      >
        <div class="model-header">
          <div class="model-type" :class="model.type.toLowerCase()">
            {{ model.type }}
          </div>
          <div class="model-actions">
            <button class="btn-icon" @click.stop="toggleModelFavorite(model)">
              {{ model.isFavorite ? '⭐' : '☆' }}
            </button>
            <div class="dropdown">
              <button class="btn-icon" @click.stop="toggleDropdown($event, model.id)">
                ⋮
              </button>
              <div v-if="activeDropdown === model.id" class="dropdown-menu">
                <button @click.stop="editModel(model)">
                  <i>✏️</i> Edit
                </button>
                <button @click.stop="duplicateModel(model)">
                  <i>⎘</i> Duplicate
                </button>
                <button @click.stop="deleteModel(model.id)" class="danger">
                  <i>🗑️</i> Delete
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="model-body">
          <div class="model-avatar">
            <i>{{ getModelIcon(model.type) }}</i>
          </div>
          <h3>{{ model.name }}</h3>
          <p class="model-description">{{ model.description || 'No description provided.' }}</p>
          
          <div class="model-stats">
            <div class="stat">
              <span class="stat-value">{{ model.accuracy }}%</span>
              <span class="stat-label">Accuracy</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ model.trainingTime }}</span>
              <span class="stat-label">Training Time</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ model.datasetSize }}</span>
              <span class="stat-label">Samples</span>
            </div>
          </div>
        </div>
        
        <div class="model-footer">
          <div class="model-tags">
            <span class="tag" v-for="tag in model.tags" :key="tag">{{ tag }}</span>
          </div>
          <div class="model-updated">
            Updated {{ formatDate(model.updatedAt) }}
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredModels.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <h3>No models found</h3>
        <p>Try adjusting your search or create a new model to get started.</p>
        <button class="btn btn-primary" @click="showCreateModelModal = true">
          Create Your First Model
        </button>
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
      editingModel: null,
      modelToDelete: null,
      modelForm: {
        name: '',
        type: 'Text Classification',
        description: '',
        tags: ''
      },
      modelTypes: [
        'Text Classification',
        'Image Classification',
        'Object Detection',
        'Text Generation',
        'Translation',
        'Summarization',
        'Question Answering',
        'Sentiment Analysis'
      ],
      models: [
        {
          id: 1,
          name: 'Sentiment Analyzer',
          type: 'Sentiment Analysis',
          description: 'Analyzes text sentiment as positive, negative, or neutral',
          accuracy: 92.5,
          trainingTime: '2h 15m',
          datasetSize: '25,000',
          tags: ['nlp', 'sentiment', 'classification'],
          isFavorite: true,
          updatedAt: '2023-10-15T14:30:00Z'
        },
        {
          id: 2,
          name: 'Image Classifier',
          type: 'Image Classification',
          description: 'Classifies images into 1000 different categories',
          accuracy: 87.3,
          trainingTime: '8h 45m',
          datasetSize: '1.2M',
          tags: ['cv', 'classification', 'imagenet'],
          isFavorite: false,
          updatedAt: '2023-10-10T09:15:00Z'
        },
        {
          id: 3,
          name: 'News Summarizer',
          type: 'Summarization',
          description: 'Generates concise summaries of news articles',
          accuracy: 78.9,
          trainingTime: '5h 30m',
          datasetSize: '50,000',
          tags: ['nlp', 'summarization', 'generation'],
          isFavorite: true,
          updatedAt: '2023-10-05T16:45:00Z'
        },
        {
          id: 4,
          name: 'Language Translator',
          type: 'Translation',
          description: 'Translates between English and Spanish',
          accuracy: 95.1,
          trainingTime: '12h 20m',
          datasetSize: '500,000',
          tags: ['nlp', 'translation', 'bilingual'],
          isFavorite: false,
          updatedAt: '2023-09-28T11:20:00Z'
        }
      ]
    };
  },
  computed: {
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
    getModelIcon(type) {
      const icons = {
        'Text Classification': '📝',
        'Image Classification': '🖼️',
        'Object Detection': '🎯',
        'Text Generation': '✍️',
        'Translation': '🌐',
        'Summarization': '📑',
        'Question Answering': '❓',
        'Sentiment Analysis': '😊'
      };
      return icons[type] || '🤖';
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
    }
  },
  
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
.models-container {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  font-size: 1.8rem;
  margin: 0 0 0.25rem;
  color: var(--text-color);
}

.page-header p {
  margin: 0;
  color: var(--secondary);
}

.filters-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
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
</style>
