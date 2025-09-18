<template>
  <div class="model-comparison">
    <!-- Header Section -->
    <div class="header-section">
      <h1 class="page-title">
        <i class="material-icons-round">compare_arrows</i>
        Model Comparison
      </h1>
      <p class="page-subtitle">Compare AI models side-by-side with detailed specifications and performance metrics</p>
    </div>

    <!-- Model Selection Panel -->
    <div class="selection-panel">
      <div class="panel-header">
        <h3>
          <i class="material-icons-round">checklist</i>
          Select Models to Compare
        </h3>
        <div class="selection-controls">
          <button 
            @click="selectAllModels" 
            class="btn btn-outline-primary btn-sm"
            :disabled="availableModels.length === 0"
          >
            <i class="material-icons-round">select_all</i>
            Select All
          </button>
          <button 
            @click="clearSelection" 
            class="btn btn-outline-secondary btn-sm"
            :disabled="selectedModels.length === 0"
          >
            <i class="material-icons-round">clear_all</i>
            Clear All
          </button>
        </div>
      </div>
      
      <div class="model-grid">
        <div 
          v-for="model in availableModels" 
          :key="model.name"
          class="model-card"
          :class="{ 'selected': selectedModels.includes(model.name) }"
          @click="toggleModelSelection(model.name)"
        >
          <div class="model-info">
            <h4>{{ model.name }}</h4>
            <p class="model-size">{{ model.size }}</p>
            <div class="model-capabilities">
              <span 
                v-for="capability in model.capabilities" 
                :key="capability"
                class="capability-tag"
              >
                {{ capability }}
              </span>
            </div>
          </div>
          <div class="selection-indicator">
            <i class="material-icons-round">{{ selectedModels.includes(model.name) ? 'check_circle' : 'radio_button_unchecked' }}</i>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="selectedModels.length > 0" class="comparison-section">
      <div class="section-header">
        <h3>
          <i class="material-icons-round">table_chart</i>
          Model Comparison Table
        </h3>
        <div class="table-controls">
          <button 
            @click="exportComparison" 
            class="btn btn-outline-success btn-sm"
            :disabled="comparisonData.length === 0"
          >
            <i class="material-icons-round">download</i>
            Export CSV
          </button>
          <button 
            @click="refreshComparison" 
            class="btn btn-outline-primary btn-sm"
            :disabled="loading"
          >
            <i class="material-icons-round">refresh</i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading model details...</p>
      </div>

      <!-- Comparison Table -->
      <div v-else-if="comparisonData.length > 0" class="table-container">
        <div class="table-responsive">
          <table class="table table-striped comparison-table">
            <thead>
              <tr>
                <th class="sticky-column">Model</th>
                <th>Parameters</th>
                <th>Context Length</th>
                <th>Embedding Length</th>
                <th>Tokens</th>
                <th>Architecture</th>
                <th>Quantization</th>
                <th>Capabilities</th>
                <th>Training Data</th>
                <th>Vocabulary</th>
                <th>License</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="model in comparisonData" :key="model.name">
                <td class="sticky-column model-name-cell">
                  <div class="model-name">
                    <strong>{{ model.name }}</strong>
                    <small class="text-muted">{{ model.size }}</small>
                  </div>
                </td>
                <td>
                  <span class="metric-value">{{ model.details.parameters || 'N/A' }}</span>
                </td>
                <td>
                  <span class="metric-value">{{ formatNumber(model.details.context_length) }}</span>
                </td>
                <td>
                  <span class="metric-value">{{ formatNumber(model.details.embedding_length) }}</span>
                </td>
                <td>
                  <span class="metric-value">{{ model.details.tokens || 'N/A' }}</span>
                </td>
                <td>
                  <span class="architecture-tag">{{ model.details.architecture || 'N/A' }}</span>
                </td>
                <td>
                  <span class="quantization-tag">{{ model.details.quantization || 'N/A' }}</span>
                </td>
                <td>
                  <div class="capabilities-list">
                    <span 
                      v-for="capability in model.details.capabilities" 
                      :key="capability"
                      class="capability-badge"
                    >
                      {{ capability }}
                    </span>
                  </div>
                </td>
                <td>
                  <span class="metric-value">{{ model.details.training_data_size || 'N/A' }}</span>
                </td>
                <td>
                  <span class="metric-value">{{ model.details.vocab_size || 'N/A' }}</span>
                </td>
                <td>
                  <span class="license-text">{{ truncateText(model.details.license, 30) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <i class="material-icons-round">info</i>
        <h4>No comparison data available</h4>
        <p>Select models to compare their details</p>
      </div>
    </div>

    <!-- Performance Charts Section -->
    <div v-if="selectedModels.length > 1" class="charts-section">
      <div class="section-header">
        <h3>
          <i class="material-icons-round">bar_chart</i>
          Performance Comparison
        </h3>
      </div>

      <div class="charts-grid">
        <!-- Parameters Comparison Chart -->
        <div class="chart-container">
          <h5>Model Parameters (Billions)</h5>
          <div class="bar-chart">
            <div 
              v-for="model in comparisonData" 
              :key="model.name"
              class="bar-item"
            >
              <div class="bar-label">{{ model.name }}</div>
              <div class="bar-wrapper">
                <div 
                  class="bar" 
                  :style="{ width: `${(parseParameters(model.details.parameters) / Math.max(...comparisonData.map(m => parseParameters(m.details.parameters)))) * 100}%` }"
                ></div>
                <span class="bar-value">{{ model.details.parameters || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Context Length Comparison Chart -->
        <div class="chart-container">
          <h5>Context Length (Tokens)</h5>
          <div class="bar-chart">
            <div 
              v-for="model in comparisonData" 
              :key="model.name"
              class="bar-item"
            >
              <div class="bar-label">{{ model.name }}</div>
              <div class="bar-wrapper">
                <div 
                  class="bar context-bar" 
                  :style="{ width: `${(model.details.context_length / Math.max(...comparisonData.map(m => m.details.context_length || 0))) * 100}%` }"
                ></div>
                <span class="bar-value">{{ formatNumber(model.details.context_length) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Capabilities Comparison Chart -->
        <div class="chart-container">
          <h5>Capabilities Distribution</h5>
          <div class="capabilities-grid">
            <div 
              v-for="capability in uniqueCapabilities" 
              :key="capability"
              class="capability-item"
            >
              <span class="capability-name">{{ capability }}</span>
              <div class="capability-count">
                <span class="count">{{ getCapabilityCount(capability) }}</span>
                <span class="total">/ {{ comparisonData.length }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Details Modal -->
    <div v-if="selectedModelDetails" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="material-icons-round">info</i>
              {{ selectedModelDetails.name }} - Detailed Information
            </h5>
            <button type="button" class="btn-close" @click="closeModelDetails"></button>
          </div>
          <div class="modal-body">
            <div class="model-details-grid">
              <div class="detail-section">
                <h6>Technical Specifications</h6>
                <div class="detail-item">
                  <span class="label">Architecture:</span>
                  <span class="value">{{ selectedModelDetails.details.architecture || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Parameters:</span>
                  <span class="value">{{ selectedModelDetails.details.parameters || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Context Length:</span>
                  <span class="value">{{ formatNumber(selectedModelDetails.details.context_length) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Embedding Length:</span>
                  <span class="value">{{ formatNumber(selectedModelDetails.details.embedding_length) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Quantization:</span>
                  <span class="value">{{ selectedModelDetails.details.quantization || 'N/A' }}</span>
                </div>
              </div>

              <div class="detail-section">
                <h6>Training Information</h6>
                <div class="detail-item">
                  <span class="label">Estimated Tokens:</span>
                  <span class="value">{{ selectedModelDetails.details.tokens || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Training Data Size:</span>
                  <span class="value">{{ selectedModelDetails.details.training_data_size || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Vocabulary Size:</span>
                  <span class="value">{{ selectedModelDetails.details.vocab_size || 'N/A' }}</span>
                </div>
              </div>

              <div class="detail-section">
                <h6>Capabilities</h6>
                <div class="capabilities-list">
                  <span 
                    v-for="capability in selectedModelDetails.details.capabilities" 
                    :key="capability"
                    class="capability-badge"
                  >
                    {{ capability }}
                  </span>
                </div>
              </div>

              <div class="detail-section">
                <h6>Configuration</h6>
                <div class="config-params">
                  <div 
                    v-for="(value, key) in selectedModelDetails.details.parameters_config" 
                    :key="key"
                    class="config-item"
                  >
                    <span class="config-key">{{ key }}:</span>
                    <span class="config-value">{{ value }}</span>
                  </div>
                </div>
              </div>

              <div class="detail-section">
                <h6>License</h6>
                <p class="license-text">{{ selectedModelDetails.details.license || 'N/A' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModelDetails">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelComparison',
  data() {
    return {
      availableModels: [],
      selectedModels: [],
      comparisonData: [],
      loading: false,
      selectedModelDetails: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      },
      doughnutOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    }
  },
  computed: {
    uniqueCapabilities() {
      const capabilities = new Set()
      this.comparisonData.forEach(model => {
        model.details.capabilities?.forEach(capability => {
          capabilities.add(capability)
        })
      })
      return Array.from(capabilities)
    }
  },
  async mounted() {
    await this.loadAvailableModels()
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await fetch('http://localhost:5000/api/models')
        const data = await response.json()
        
        if (data.success) {
          this.availableModels = data.models
        } else {
          console.error('Failed to load models:', data.error)
        }
      } catch (error) {
        console.error('Error loading models:', error)
      }
    },
    
    toggleModelSelection(modelName) {
      const index = this.selectedModels.indexOf(modelName)
      if (index > -1) {
        this.selectedModels.splice(index, 1)
      } else {
        this.selectedModels.push(modelName)
      }
      this.loadComparisonData()
    },
    
    selectAllModels() {
      this.selectedModels = this.availableModels.map(m => m.name)
      this.loadComparisonData()
    },
    
    clearSelection() {
      this.selectedModels = []
      this.comparisonData = []
    },
    
    async loadComparisonData() {
      if (this.selectedModels.length === 0) {
        this.comparisonData = []
        return
      }
      
      this.loading = true
      this.comparisonData = []
      
      try {
        const promises = this.selectedModels.map(async (modelName) => {
          const response = await fetch(`http://localhost:5000/api/models/${modelName}/details`)
          const data = await response.json()
          
          if (data.success) {
            return {
              name: modelName,
              size: this.availableModels.find(m => m.name === modelName)?.size || 'Unknown',
              details: data.details
            }
          } else {
            console.error(`Failed to load details for ${modelName}:`, data.error)
            return null
          }
        })
        
        const results = await Promise.all(promises)
        this.comparisonData = results.filter(result => result !== null)
        
      } catch (error) {
        console.error('Error loading comparison data:', error)
      } finally {
        this.loading = false
      }
    },
    
    async refreshComparison() {
      await this.loadComparisonData()
    },
    
    exportComparison() {
      if (this.comparisonData.length === 0) return
      
      const csvContent = this.generateCSV()
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `model-comparison-${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    },
    
    generateCSV() {
      const headers = [
        'Model', 'Parameters', 'Context Length', 'Embedding Length', 'Tokens',
        'Architecture', 'Quantization', 'Capabilities', 'Training Data', 'Vocabulary', 'License'
      ]
      
      const rows = this.comparisonData.map(model => [
        model.name,
        model.details.parameters || 'N/A',
        model.details.context_length || 'N/A',
        model.details.embedding_length || 'N/A',
        model.details.tokens || 'N/A',
        model.details.architecture || 'N/A',
        model.details.quantization || 'N/A',
        model.details.capabilities?.join(', ') || 'N/A',
        model.details.training_data_size || 'N/A',
        model.details.vocab_size || 'N/A',
        model.details.license || 'N/A'
      ])
      
      return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
    },
    
    showModelDetails(model) {
      this.selectedModelDetails = model
    },
    
    closeModelDetails() {
      this.selectedModelDetails = null
    },
    
    formatNumber(num) {
      if (!num) return 'N/A'
      return num.toLocaleString()
    },
    
    parseParameters(paramStr) {
      if (!paramStr) return 0
      const match = paramStr.match(/(\d+\.?\d*)([BM])/)
      if (match) {
        const value = parseFloat(match[1])
        const unit = match[2]
        return unit === 'B' ? value : value / 1000
      }
      return 0
    },
    
    truncateText(text, maxLength) {
      if (!text) return 'N/A'
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },
    
    getCapabilityCount(capability) {
      return this.comparisonData.filter(model => 
        model.details.capabilities?.includes(capability)
      ).length
    }
  }
}
</script>

<style scoped>
.model-comparison {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  max-width: 600px;
  margin: 0 auto;
}

.selection-panel {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2c3e50;
}

.selection-controls {
  display: flex;
  gap: 0.5rem;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.model-card {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-card:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.model-card.selected {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.model-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.model-size {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
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

.selection-indicator {
  color: #6c757d;
  font-size: 1.5rem;
}

.comparison-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2c3e50;
}

.table-controls {
  display: flex;
  gap: 0.5rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.table-container {
  overflow-x: auto;
}

.comparison-table {
  min-width: 1200px;
}

.sticky-column {
  position: sticky;
  left: 0;
  background: white;
  z-index: 10;
}

.model-name-cell {
  min-width: 200px;
}

.model-name strong {
  color: #2c3e50;
}

.metric-value {
  font-weight: 500;
  color: #495057;
}

.architecture-tag,
.quantization-tag {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.capabilities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-badge {
  background: #007bff;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.license-text {
  font-size: 0.85rem;
  color: #6c757d;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.charts-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.chart-container {
  text-align: center;
}

.chart-container h5 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.performance-chart {
  height: 300px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.bar-label {
  min-width: 150px;
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.bar-wrapper {
  flex: 1;
  position: relative;
  height: 30px;
  background: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.context-bar {
  background: linear-gradient(90deg, #28a745, #1e7e34);
}

.bar-value {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.85rem;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.capability-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.capability-name {
  font-weight: 500;
  color: #2c3e50;
}

.capability-count {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.capability-count .count {
  font-weight: 700;
  color: #007bff;
  font-size: 1.1rem;
}

.capability-count .total {
  color: #6c757d;
  font-size: 0.9rem;
}

.model-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.detail-section h6 {
  color: #2c3e50;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-item .label {
  font-weight: 500;
  color: #6c757d;
}

.detail-item .value {
  color: #2c3e50;
}

.config-params {
  max-height: 200px;
  overflow-y: auto;
}

.config-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.config-key {
  font-weight: 500;
  color: #6c757d;
}

.config-value {
  color: #2c3e50;
}

.license-text {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.5;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-outline-primary {
  color: #007bff;
  border-color: #007bff;
}

.btn-outline-primary:hover {
  background-color: #007bff;
  color: white;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
}

.btn-outline-secondary:hover {
  background-color: #6c757d;
  color: white;
}

.btn-outline-success {
  color: #28a745;
  border-color: #28a745;
}

.btn-outline-success:hover {
  background-color: #28a745;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  border-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
  border-color: #545b62;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-dialog {
  max-width: 800px;
}

.modal-header {
  border-bottom: 1px solid #e9ecef;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.text-primary {
  color: #007bff !important;
}

.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}
</style>
