<template>
  <div class="evaluation-container">
    <div class="header">
      <h1>Model Evaluation</h1>
      <button class="btn btn-primary" @click="showNewEvaluationModal = true">
        <span class="emoji">➕</span> New Evaluation
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card" v-for="(metric, key) in metrics" :key="key">
        <div class="summary-icon" :class="key">
          <span class="emoji">{{ metric.icon }}</span>
        </div>
        <div class="summary-details">
          <h3>{{ metric.label }}</h3>
          <p class="metric">{{ metric.value }}</p>
          <p class="trend" :class="metric.trend > 0 ? 'positive' : 'negative'">
            <span class="emoji">{{ metric.trend > 0 ? '📈' : '📉' }}</span>
            {{ Math.abs(metric.trend) }}% {{ metric.trend > 0 ? 'increase' : 'decrease' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="evaluation-content">
      <!-- Tabs -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Evaluations List -->
      <div v-if="activeTab === 'evaluations'" class="evaluations-list">
        <div class="search-filter-bar">
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search evaluations..."
              class="search-input"
            >
            <span class="search-icon">🔍</span>
          </div>
          
          <select v-model="sortBy" class="filter-select">
            <option value="date_desc">Sort by Date (Newest)</option>
            <option value="date_asc">Sort by Date (Oldest)</option>
            <option value="accuracy_desc">Sort by Accuracy (High to Low)</option>
            <option value="accuracy_asc">Sort by Accuracy (Low to High)</option>
          </select>
        </div>

        <div class="evaluations-grid">
          <div 
            v-for="evaluation in filteredEvaluations" 
            :key="evaluation.id"
            class="evaluation-card"
          >
            <div class="evaluation-header">
              <div class="evaluation-model">
                <div class="model-avatar" :style="{ backgroundColor: stringToColor(evaluation.modelName) }">
                  {{ getInitials(evaluation.modelName) }}
                </div>
                <div>
                  <h4>{{ evaluation.modelName }}</h4>
                  <p class="model-type">{{ evaluation.modelType }}</p>
                </div>
              </div>
              <div class="evaluation-actions">
                <button class="btn-icon" @click="toggleFavorite(evaluation.id)">
                  {{ evaluation.isFavorite ? '⭐' : '☆' }}
                </button>
                <div class="dropdown">
                  <button class="btn-icon">⋮</button>
                  <div class="dropdown-content">
                    <a href="#" @click.prevent="viewEvaluationDetails(evaluation)">View Details</a>
                    <a href="#" @click.prevent="compareSelected(evaluation)">Compare</a>
                    <a href="#" @click.prevent="exportEvaluation(evaluation)">Export</a>
                    <a href="#" @click.prevent="deleteEvaluation(evaluation.id)" class="danger">Delete</a>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="evaluation-metrics">
              <div class="metric">
                <div class="metric-label">Accuracy</div>
                <div class="metric-value">
                  {{ evaluation.metrics.accuracy }}%
                  <span class="metric-trend" :class="{ 'up': evaluation.metrics.accuracyChange > 0, 'down': evaluation.metrics.accuracyChange < 0 }">
                    {{ evaluation.metrics.accuracyChange > 0 ? '↑' : '↓' }}
                    {{ Math.abs(evaluation.metrics.accuracyChange) }}%
                  </span>
                </div>
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: evaluation.metrics.accuracy + '%' }" :class="getAccuracyClass(evaluation.metrics.accuracy)"></div>
                </div>
              </div>
              
              <div class="metric">
                <div class="metric-label">Precision</div>
                <div class="metric-value">{{ evaluation.metrics.precision.toFixed(3) }}</div>
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (evaluation.metrics.precision * 100) + '%' }" :class="getMetricClass(evaluation.metrics.precision)"></div>
                </div>
              </div>
              
              <div class="metric">
                <div class="metric-label">Recall</div>
                <div class="metric-value">{{ evaluation.metrics.recall.toFixed(3) }}</div>
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (evaluation.metrics.recall * 100) + '%' }" :class="getMetricClass(evaluation.metrics.recall)"></div>
                </div>
              </div>
              
              <div class="metric">
                <div class="metric-label">F1 Score</div>
                <div class="metric-value">{{ evaluation.metrics.f1.toFixed(3) }}</div>
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (evaluation.metrics.f1 * 100) + '%' }" :class="getMetricClass(evaluation.metrics.f1)"></div>
                </div>
              </div>
            </div>
            
            <div class="evaluation-footer">
              <div class="dataset-info">
                <span class="emoji">📊</span>
                <span>{{ evaluation.datasetName }}</span>
              </div>
              <div class="evaluation-date">
                {{ formatDate(evaluation.date) }}
              </div>
            </div>
            
            <div class="evaluation-actions-footer">
              <button class="btn btn-sm btn-outline" @click="viewEvaluationDetails(evaluation)">
                <span class="emoji">🔍</span> Details
              </button>
              <button class="btn btn-sm" :class="{ 'btn-primary': evaluation.isSelected }" @click="toggleSelection(evaluation.id)">
                {{ evaluation.isSelected ? 'Selected' : 'Select' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Comparison View -->
      <div v-else-if="activeTab === 'comparison'" class="comparison-view">
        <div v-if="selectedEvaluations.length < 2" class="empty-state">
          <div class="empty-icon">
            <span class="emoji">🔍</span>
          </div>
          <h3>Compare Models</h3>
          <p>Select 2 or more evaluations to compare model performance.</p>
          <button class="btn btn-primary" @click="activeTab = 'evaluations'">
            <span class="emoji">📊</span> View Evaluations
          </button>
        </div>
        <div v-else>
          <div class="comparison-header">
            <h2>Model Comparison</h2>
            <div class="comparison-actions">
              <button class="btn btn-outline" @click="exportComparison">
                <span class="emoji">📤</span> Export Comparison
              </button>
              <button class="btn btn-outline" @click="clearComparison">
                <span class="emoji">🗑️</span> Clear All
              </button>
            </div>
          </div>
          
          <div class="metrics-table">
            <table>
              <thead>
                <tr>
                  <th>Metric</th>
                  <th v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.modelName }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Accuracy</td>
                  <td v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.metrics.accuracy }}%
                  </td>
                </tr>
                <tr>
                  <td>Precision</td>
                  <td v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.metrics.precision.toFixed(3) }}
                  </td>
                </tr>
                <tr>
                  <td>Recall</td>
                  <td v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.metrics.recall.toFixed(3) }}
                  </td>
                </tr>
                <tr>
                  <td>F1 Score</td>
                  <td v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.metrics.f1.toFixed(3) }}
                  </td>
                </tr>
                <tr>
                  <td>Inference Time</td>
                  <td v-for="eval in selectedEvaluations" :key="eval.id">
                    {{ eval.metrics.inferenceTime }}ms
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- History View -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <span class="emoji">📜</span>
        </div>
        <h3>Evaluation History</h3>
        <p>View past evaluation runs and their results.</p>
        <p>This feature is coming soon!</p>
      </div>
    </div>
    
    <!-- New Evaluation Modal -->
    <div v-if="showNewEvaluationModal" class="modal-overlay" @click.self="showNewEvaluationModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>New Model Evaluation</h2>
          <button class="btn-icon" @click="showNewEvaluationModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Select Model</label>
            <select v-model="newEvaluation.modelId" class="form-control">
              <option value="" disabled>Select a model</option>
              <option v-for="model in availableModels" :key="model.id" :value="model.id">
                {{ model.name }} ({{ model.type }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Select Dataset</label>
            <select v-model="newEvaluation.datasetId" class="form-control">
              <option value="" disabled>Select a dataset</option>
              <option v-for="dataset in availableDatasets" :key="dataset.id" :value="dataset.id">
                {{ dataset.name }} ({{ dataset.type }})
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Evaluation Name</label>
            <input 
              type="text" 
              v-model="newEvaluation.name" 
              placeholder="e.g., BERT-base on IMDB Test Set"
              class="form-control"
            >
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showNewEvaluationModal = false">
            Cancel
          </button>
          <button class="btn btn-primary" @click="startEvaluation" :disabled="!canStartEvaluation">
            Start Evaluation
          </button>
        </div>
      </div>
    </div>
    
    <!-- Evaluation Details Modal -->
    <div v-if="selectedEvaluation" class="modal-overlay" @click.self="selectedEvaluation = null">
      <div class="modal evaluation-details-modal">
        <div class="modal-header">
          <h2>Evaluation Details</h2>
          <div class="header-actions">
            <button class="btn-icon" @click="exportEvaluation(selectedEvaluation)" title="Export">
              <span class="emoji">📤</span>
            </button>
            <button class="btn-icon" @click="selectedEvaluation = null">✕</button>
          </div>
        </div>
        
        <div class="modal-body">
          <div class="evaluation-details-header">
            <div class="model-info">
              <h3>{{ selectedEvaluation.modelName }}</h3>
              <p class="model-type">{{ selectedEvaluation.modelType }}</p>
              <p class="evaluation-date">Evaluated on {{ formatDate(selectedEvaluation.date, true) }}</p>
            </div>
            
            <div class="evaluation-metrics-summary">
              <div class="metric-summary">
                <div class="metric-value">{{ selectedEvaluation.metrics.accuracy }}%</div>
                <div class="metric-label">Accuracy</div>
                <div class="metric-change" :class="{ 'positive': selectedEvaluation.metrics.accuracyChange > 0, 'negative': selectedEvaluation.metrics.accuracyChange < 0 }">
                  {{ selectedEvaluation.metrics.accuracyChange > 0 ? '+' : '' }}{{ selectedEvaluation.metrics.accuracyChange }}% from previous
                </div>
              </div>
              
              <div class="metric-summary">
                <div class="metric-value">{{ selectedEvaluation.metrics.f1.toFixed(3) }}</div>
                <div class="metric-label">F1 Score</div>
              </div>
              
              <div class="metric-summary">
                <div class="metric-value">{{ selectedEvaluation.metrics.inferenceTime }}ms</div>
                <div class="metric-label">Avg. Inference</div>
              </div>
            </div>
          </div>
          
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-card-header">
                <h4>Precision</h4>
                <div class="metric-value">{{ selectedEvaluation.metrics.precision.toFixed(3) }}</div>
              </div>
              <div class="metric-card-content">
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (selectedEvaluation.metrics.precision * 100) + '%' }" :class="getMetricClass(selectedEvaluation.metrics.precision)"></div>
                </div>
                <p>Measures the accuracy of positive predictions</p>
              </div>
            </div>
            
            <div class="metric-card">
              <div class="metric-card-header">
                <h4>Recall</h4>
                <div class="metric-value">{{ selectedEvaluation.metrics.recall.toFixed(3) }}</div>
              </div>
              <div class="metric-card-content">
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (selectedEvaluation.metrics.recall * 100) + '%' }" :class="getMetricClass(selectedEvaluation.metrics.recall)"></div>
                </div>
                <p>Measures the ability to find all positive samples</p>
              </div>
            </div>
            
            <div class="metric-card">
              <div class="metric-card-header">
                <h4>F1 Score</h4>
                <div class="metric-value">{{ selectedEvaluation.metrics.f1.toFixed(3) }}</div>
              </div>
              <div class="metric-card-content">
                <div class="metric-bar">
                  <div class="metric-bar-fill" :style="{ width: (selectedEvaluation.metrics.f1 * 100) + '%' }" :class="getMetricClass(selectedEvaluation.metrics.f1)"></div>
                </div>
                <p>Harmonic mean of precision and recall</p>
              </div>
            </div>
            
            <div class="metric-card">
              <div class="metric-card-header">
                <h4>Inference Time</h4>
                <div class="metric-value">{{ selectedEvaluation.metrics.inferenceTime }}ms</div>
              </div>
              <div class="metric-card-content">
                <div class="metric-bar">
                  <div class="metric-bar-fill time" :style="{ width: Math.min(100, (1 - (selectedEvaluation.metrics.inferenceTime / 1000)) * 100) + '%' }"></div>
                </div>
                <p>Average time per prediction (lower is better)</p>
              </div>
            </div>
          </div>
          
          <div class="dataset-info">
            <h4>Dataset Information</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Dataset:</span>
                <span class="info-value">{{ selectedEvaluation.datasetName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Samples:</span>
                <span class="info-value">{{ selectedEvaluation.datasetSize.toLocaleString() }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Evaluation Time:</span>
                <span class="info-value">{{ formatDateTime(selectedEvaluation.date) }}</span>
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
  name: 'EvaluationView',
  data() {
    return {
      activeTab: 'evaluations',
      searchQuery: '',
      sortBy: 'date_desc',
      showNewEvaluationModal: false,
      selectedEvaluation: null,
      metrics: {
        accuracy: { label: 'Average Accuracy', value: '87.5%', trend: 2.3, icon: '🎯' },
        models: { label: 'Models Evaluated', value: '24', trend: 5, icon: '🤖' },
        datasets: { label: 'Test Datasets', value: '12', trend: 3, icon: '📊' }
      },
      tabs: [
        { id: 'evaluations', label: 'Evaluations' },
        { id: 'comparison', label: 'Comparison' },
        { id: 'history', label: 'History' }
      ],
      newEvaluation: {
        modelId: '',
        datasetId: '',
        name: ''
      },
      availableModels: [
        { id: 'model-1', name: 'ResNet-50', type: 'Image Classification' },
        { id: 'model-2', name: 'BERT-base', type: 'Text Classification' },
        { id: 'model-3', name: 'YOLOv5s', type: 'Object Detection' }
      ],
      availableDatasets: [
        { id: 'dataset-1', name: 'CIFAR-10 Test Set', type: 'Image' },
        { id: 'dataset-2', name: 'IMDB Reviews', type: 'Text' },
        { id: 'dataset-3', name: 'COCO Val 2017', type: 'Image' }
      ],
      evaluations: [
        {
          id: 'eval-1',
          modelId: 'model-1',
          modelName: 'ResNet-50',
          modelType: 'Image Classification',
          datasetId: 'dataset-1',
          datasetName: 'CIFAR-10 Test Set',
          datasetSize: 10000,
          date: '2023-11-15T14:30:00Z',
          isFavorite: true,
          isSelected: false,
          metrics: {
            accuracy: 92.3,
            accuracyChange: 1.2,
            precision: 0.924,
            recall: 0.918,
            f1: 0.921,
            inferenceTime: 45
          }
        },
        {
          id: 'eval-2',
          modelId: 'model-2',
          modelName: 'BERT-base',
          modelType: 'Text Classification',
          datasetId: 'dataset-2',
          datasetName: 'IMDB Reviews',
          datasetSize: 25000,
          date: '2023-11-10T09:15:00Z',
          isFavorite: false,
          isSelected: false,
          metrics: {
            accuracy: 89.7,
            accuracyChange: -0.5,
            precision: 0.901,
            recall: 0.892,
            f1: 0.896,
            inferenceTime: 28
          }
        },
        {
          id: 'eval-3',
          modelId: 'model-3',
          modelName: 'YOLOv5s',
          modelType: 'Object Detection',
          datasetId: 'dataset-3',
          datasetName: 'COCO Val 2017',
          datasetSize: 5000,
          date: '2023-11-05T16:45:00Z',
          isFavorite: true,
          isSelected: false,
          metrics: {
            accuracy: 76.2,
            accuracyChange: 3.1,
            precision: 0.745,
            recall: 0.768,
            f1: 0.756,
            inferenceTime: 18
          }
        }
      ]
    };
  },
  computed: {
    filteredEvaluations() {
      return this.evaluations.filter(eval => 
        eval.modelName.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        eval.modelType.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        eval.datasetName.toLowerCase().includes(this.searchQuery.toLowerCase())
      ).sort((a, b) => {
        const [field, order] = this.sortBy.split('_');
        let aValue, bValue;
        
        if (field === 'date') {
          aValue = new Date(a.date);
          bValue = new Date(b.date);
        } else if (field === 'accuracy') {
          aValue = a.metrics.accuracy;
          bValue = b.metrics.accuracy;
        } else {
          aValue = a[field];
          bValue = b[field];
        }
        
        if (order === 'asc') {
          return aValue > bValue ? 1 : -1;
        } else {
          return aValue < bValue ? 1 : -1;
        }
      });
    },
    selectedEvaluations() {
      return this.evaluations.filter(eval => eval.isSelected);
    },
    canStartEvaluation() {
      return this.newEvaluation.modelId && this.newEvaluation.datasetId && this.newEvaluation.name;
    }
  },
  methods: {
    formatDate(dateString, includeTime = false) {
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        ...(includeTime && { hour: '2-digit', minute: '2-digit' })
      };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString();
    },
    getInitials(name) {
      return name.split(' ').map(part => part[0]).join('').toUpperCase().substring(0, 2);
    },
    stringToColor(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      const hue = Math.abs(hash % 360);
      return `hsl(${hue}, 70%, 80%)`;
    },
    getAccuracyClass(accuracy) {
      if (accuracy >= 90) return 'excellent';
      if (accuracy >= 80) return 'good';
      if (accuracy >= 70) return 'fair';
      return 'poor';
    },
    getMetricClass(value) {
      if (value >= 0.9) return 'excellent';
      if (value >= 0.8) return 'good';
      if (value >= 0.7) return 'fair';
      return 'poor';
    },
    toggleFavorite(id) {
      const evaluation = this.evaluations.find(e => e.id === id);
      if (evaluation) evaluation.isFavorite = !evaluation.isFavorite;
    },
    toggleSelection(id) {
      const evaluation = this.evaluations.find(e => e.id === id);
      if (evaluation) evaluation.isSelected = !evaluation.isSelected;
    },
    viewEvaluationDetails(evaluation) {
      this.selectedEvaluation = evaluation;
    },
    compareSelected(evaluation) {
      this.toggleSelection(evaluation.id);
      this.activeTab = 'comparison';
    },
    clearComparison() {
      this.evaluations.forEach(eval => { eval.isSelected = false; });
      this.activeTab = 'evaluations';
    },
    exportEvaluation(evaluation) {
      console.log('Exporting evaluation:', evaluation.id);
      alert(`Exporting evaluation: ${evaluation.modelName} on ${evaluation.datasetName}`);
    },
    exportComparison() {
      console.log('Exporting comparison of:', this.selectedEvaluations.map(e => e.id));
      alert(`Exporting comparison of ${this.selectedEvaluations.length} models`);
    },
    deleteEvaluation(id) {
      if (confirm('Are you sure you want to delete this evaluation?')) {
        this.evaluations = this.evaluations.filter(e => e.id !== id);
      }
    },
    startEvaluation() {
      console.log('Starting evaluation:', this.newEvaluation);
      // In a real app, this would call an API to start the evaluation
      // For now, we'll just add a new evaluation with sample data
      const newEval = {
        id: 'eval-' + Date.now(),
        modelId: this.newEvaluation.modelId,
        modelName: this.availableModels.find(m => m.id === this.newEvaluation.modelId)?.name || 'Unknown Model',
        modelType: this.availableModels.find(m => m.id === this.newEvaluation.modelId)?.type || 'Unknown',
        datasetId: this.newEvaluation.datasetId,
        datasetName: this.availableDatasets.find(d => d.id === this.newEvaluation.datasetId)?.name || 'Unknown Dataset',
        datasetSize: 1000, // Default size for demo
        date: new Date().toISOString(),
        isFavorite: false,
        isSelected: false,
        metrics: {
          accuracy: Math.random() * 20 + 80, // Random value between 80-100
          accuracyChange: (Math.random() * 5 - 2.5).toFixed(1), // Random change between -2.5 and 2.5
          precision: (Math.random() * 0.3 + 0.7).toFixed(3), // Random value between 0.7-1.0
          recall: (Math.random() * 0.3 + 0.7).toFixed(3), // Random value between 0.7-1.0
          f1: (Math.random() * 0.3 + 0.7).toFixed(3), // Random value between 0.7-1.0
          inferenceTime: Math.floor(Math.random() * 50) + 10 // Random time between 10-60ms
        }
      };
      
      this.evaluations.unshift(newEval);
      this.showNewEvaluationModal = false;
      this.newEvaluation = { modelId: '', datasetId: '', name: '' };
    }
  }
};
</script>

<style scoped>
/* Base styles */
.evaluation-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  margin: 0;
  font-size: 2rem;
  color: #333;
}

/* Summary cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  border: 1px solid #eee;
}

.summary-icon {
  font-size: 2.5rem;
  margin-right: 1.5rem;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-icon.accuracy { background-color: #e3f2fd; color: #1976d2; }
.summary-icon.models { background-color: #e8f5e9; color: #2e7d32; }
.summary-icon.datasets { background-color: #fff3e0; color: #e65100; }

.summary-details h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #666;
  font-weight: 500;
}

.metric {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #333;
}

.trend {
  font-size: 0.85rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.trend.positive { color: #2e7d32; }
.trend.negative { color: #d32f2f; }

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 0.95rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  color: #1976d2;
}

.tab.active {
  color: #1976d2;
  border-bottom-color: #1976d2;
}

/* Search and filter bar */
.search-filter-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #777;
  pointer-events: none;
}

.filter-select {
  padding: 0.7rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 200px;
}

.filter-select:focus {
  outline: none;
  border-color: #1976d2;
}

/* Evaluations grid */
.evaluations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.evaluation-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
}

.evaluation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.evaluation-model {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.model-avatar {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.evaluation-model h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #333;
}

.model-type {
  margin: 0;
  font-size: 0.8rem;
  color: #666;
  background: #f5f5f5;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.evaluation-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0.3rem;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.btn-icon:hover {
  background-color: #f5f5f5;
  color: #333;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content {
  display: none;
  position: absolute;
  right: 0;
  background-color: white;
  min-width: 160px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  z-index: 1;
  border: 1px solid #eee;
  overflow: hidden;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-content a {
  color: #333;
  padding: 0.75rem 1rem;
  text-decoration: none;
  display: block;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.dropdown-content a:hover {
  background-color: #f8f9fa;
}

.dropdown-content a.danger {
  color: #d32f2f;
}

/* Metrics */
.evaluation-metrics {
  margin-bottom: 1.5rem;
}

.metric {
  margin-bottom: 1rem;
}

.metric:last-child {
  margin-bottom: 0;
}

.metric-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.metric-trend {
  font-size: 0.8rem;
  font-weight: 500;
}

.metric-trend.up { color: #2e7d32; }
.metric-trend.down { color: #d32f2f; }

.metric-bar {
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.metric-bar-fill.excellent { background-color: #2e7d32; }
.metric-bar-fill.good { background-color: #1976d2; }
.metric-bar-fill.fair { background-color: #ed6c02; }
.metric-bar-fill.poor { background-color: #d32f2f; }
.metric-bar-fill.time { background-color: #7b1fa2; }

/* Footer */
.evaluation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  font-size: 0.85rem;
  color: #666;
}

.dataset-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.evaluation-actions-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-outline {
  background: none;
  border: 1px solid #ddd;
  color: #333;
}

.btn-outline:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

/* Comparison view */
.comparison-view {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.comparison-actions {
  display: flex;
  gap: 0.75rem;
}

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.5rem;
}

.metrics-table th,
.metrics-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.metrics-table th {
  font-weight: 600;
  color: #333;
  background-color: #f9f9f9;
}

.metrics-table tr:hover {
  background-color: #f5f5f5;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  color: #666;
}

/* Modal */
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
}

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
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
  font-size: 1.5rem;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex-grow: 1;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #444;
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* Evaluation details */
.evaluation-details-modal {
  max-width: 900px;
}

.evaluation-details-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.model-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #333;
}

.evaluation-date {
  color: #666;
  font-size: 0.9rem;
}

.evaluation-metrics-summary {
  display: flex;
  gap: 2rem;
}

.metric-summary {
  text-align: center;
}

.metric-summary .metric-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 0.25rem;
}

.metric-summary .metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.metric-summary .metric-change {
  font-size: 0.8rem;
  font-weight: 500;
}

.metric-summary .metric-change.positive { color: #2e7d32; }
.metric-summary .metric-change.negative { color: #d32f2f; }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 1.25rem;
  border: 1px solid #eee;
}

.metric-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.metric-card-header h4 {
  margin: 0;
  font-size: 0.95rem;
  color: #555;
}

.metric-card-header .metric-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1976d2;
}

.metric-card-content p {
  margin: 0.75rem 0 0 0;
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

.dataset-info {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #eee;
}

.dataset-info h4 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  margin-bottom: 0.5rem;
}

.info-label {
  font-weight: 500;
  color: #555;
  margin-right: 0.5rem;
}

.info-value {
  color: #333;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-filter-bar {
    flex-direction: column;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .evaluation-details-header {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .evaluation-metrics-summary {
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .evaluation-card {
    padding: 1rem;
  }
  
  .evaluation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .evaluation-actions {
    align-self: flex-end;
  }
}
</style>
