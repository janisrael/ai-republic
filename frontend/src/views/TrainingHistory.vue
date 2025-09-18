<template>
  <div class="training-history">
    <div class="page-header">
      <h1>Training History</h1>
      <p>Comprehensive view of all training jobs and their detailed information</p>
    </div>

    <!-- Statistics Overview -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_jobs }}</div>
          <div class="stat-label">Total Jobs</div>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completed_jobs }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      <div class="stat-card error">
        <div class="stat-icon">❌</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.failed_jobs }}</div>
          <div class="stat-label">Failed</div>
        </div>
      </div>
      <div class="stat-card running">
        <div class="stat-icon">🔄</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.running_jobs }}</div>
          <div class="stat-label">Running</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Status:</label>
        <select v-model="filters.status" @change="applyFilters">
          <option value="">All Status</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="RUNNING">Running</option>
          <option value="PENDING">Pending</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Training Type:</label>
        <select v-model="filters.training_type" @change="applyFilters">
          <option value="">All Types</option>
          <option value="LoRA">LoRA</option>
          <option value="RAG">RAG</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search:</label>
        <input 
          type="text" 
          v-model="filters.search" 
          @input="applyFilters"
          placeholder="Search by model name or description..."
        />
      </div>
    </div>

    <!-- Training Jobs List -->
    <div class="training-jobs-list">
      <div 
        v-for="job in filteredJobs" 
        :key="job.id" 
        class="job-card"
        :class="getJobStatusClass(job.status)"
        @click="selectJob(job)"
      >
        <div class="job-header">
          <div class="job-title">
            <h3>{{ job.name }}</h3>
            <span class="job-type">{{ job.training_type }}</span>
          </div>
          <div class="job-status">
            <span class="status-badge" :class="getStatusClass(job.status)">
              {{ job.status }}
            </span>
            <div class="job-date">{{ formatDate(job.created_at) }}</div>
          </div>
        </div>

        <div class="job-content">
          <div class="job-info">
            <div class="info-item">
              <span class="label">Model:</span>
              <span class="value">{{ job.model_name }}</span>
            </div>
            <div class="info-item" v-if="job.base_model">
              <span class="label">Base Model:</span>
              <span class="value">{{ job.base_model }}</span>
            </div>
            <div class="info-item" v-if="job.dataset">
              <span class="label">Dataset:</span>
              <span class="value">{{ job.dataset.name }} ({{ job.dataset.sample_count }} samples)</span>
            </div>
            <div class="info-item" v-if="job.duration">
              <span class="label">Duration:</span>
              <span class="value">{{ job.duration.formatted }}</span>
            </div>
          </div>

          <div class="job-progress" v-if="job.status === 'RUNNING'">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (job.progress * 100) + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ Math.round(job.progress * 100) }}%</span>
          </div>

          <div class="job-error" v-if="job.status === 'FAILED' && job.error_message">
            <div class="error-message">{{ job.error_message }}</div>
          </div>
        </div>

        <div class="job-actions">
          <button 
            class="btn btn-primary" 
            @click.stop="viewDetails(job)"
          >
            View Details
          </button>
          <button 
            class="btn btn-secondary" 
            @click.stop="restartJob(job)"
            v-if="job.status === 'FAILED'"
          >
            Restart
          </button>
        </div>
      </div>
    </div>

    <!-- Job Details Modal -->
    <div v-if="selectedJob" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedJob.name }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Basic Information -->
          <div class="details-section">
            <h3>Basic Information</h3>
            <div class="details-grid">
              <div class="detail-item">
                <span class="label">Status:</span>
                <span class="value" :class="getStatusClass(selectedJob.status)">
                  {{ selectedJob.status }}
                </span>
              </div>
              <div class="detail-item">
                <span class="label">Training Type:</span>
                <span class="value">{{ selectedJob.training_type }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Model Name:</span>
                <span class="value">{{ selectedJob.model_name }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.base_model">
                <span class="label">Base Model:</span>
                <span class="value">{{ selectedJob.base_model }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Created:</span>
                <span class="value">{{ formatDateTime(selectedJob.created_at) }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.started_at">
                <span class="label">Started:</span>
                <span class="value">{{ formatDateTime(selectedJob.started_at) }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.completed_at">
                <span class="label">Completed:</span>
                <span class="value">{{ formatDateTime(selectedJob.completed_at) }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.duration">
                <span class="label">Duration:</span>
                <span class="value">{{ selectedJob.duration.formatted }}</span>
              </div>
            </div>
          </div>

          <!-- Dataset Information -->
          <div class="details-section" v-if="selectedJob.dataset">
            <h3>Dataset Information</h3>
            <div class="details-grid">
              <div class="detail-item">
                <span class="label">Dataset Name:</span>
                <span class="value">{{ selectedJob.dataset.name }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Description:</span>
                <span class="value">{{ selectedJob.dataset.description || 'No description' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Samples Used:</span>
                <span class="value">{{ selectedJob.dataset.sample_count }} / {{ selectedJob.dataset.total_samples }}</span>
              </div>
            </div>
          </div>

          <!-- Training Parameters -->
          <div class="details-section" v-if="selectedJob.training_parameters">
            <h3>Training Parameters</h3>
            <div class="details-grid">
              <div class="detail-item" v-if="selectedJob.training_parameters.epochs !== 'N/A'">
                <span class="label">Epochs:</span>
                <span class="value">{{ selectedJob.training_parameters.epochs }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.training_parameters.learning_rate !== 'N/A'">
                <span class="label">Learning Rate:</span>
                <span class="value">{{ selectedJob.training_parameters.learning_rate }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.training_parameters.batch_size !== 'N/A'">
                <span class="label">Batch Size:</span>
                <span class="value">{{ selectedJob.training_parameters.batch_size }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.training_parameters.lora_rank !== 'N/A'">
                <span class="label">LoRA Rank:</span>
                <span class="value">{{ selectedJob.training_parameters.lora_rank }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.training_parameters.lora_alpha !== 'N/A'">
                <span class="label">LoRA Alpha:</span>
                <span class="value">{{ selectedJob.training_parameters.lora_alpha }}</span>
              </div>
            </div>
          </div>

          <!-- Performance Metrics -->
          <div class="details-section" v-if="selectedJob.performance">
            <h3>Performance Metrics</h3>
            <div class="details-grid">
              <div class="detail-item" v-if="selectedJob.performance.final_loss">
                <span class="label">Final Loss:</span>
                <span class="value">{{ selectedJob.performance.final_loss }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.performance.best_loss">
                <span class="label">Best Loss:</span>
                <span class="value">{{ selectedJob.performance.best_loss }}</span>
              </div>
              <div class="detail-item" v-if="selectedJob.performance.convergence_epoch">
                <span class="label">Convergence Epoch:</span>
                <span class="value">{{ selectedJob.performance.convergence_epoch }}</span>
              </div>
            </div>
          </div>

          <!-- Error Information -->
          <div class="details-section" v-if="selectedJob.status === 'FAILED' && selectedJob.error_message">
            <h3>Error Information</h3>
            <div class="error-details">
              <pre>{{ selectedJob.error_message }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingHistory',
  data() {
    return {
      trainingJobs: [],
      filteredJobs: [],
      selectedJob: null,
      stats: {
        total_jobs: 0,
        completed_jobs: 0,
        failed_jobs: 0,
        running_jobs: 0
      },
      filters: {
        status: '',
        training_type: '',
        search: ''
      },
      loading: false
    }
  },
  async mounted() {
    await this.loadTrainingHistory()
  },
  methods: {
    async loadTrainingHistory() {
      try {
        this.loading = true
        const response = await fetch('/api/training-history')
        const data = await response.json()
        
        if (data.success) {
          this.trainingJobs = data.history
          this.filteredJobs = [...this.trainingJobs]
          this.stats = {
            total_jobs: data.total_jobs,
            completed_jobs: data.completed_jobs,
            failed_jobs: data.failed_jobs,
            running_jobs: data.running_jobs
          }
        } else {
          console.error('Failed to load training history:', data.error)
        }
      } catch (error) {
        console.error('Error loading training history:', error)
      } finally {
        this.loading = false
      }
    },
    
    applyFilters() {
      this.filteredJobs = this.trainingJobs.filter(job => {
        const matchesStatus = !this.filters.status || job.status === this.filters.status
        const matchesType = !this.filters.training_type || job.training_type === this.filters.training_type
        const matchesSearch = !this.filters.search || 
          job.name.toLowerCase().includes(this.filters.search.toLowerCase()) ||
          job.description.toLowerCase().includes(this.filters.search.toLowerCase()) ||
          job.model_name.toLowerCase().includes(this.filters.search.toLowerCase())
        
        return matchesStatus && matchesType && matchesSearch
      })
    },
    
    selectJob(job) {
      this.selectedJob = job
    },
    
    closeModal() {
      this.selectedJob = null
    },
    
    viewDetails(job) {
      this.selectedJob = job
    },
    
    async restartJob(job) {
      try {
        const response = await fetch(`/api/training-jobs/${job.id}/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        if (data.success) {
          alert('Job restarted successfully!')
          await this.loadTrainingHistory()
        } else {
          alert('Failed to restart job: ' + data.error)
        }
      } catch (error) {
        console.error('Error restarting job:', error)
        alert('Error restarting job: ' + error.message)
      }
    },
    
    getJobStatusClass(status) {
      return {
        'job-completed': status === 'COMPLETED',
        'job-failed': status === 'FAILED',
        'job-running': status === 'RUNNING',
        'job-pending': status === 'PENDING'
      }
    },
    
    getStatusClass(status) {
      return {
        'status-completed': status === 'COMPLETED',
        'status-failed': status === 'FAILED',
        'status-running': status === 'RUNNING',
        'status-pending': status === 'PENDING'
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString()
    }
  }
}
</script>

<style scoped>
.training-history {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.page-header p {
  color: #666;
  font-size: 1.1rem;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-card.success {
  border-left: 4px solid #10b981;
}

.stat-card.error {
  border-left: 4px solid #ef4444;
}

.stat-card.running {
  border-left: 4px solid #3b82f6;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #333;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.training-jobs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.job-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #ddd;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.job-completed {
  border-left-color: #10b981;
}

.job-failed {
  border-left-color: #ef4444;
}

.job-running {
  border-left-color: #3b82f6;
}

.job-pending {
  border-left-color: #f59e0b;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.job-title h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.job-type {
  background: #e5e7eb;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.job-status {
  text-align: right;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-running {
  background: #dbeafe;
  color: #1e40af;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.job-date {
  color: #666;
  font-size: 0.9rem;
}

.job-content {
  margin-bottom: 1rem;
}

.job-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  gap: 0.5rem;
}

.info-item .label {
  font-weight: 600;
  color: #666;
}

.info-item .value {
  color: #333;
}

.job-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: #666;
  min-width: 40px;
}

.job-error {
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #991b1b;
  font-size: 0.9rem;
}

.job-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
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

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  margin: 1rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.details-section {
  margin-bottom: 2rem;
}

.details-section h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.2rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item .label {
  font-weight: 600;
  color: #666;
  font-size: 0.9rem;
}

.detail-item .value {
  color: #333;
  font-size: 1rem;
}

.error-details {
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 1rem;
}

.error-details pre {
  margin: 0;
  color: #991b1b;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 768px) {
  .training-history {
    padding: 1rem;
  }
  
  .filters-section {
    flex-direction: column;
    gap: 1rem;
  }
  
  .job-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .job-status {
    text-align: left;
  }
  
  .job-info {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
