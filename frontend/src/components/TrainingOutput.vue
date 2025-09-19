<template>
  <div class="training-output-section">
    <!-- Job Card with Integrated Progress -->
    <div v-if="currentJob" class="job-card">
      <div class="job-header">
        <h3>{{ currentJob.name }}</h3>
        <span class="job-status" :class="getStatusClass(currentJob.status)">{{ getStatusText(currentJob.status) }}</span>
      </div>
      
      <!-- Progress Status Inside Card -->
      <div class="progress-status">
        <div v-if="currentJob.status === 'RUNNING'" class="loading-status">
          <div class="loading-spinner"></div>
          <span>Training in progress...</span>
        </div>
        
        <div v-else-if="currentJob.status === 'FAILED'" class="error-status">
          <span class="error-icon">❌</span>
          <span>Training failed</span>
          <div class="error-details">
            <p><strong>Error:</strong> {{ currentJob.errorMessage || 'Unknown error occurred' }}</p>
            <p v-if="currentJob.progress > 0" class="progress-info">
              <strong>Progress:</strong> {{ Math.round(currentJob.progress * 100) }}% completed before failure
            </p>
            <p class="retry-suggestion">
              <strong>Suggestions:</strong> Check dataset format, ensure base model exists, or try with different parameters
            </p>
          </div>
        </div>
        
        <div v-else-if="currentJob.status === 'COMPLETED'" class="success-status">
          <span class="success-icon">✅</span>
          <span>Training completed successfully!</span>
        </div>
        
        <div v-else class="idle-status">
          <span class="idle-icon">⏸️</span>
          <span>Ready to start</span>
        </div>
      </div>
      
      <div class="job-info">
        <p class="job-description">{{ currentJob.description || 'No description provided' }}</p>
        <div class="job-capabilities">
          <span v-for="capability in currentJob.capabilities" :key="capability" class="capability-tag">
            {{ capability }}
          </span>
        </div>
        <p class="dataset-info">{{ currentJob.datasetName }}</p>
        <div class="job-meta">
          <span>{{ formatDuration(currentJob.elapsedTime) }}</span>
        </div>
      </div>
    </div>

    <!-- No Job Message -->
    <div v-else class="no-job-message">
      <div class="idle-icon">⏸️</div>
      <p>No training job selected</p>
      <p class="idle-details">Start a training job to see progress here</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingOutput',
  props: {
    currentJob: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      statusPollingInterval: null,
      lastStatus: null
    }
  },
  watch: {
    currentJob: {
      handler(newJob) {
        if (newJob) {
          this.startStatusPolling();
          this.lastStatus = newJob.status;
        } else {
          this.stopStatusPolling();
        }
      },
      immediate: true
    }
  },
  beforeUnmount() {
    this.stopStatusPolling();
  },
  methods: {
    startStatusPolling() {
      if (!this.currentJob || this.currentJob.status === 'COMPLETED' || this.currentJob.status === 'FAILED') {
        return; // Don't poll for completed/failed jobs
      }
      
      this.statusPollingInterval = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/training-jobs/${this.currentJob.id}/status`);
          const result = await response.json();
          
          if (result.success && result.status) {
            const newStatus = result.status.status;
            
            // Only emit if status changed (RUNNING -> FAILED/COMPLETED)
            if (newStatus !== this.lastStatus) {
              this.lastStatus = newStatus;
              
              // Emit status change to parent component
              this.$emit('status-changed', {
                jobId: this.currentJob.id,
                newStatus: newStatus,
                jobData: result.status
              });
              
              // Stop polling once status changes to final state
              this.stopStatusPolling();
            }
          }
        } catch (error) {
          console.error('Error polling job status:', error);
        }
      }, 3000); // Poll every 3 seconds - only for status changes, not progress
    },
    
    stopStatusPolling() {
      if (this.statusPollingInterval) {
        clearInterval(this.statusPollingInterval);
        this.statusPollingInterval = null;
      }
    },
    
    getStatusClass(status) {
      switch (status) {
        case 'RUNNING':
          return 'running';
        case 'COMPLETED':
          return 'completed';
        case 'FAILED':
          return 'failed';
        case 'PENDING':
          return 'pending';
        default:
          return 'unknown';
      }
    },
    
    getStatusText(status) {
      switch (status) {
        case 'RUNNING':
          return 'Loading...';
        case 'COMPLETED':
          return 'Done';
        case 'FAILED':
          return 'Error';
        case 'PENDING':
          return 'Pending';
        default:
          return status;
      }
    },
    
    formatDuration(seconds) {
      if (!seconds) return '0s';
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
      } else {
        return `${secs}s`;
      }
    }
  }
}
</script>

<style scoped>
.training-output-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--card-shadow);
}

.job-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.job-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.job-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.job-status.running {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.job-status.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.job-status.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.job-status.pending {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
  border: 1px solid rgba(156, 163, 175, 0.2);
}

.job-info {
  color: var(--text-secondary);
}

.job-description {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

.job-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.capability-tag {
  background: var(--accent-bg);
  color: var(--accent-text);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.dataset-info {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

.job-meta {
  display: flex;
  gap: 16px;
  font-size: 0.875rem;
  color: var(--text-tertiary);
}

.progress-status {
  margin: 16px 0;
  padding: 16px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
}

.loading-status {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-status span {
  font-size: 0.95rem;
  font-weight: 500;
}

.error-status {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}

.error-icon {
  font-size: 1.2rem;
}

.error-status span {
  font-size: 0.95rem;
  font-weight: 500;
}

.error-details {
  margin: 8px 0 0 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.error-details p {
  margin: 6px 0;
}

.error-details strong {
  color: var(--text-primary);
  font-weight: 600;
}

.progress-info {
  color: var(--warning-color, #f59e0b);
}

.retry-suggestion {
  color: var(--info-color, #3b82f6);
  font-size: 0.8rem;
  margin-top: 8px;
}

.success-status {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}

.success-icon {
  font-size: 1.2rem;
}

.success-status span {
  font-size: 0.95rem;
  font-weight: 500;
}

.idle-status {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}

.idle-icon {
  font-size: 1.2rem;
}

.idle-status span {
  font-size: 0.95rem;
  font-weight: 500;
}

.no-job-message {
  text-align: center;
  padding: 40px 20px;
  border-radius: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.no-job-message .idle-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.no-job-message p {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.idle-details {
  font-size: 0.9rem;
  color: var(--text-tertiary);
}
</style>