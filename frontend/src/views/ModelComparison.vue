<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>Model Comparison</h1>
      <p>Compare AI models side-by-side with detailed specifications and performance metrics</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">smart_toy</span>
        </div>
        <div class="stats-info">
          <h3>{{ availableModels.length }}</h3>
          <p>Available Models</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon training">
          <span class="material-icons-round">compare_arrows</span>
        </div>
        <div class="stats-info">
          <h3>{{ selectedModels.length }}</h3>
          <p>Selected for Comparison</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon dataset">
          <span class="material-icons-round">table_chart</span>
        </div>
        <div class="stats-info">
          <h3>{{ comparisonData.length }}</h3>
          <p>Models Compared</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon accuracy">
          <span class="material-icons-round">analytics</span>
        </div>
        <div class="stats-info">
          <h3>{{ uniqueCapabilities.length }}</h3>
          <p>Unique Capabilities</p>
        </div>
      </div>
    </div>

    <!-- Model Selection and Comparison -->
    <div class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Model Selection</h3>
            <div class="selection-controls">
              <button 
                @click="selectAllModels" 
                class="btn btn-sm btn-outline-primary"
                :disabled="availableModels.length === 0"
              >
                <span class="material-icons-round">select_all</span>
                Select All
              </button>
              <button 
                @click="clearSelection" 
                class="btn btn-sm btn-outline-secondary"
                :disabled="selectedModels.length === 0"
              >
                <span class="material-icons-round">clear_all</span>
                Clear All
              </button>
            </div>
          </div>
          
          <div class="model-selection-grid">
            <div 
              v-for="model in availableModels" 
              :key="model.name"
              class="model-selection-card"
              :class="{ 'selected': selectedModels.includes(model.name) }"
              @click="toggleModelSelection(model.name)"
            >
              <div class="model-info">
                <div class="model-header-with-avatar">
                  <div class="model-avatar" v-if="model.avatar_url">
                    <img :src="model.avatar_url" :alt="model.name + ' avatar'" class="avatar-image">
                  </div>
                  <div class="model-avatar-placeholder" v-else>
                    <span class="material-icons-round">smart_toy</span>
                  </div>
                  <h4>{{ model.name }}</h4>
                </div>
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
                <span class="material-icons-round">{{ selectedModels.includes(model.name) ? 'check_circle' : 'radio_button_unchecked' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Comparison Actions</h3>
            <div class="action-controls">
              <button 
                @click="loadComparisonData" 
                class="btn btn-sm btn-primary"
                :disabled="selectedModels.length === 0 || loading"
              >
                <span class="material-icons-round">compare_arrows</span>
                {{ loading ? 'Loading...' : 'Compare Models' }}
              </button>
              <button 
                @click="exportComparison" 
                class="btn btn-sm btn-outline-success"
                :disabled="comparisonData.length === 0"
              >
                <span class="material-icons-round">download</span>
                Export CSV
              </button>
            </div>
          </div>
          
          <div v-if="loading" class="loading-state">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Loading model details...</p>
          </div>

          <div v-else-if="comparisonData.length > 0" class="comparison-summary">
            <h4>Comparison Summary</h4>
            <div class="summary-stats">
              <div class="summary-item">
                <span class="label">Models Compared:</span>
                <span class="value">{{ comparisonData.length }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Total Parameters:</span>
                <span class="value">{{ getTotalParameters() }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Avg Context Length:</span>
                <span class="value">{{ getAvgContextLength() }}</span>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <span class="material-icons-round">compare_arrows</span>
            <p>Select models to compare their specifications and performance</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="comparisonData.length > 0" class="neumorphic-card comparison-table-card">
      <div class="card-header">
        <h3>Detailed Comparison</h3>
        <div class="table-controls">
          <button 
            @click="refreshComparison" 
            class="btn btn-sm btn-outline-primary"
            :disabled="loading"
          >
            <span class="material-icons-round">refresh</span>
            Refresh
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Parameters</th>
              <th>Context Length</th>
              <th>Embedding Length</th>
              <th>Quantization</th>
              <th>Temperature</th>
              <th>Top P</th>
              <th>Capabilities</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in comparisonData" :key="model.name">
              <td class="model-name-cell">
                <div class="model-name">
                  <div class="model-name-with-avatar">
                    <div class="model-avatar-small" v-if="model.avatar_url">
                      <img :src="model.avatar_url" :alt="model.name + ' avatar'" class="avatar-image-small">
                    </div>
                    <div class="model-avatar-placeholder-small" v-else>
                      <span class="material-icons-round">smart_toy</span>
                    </div>
                    <div class="model-name-text">
                      <strong>{{ model.name }}</strong>
                      <small>{{ model.details.architecture || 'Unknown' }}</small>
                    </div>
                  </div>
                </div>
              </td>
              <td>{{ model.details.parameters || 'Unknown' }}</td>
              <td>{{ model.details.context_length || 'Unknown' }}</td>
              <td>{{ model.details.embedding_length || 'Unknown' }}</td>
              <td>{{ model.details.quantization || 'Unknown' }}</td>
              <td>{{ model.details.temperature || 'Unknown' }}</td>
              <td>{{ model.details.top_p || 'Unknown' }}</td>
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
                <button 
                  @click="viewModelDetails(model)"
                  class="btn btn-sm btn-outline-primary"
                >
                  <span class="material-icons-round">visibility</span>
                  Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Performance Charts -->
    <div v-if="comparisonData.length > 1" class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Performance Comparison</h3>
          </div>
          <div class="chart-container">
            <canvas ref="performanceChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Capabilities Overview</h3>
          </div>
          <div class="chart-container">
            <canvas ref="capabilitiesChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Details Modal -->
    <div v-if="selectedModelDetails" class="modal-overlay" @click.self="selectedModelDetails = null">
      <div class="modal model-details-modal">
        <div class="modal-header">
          <h2>Model Details</h2>
          <button class="btn-icon" @click="selectedModelDetails = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="model-details-content">
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Name:</span>
                  <span class="value">{{ selectedModelDetails.name }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Architecture:</span>
                  <span class="value">{{ selectedModelDetails.details.architecture || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Parameters:</span>
                  <span class="value">{{ selectedModelDetails.details.parameters || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Context Length:</span>
                  <span class="value">{{ selectedModelDetails.details.context_length || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Configuration</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="label">Temperature:</span>
                  <span class="value">{{ selectedModelDetails.details.temperature || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Top P:</span>
                  <span class="value">{{ selectedModelDetails.details.top_p || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Quantization:</span>
                  <span class="value">{{ selectedModelDetails.details.quantization || 'Unknown' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Embedding Length:</span>
                  <span class="value">{{ selectedModelDetails.details.embedding_length || 'Unknown' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Capabilities</h4>
              <div class="capabilities-grid">
                <span 
                  v-for="capability in selectedModelDetails.details.capabilities" 
                  :key="capability"
                  class="capability-tag large"
                >
                  {{ capability }}
                </span>
              </div>
            </div>

            <div v-if="selectedModelDetails.details.system_prompt" class="detail-section">
              <h4>System Prompt</h4>
              <div class="system-prompt">
                <p>{{ selectedModelDetails.details.system_prompt }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'ModelComparisonView',
  data() {
    return {
      availableModels: [],
      selectedModels: [],
      comparisonData: [],
      loading: false,
      selectedModelDetails: null,
      chartInstances: []
    };
  },
  computed: {
    uniqueCapabilities() {
      const capabilities = new Set();
      this.comparisonData.forEach(model => {
        model.details.capabilities?.forEach(capability => {
          capabilities.add(capability);
        });
      });
      return Array.from(capabilities);
    }
  },
  async mounted() {
    await this.loadAvailableModels();
  },
  beforeUnmount() {
    // Cleanup chart instances
    this.chartInstances.forEach(chart => chart.dispose());
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await fetch('http://localhost:5000/api/models');
        const data = await response.json();
        
        if (data.success) {
          this.availableModels = data.models;
        } else {
          console.error('Failed to load models:', data.error);
        }
      } catch (error) {
        console.error('Error loading models:', error);
      }
    },
    
    toggleModelSelection(modelName) {
      const index = this.selectedModels.indexOf(modelName);
      if (index > -1) {
        this.selectedModels.splice(index, 1);
      } else {
        this.selectedModels.push(modelName);
      }
    },
    
    selectAllModels() {
      this.selectedModels = this.availableModels.map(model => model.name);
    },
    
    clearSelection() {
      this.selectedModels = [];
      this.comparisonData = [];
    },
    
    async loadComparisonData() {
      if (this.selectedModels.length === 0) return;
      
      this.loading = true;
      this.comparisonData = [];
      
      try {
        // Fetch all models first
        const response = await fetch('http://localhost:5000/api/models');
        const data = await response.json();
        
        if (data.success) {
          // Filter to only selected models and get their details
          this.comparisonData = data.models
            .filter(model => this.selectedModels.includes(model.name))
            .map(model => ({
              name: model.name,
              details: {
                architecture: model.architecture || 'Unknown',
                parameters: model.parameters || 'Unknown',
                context_length: model.context_length || 'Unknown',
                embedding_length: model.embedding_length || 'Unknown',
                quantization: model.quantization || 'Unknown',
                temperature: model.temperature || 'Unknown',
                top_p: model.top_p || 'Unknown',
                capabilities: model.capabilities || [],
                system_prompt: model.system_prompt || '',
                license: model.license || 'Unknown',
                modified: model.modified || 'Unknown',
                size: model.size || 'Unknown'
              }
            }));
          
          console.log('📊 Loaded comparison data:', this.comparisonData);
          
          // Initialize charts after data is loaded
          this.$nextTick(() => {
            this.initCharts();
          });
        } else {
          console.error('Failed to load models:', data.error);
        }
        
      } catch (error) {
        console.error('Error loading comparison data:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async refreshComparison() {
      await this.loadComparisonData();
    },
    
    exportComparison() {
      if (this.comparisonData.length === 0) return;
      
      const csvContent = this.generateCSV();
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `model-comparison-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    },
    
    generateCSV() {
      const headers = [
        'Model', 'Parameters', 'Context Length', 'Embedding Length', 'Quantization',
        'Temperature', 'Top P', 'Architecture', 'Capabilities'
      ];
      
      const rows = this.comparisonData.map(model => [
        model.name,
        model.details.parameters || 'Unknown',
        model.details.context_length || 'Unknown',
        model.details.embedding_length || 'Unknown',
        model.details.quantization || 'Unknown',
        model.details.temperature || 'Unknown',
        model.details.top_p || 'Unknown',
        model.details.architecture || 'Unknown',
        (model.details.capabilities || []).join('; ')
      ]);
      
      const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
      
      return csvContent;
    },
    
    viewModelDetails(model) {
      this.selectedModelDetails = model;
      console.log('📋 Viewing model details:', model);
    },
    
    getTotalParameters() {
      return this.comparisonData.reduce((total, model) => {
        const params = model.details.parameters;
        if (params && params.includes('B')) {
          const num = parseFloat(params);
          return total + (num * 1000000000); // Convert B to actual number
        }
        return total;
      }, 0);
    },
    
    getAvgContextLength() {
      const validLengths = this.comparisonData
        .map(model => parseInt(model.details.context_length))
        .filter(length => !isNaN(length));
      
      if (validLengths.length === 0) return 'Unknown';
      return Math.round(validLengths.reduce((a, b) => a + b, 0) / validLengths.length).toLocaleString();
    },
    
    initCharts() {
      this.createPerformanceChart();
      this.createCapabilitiesChart();
    },
    
    createPerformanceChart() {
      const canvas = this.$refs.performanceChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      // Set high DPI canvas
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      const modelNames = this.comparisonData.map(model => model.name);
      const contextLengths = this.comparisonData.map(model => {
        const length = parseInt(model.details.context_length);
        return isNaN(length) ? 0 : length;
      });
      
      const option = {
        title: {
          text: 'Context Length Comparison',
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: modelNames,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: 'Context Length'
        },
        series: [{
          name: 'Context Length',
          type: 'bar',
          data: contextLengths,
          itemStyle: {
            color: '#4e73df'
          }
        }]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    },
    
    createCapabilitiesChart() {
      const canvas = this.$refs.capabilitiesChart;
      if (!canvas || this.comparisonData.length < 2) return;
      
      // Set high DPI canvas
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      const chart = echarts.init(canvas, null, {
        renderer: 'canvas',
        useDirtyRect: false
      });
      
      // Count capabilities across all models
      const capabilityCount = {};
      this.comparisonData.forEach(model => {
        model.details.capabilities?.forEach(capability => {
          capabilityCount[capability] = (capabilityCount[capability] || 0) + 1;
        });
      });
      
      const data = Object.entries(capabilityCount).map(([capability, count]) => ({
        name: capability,
        value: count
      }));
      
      const option = {
        title: {
          text: 'Capabilities Distribution',
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [{
          name: 'Capabilities',
          type: 'pie',
          radius: '60%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
      
      chart.setOption(option);
      this.chartInstances.push(chart);
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: #666;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-col {
  display: flex;
  flex-direction: column;
}

.neumorphic-card {
  background: #f0f0f3;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 
    20px 20px 60px #bebebe,
    -20px -20px 60px #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.5rem;
}

.stats-icon.training {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.dataset {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.accuracy {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info h3 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.stats-info p {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.selection-controls,
.action-controls,
.table-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.model-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.model-selection-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-selection-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.model-selection-card.selected {
  border-color: #4e73df;
  background: linear-gradient(135deg, rgba(78, 115, 223, 0.1) 0%, rgba(78, 115, 223, 0.05) 100%);
}

.model-header-with-avatar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.model-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.model-avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color, #4e73df);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.model-avatar-placeholder .material-icons-round {
  font-size: 20px;
}

.model-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.model-size {
  font-size: 0.85rem;
  color: #666;
  margin: 0 0 0.5rem 0;
}

.model-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.capability-tag.large {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
}

.selection-indicator {
  color: #4e73df;
  font-size: 1.25rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
  border: 0.25rem solid #f3f3f3;
  border-top: 0.25rem solid #4e73df;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.comparison-summary {
  padding: 1rem;
}

.comparison-summary h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item .label {
  color: #666;
  font-size: 0.9rem;
}

.summary-item .value {
  color: #333;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty-state .material-icons-round {
  font-size: 3rem;
  color: #ccc;
  margin-bottom: 1rem;
}

.comparison-table-card {
  margin-top: 1.5rem;
}

.table-container {
  overflow-x: auto;
  border-radius: 12px;
  background: white;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.comparison-table th {
  background: #f8f9fa;
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
}

.comparison-table td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: top;
}

.comparison-table tr:hover {
  background: #f8f9fa;
}

.model-name-cell {
  min-width: 150px;
}

.model-name-with-avatar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.model-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.avatar-image-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.model-avatar-placeholder-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary-color, #4e73df);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.model-avatar-placeholder-small .material-icons-round {
  font-size: 12px;
}

.model-name-text {
  flex: 1;
}

.model-name strong {
  color: #333;
  font-size: 0.95rem;
}

.model-name small {
  color: #666;
  display: block;
  margin-top: 0.25rem;
}

.capabilities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.capability-badge {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
}

.chart-container {
  height: 300px;
  position: relative;
  margin: 0 -1rem -1rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 8px;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
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
}

.model-details-modal {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
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
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #4e73df;
  color: white;
}

.btn-primary:hover {
  background: #3c5bd1;
}

.btn-outline-primary {
  background: transparent;
  color: #4e73df;
  border: 1px solid #4e73df;
}

.btn-outline-primary:hover {
  background: #4e73df;
  color: white;
}

.btn-outline-secondary {
  background: transparent;
  color: #666;
  border: 1px solid #ddd;
}

.btn-outline-secondary:hover {
  background: #666;
  color: white;
}

.btn-outline-success {
  background: transparent;
  color: #28a745;
  border: 1px solid #28a745;
}

.btn-outline-success:hover {
  background: #28a745;
  color: white;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1rem;
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