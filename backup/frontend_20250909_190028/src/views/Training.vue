<template>
  <div class="training-container">
    <div class="page-header">
      <div>
        <h1>Model Training</h1>
        <p>Train and fine-tune your AI models</p>
      </div>
      <button class="btn btn-primary" @click="startNewTraining">
        <i>⚡</i> New Training
      </button>
    </div>

    <!-- Training Jobs -->
    <div class="training-jobs">
      <div class="section-header">
        <h2>Training Jobs</h2>
      </div>

      <div class="jobs-grid">
        <div v-for="job in trainingJobs" :key="job.id" class="job-card">
          <div class="job-header">
            <h3>{{ job.modelName }}</h3>
            <span class="job-status" :class="job.status.toLowerCase()">
              {{ job.status }}
            </span>
          </div>
          <div class="job-details">
            <p>{{ job.datasetName }}</p>
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: job.progress + '%' }"></div>
            </div>
            <div class="job-meta">
              <span>Epoch {{ job.currentEpoch }}/{{ job.totalEpochs }}</span>
              <span>{{ formatDuration(job.elapsedTime) }}</span>
            </div>
          </div>
          <div class="job-actions">
            <button class="btn-icon" @click="viewJobDetails(job)">👁️</button>
            <button class="btn-icon" @click="stopJob(job.id)" v-if="job.status === 'RUNNING'">⏹️</button>
            <button class="btn-icon" @click="deleteJob(job.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingView',
  data() {
    return {
      trainingJobs: [
        {
          id: 'job-1',
          modelName: 'Sentiment Analysis',
          datasetName: 'IMDB Reviews (50K samples)',
          status: 'RUNNING',
          progress: 65,
          currentEpoch: 13,
          totalEpochs: 20,
          elapsedTime: 3560,
          metrics: {
            accuracy: 87.3,
            loss: 0.3421
          }
        },
        {
          id: 'job-2',
          modelName: 'Image Classifier',
          datasetName: 'CIFAR-10 (60K images)',
          status: 'COMPLETED',
          progress: 100,
          currentEpoch: 50,
          totalEpochs: 50,
          elapsedTime: 12450,
          metrics: {
            accuracy: 92.8,
            loss: 0.2156
          }
        },
        {
          id: 'job-3',
          modelName: 'Text Summarization',
          datasetName: 'CNN/Daily Mail',
          status: 'FAILED',
          progress: 42,
          currentEpoch: 8,
          totalEpochs: 20,
          elapsedTime: 24500,
          error: 'CUDA out of memory'
        }
      ]
    };
  },
  methods: {
    formatDuration(seconds) {
      if (!seconds) return '--';
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      return h > 0 ? `${h}h ${m}m` : `${m}m`;
    },
    startNewTraining() {
      // In a real app, this would open a new training form
      alert('New training form would open here');
    },
    viewJobDetails(job) {
      // In a real app, this would show detailed job info
      alert(`Viewing details for job: ${job.modelName}`);
    },
    stopJob(jobId) {
      if (confirm('Stop this training job?')) {
        const job = this.trainingJobs.find(j => j.id === jobId);
        if (job) job.status = 'STOPPED';
      }
    },
    deleteJob(jobId) {
      if (confirm('Delete this training job?')) {
        this.trainingJobs = this.trainingJobs.filter(job => job.id !== jobId);
      }
    }
  }
};
</script>

<style scoped>
.training-container {
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

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.job-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.job-card:hover {
  transform: translateY(-3px);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.job-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.job-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.job-status.running {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
}

.job-status.completed {
  background: rgba(28, 200, 138, 0.1);
  color: var(--success);
}

.job-status.failed {
  background: rgba(231, 74, 59, 0.1);
  color: var(--danger);
}

.job-status.stopped {
  background: rgba(246, 194, 62, 0.1);
  color: var(--warning);
}

.job-details {
  margin-bottom: 1rem;
}

.job-details p {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.9rem;
}

.progress-container {
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.job-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--secondary);
}

.job-actions {
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
</style>
