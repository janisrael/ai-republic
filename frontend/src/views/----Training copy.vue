<template>
  <div class="training-container">
    <div class="page-header">
      <div>
        <h1>Model Training</h1>
        <p>Train and fine-tune your AI models</p>
      </div>
      <button class="btn btn-primary" @click="startNewTraining">
        <Icon name="play_arrow" size="sm" color="light" />
        New Training
      </button>
    </div>

    <!-- Training Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="model_training" size="lg" color="primary" />
        </div>
        <div class="card-content">
          <h3>{{ trainingJobs.length }}</h3>
          <p>Total Jobs</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="play_arrow" size="lg" color="success" />
        </div>
        <div class="card-content">
          <h3>{{ runningJobsCount }}</h3>
          <p>Running</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="check_circle" size="lg" color="success" />
        </div>
        <div class="card-content">
          <h3>{{ completedJobsCount }}</h3>
          <p>Completed</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="error" size="lg" color="danger" />
        </div>
        <div class="card-content">
          <h3>{{ failedJobsCount }}</h3>
          <p>Failed</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="storage" size="lg" color="info" />
        </div>
        <div class="card-content">
          <h3>{{ chromadbCollections }}</h3>
          <p>ChromaDB Collections</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="smart_toy" size="lg" color="info" />
        </div>
        <div class="card-content">
          <h3>{{ ollamaModels.length }}</h3>
          <p>Available Models</p>
        </div>
      </div>
      <div class="summary-card">
        <div class="card-icon">
          <Icon name="dataset" size="lg" color="warning" />
        </div>
        <div class="card-content">
          <h3>{{ availableDatasets.length }}</h3>
          <p>Datasets</p>
        </div>
      </div>
    </div>

    <!-- Available Models Overview -->
    <div class="capabilities-overview">
      <div class="section-header">
        <h2>Available Models</h2>
        <p v-if="ollamaModels.length === 0" class="no-models-message">
          No Ollama models found. Install some models to get started!
        </p>
      </div>
      <div class="capabilities-grid">
        <div v-for="model in ollamaModels" :key="model.name" class="capability-card">
          <div class="capability-icon">
            <Icon :name="getModelIcon(model.capabilities)" size="lg" :color="getModelColor(model.capabilities)" />
          </div>
          <h3>{{ model.name }}</h3>
          <p>{{ getModelDescription(model.capabilities) }}</p>
          <div class="model-info">
            <span class="model-size">{{ model.size }}</span>
            <span class="model-modified">{{ model.modified }}</span>
          </div>
          <div class="capability-models">
            <span v-for="capability in model.capabilities" :key="capability" class="model-tag">
              {{ capability }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Training Jobs -->
    <div class="training-jobs">
      <div class="section-header">
        <h2>Training Jobs</h2>
      </div>

      <div class="jobs-grid">
        <div v-for="job in trainingJobs" :key="job.id" class="job-card">
          <div class="job-header">
            <h3>{{ getJobDisplayName(job) }}</h3>
            <span class="job-status" :class="job.status.toLowerCase()">
              {{ job.status }}
            </span>
          </div>
          <div class="job-details">
            <div class="job-metadata" v-if="job.description || job.jobType || job.maker || job.version || job.baseModel">
              <div class="metadata-row" v-if="job.baseModel">
                <span class="metadata-label">Base Model:</span>
                <span class="metadata-value">{{ job.baseModel }}</span>
              </div>
              <div class="metadata-row" v-if="job.description">
                <span class="metadata-label">Description:</span>
                <span class="metadata-value">{{ job.description }}</span>
              </div>
              <div class="metadata-row" v-if="job.jobType">
                <span class="metadata-label">Type:</span>
                <span class="metadata-value">{{ job.jobType }}</span>
              </div>
              <div class="metadata-row" v-if="job.maker">
                <span class="metadata-label">Maker:</span>
                <span class="metadata-value">{{ job.maker }}</span>
              </div>
              <div class="metadata-row" v-if="job.version">
                <span class="metadata-label">Version:</span>
                <span class="metadata-value">{{ job.version }}</span>
              </div>
              <div class="metadata-row" v-if="job.modelName">
                <span class="metadata-label">Output Model:</span>
                <span class="metadata-value model-file">{{ job.modelName }}</span>
              </div>
            </div>
            <p class="job-description">{{ job.description || 'No description provided' }}</p>
            <div class="job-capabilities">
              <span v-for="capability in job.capabilities" :key="capability" class="capability-tag">
                {{ capability }}
              </span>
            </div>
            <p class="dataset-info">{{ job.datasetName }}</p>
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: job.progress + '%' }"></div>
            </div>
            <div class="job-meta">
              <span v-if="job.currentStep && job.totalSteps">
                Step {{ job.currentStep }}/{{ job.totalSteps }}
              </span>
              <span v-else-if="job.currentEpoch && job.totalEpochs">
                Epoch {{ job.currentEpoch }}/{{ job.totalEpochs }}
              </span>
              <span>{{ formatDuration(job.elapsedTime) }}</span>
            </div>
            <div class="job-metrics" v-if="job.metrics">
              <div class="metric-item">
                <span class="metric-label">Accuracy:</span>
                <span class="metric-value">{{ job.metrics.accuracy }}%</span>
              </div>
              <div class="metric-item" v-if="job.metrics.debuggingScore">
                <span class="metric-label">Debugging:</span>
                <span class="metric-value">{{ job.metrics.debuggingScore }}%</span>
              </div>
              <div class="metric-item" v-if="job.metrics.reasoningScore">
                <span class="metric-label">Reasoning:</span>
                <span class="metric-value">{{ job.metrics.reasoningScore }}%</span>
              </div>
              <div class="metric-item" v-if="job.metrics.codeGenScore">
                <span class="metric-label">Code Gen:</span>
                <span class="metric-value">{{ job.metrics.codeGenScore }}%</span>
              </div>
              <div class="metric-item" v-if="job.metrics.planningScore">
                <span class="metric-label">Planning:</span>
                <span class="metric-value">{{ job.metrics.planningScore }}%</span>
              </div>
            </div>
          </div>
          <div class="job-actions">
            <button class="btn-icon" @click="viewJobDetails(job)">👁️</button>
            <button class="btn-icon btn-start" @click="startTraining(job.id)" v-if="job.status === 'PENDING'">▶️</button>
            <button class="btn-icon btn-stop" @click="stopTraining(job.id)" v-if="job.status === 'RUNNING'">⏹️</button>
            <button class="btn-icon" @click="deleteJob(job.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- New Training Modal -->
    <div v-if="showTrainingModal" class="modal-overlay" @click.self="showTrainingModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Start New AI Training</h2>
          <button class="btn-icon" @click="showTrainingModal = false">✕</button>
        </div>
        
        <div class="modal-body">
          <!-- Training Job Metadata -->
          <div class="training-metadata">
            <h3>Training Job Information</h3>
            <div class="metadata-grid">
              <div class="form-group">
                <label>Job Name <span class="required">*</span></label>
                <input 
                  type="text" 
                  v-model="newTraining.jobName" 
                  placeholder="e.g., My Custom AI Assistant"
                  class="form-control"
                  required
                >
                <small>Give your training job a descriptive name</small>
              </div>
              
              <div class="form-group">
                <label>Description</label>
                <textarea 
                  v-model="newTraining.description" 
                  placeholder="Describe what this training job will accomplish..."
                  class="form-control"
                  rows="2"
                ></textarea>
                <small>Optional description of the training purpose</small>
              </div>
              
              <div class="form-group">
                <label>Job Type</label>
                <select v-model="newTraining.jobType" class="form-control">
                  <option value="experimental">Experimental</option>
                  <option value="production">Production</option>
                  <option value="research">Research</option>
                  <option value="personal">Personal</option>
                  <option value="demo">Demo</option>
                </select>
                <small>Category for organizing your training jobs</small>
              </div>
              
              <div class="form-group">
                <label>Maker/Creator</label>
                <input 
                  type="text" 
                  v-model="newTraining.maker" 
                  placeholder="e.g., swordfish, Agimat Team"
                  class="form-control"
                >
                <small>Who is creating this training job</small>
              </div>
              
              <div class="form-group">
                <label>Version</label>
                <input 
                  type="text" 
                  v-model="newTraining.version" 
                  placeholder="e.g., v1.0, 2.1.3, beta"
                  class="form-control"
                >
                <small>Version identifier for this training job</small>
              </div>
            </div>
          </div>

          <!-- Training Type Selection -->
          <div class="form-group">
            <label>Training Type</label>
            <div class="training-types">
              <label class="training-type-card" :class="{ active: newTraining.type === 'lora' }">
                <input type="radio" v-model="newTraining.type" value="lora" hidden>
                <div class="type-icon">🎯</div>
                <h4>LoRA Fine-tuning</h4>
                <p>Train custom roles/personas with minimal resources</p>
              </label>
              
              <label class="training-type-card" :class="{ active: newTraining.type === 'rag' }">
                <input type="radio" v-model="newTraining.type" value="rag" hidden>
                <div class="type-icon">📚</div>
                <h4>RAG System</h4>
                <p>Build knowledge retrieval system</p>
              </label>
              
              <label class="training-type-card" :class="{ active: newTraining.type === 'full' }">
                <input type="radio" v-model="newTraining.type" value="full" hidden>
                <div class="type-icon">🚀</div>
                <h4>Full Fine-tuning</h4>
                <p>Complete model training (requires more resources)</p>
              </label>
            </div>
          </div>

          <!-- Model Selection -->
          <div class="form-group">
            <label>Base Model</label>
            <select v-model="newTraining.baseModel" class="form-control">
              <option value="">Select base model</option>
              <option v-for="model in ollamaModels" :key="model.name" :value="model.name">
                {{ getModelDisplayOption(model) }}
              </option>
            </select>
          </div>

          <!-- Training Configuration -->
          <div v-if="newTraining.type === 'lora'" class="lora-config">
            <h3>LoRA Configuration</h3>
            <div class="config-grid">
              <div class="form-group">
                <label>Rank (r)</label>
                <input type="number" v-model="newTraining.loraConfig.rank" min="1" max="64" class="form-control">
                <small>Higher rank = more parameters, better performance</small>
              </div>
              <div class="form-group">
                <label>Alpha</label>
                <input type="number" v-model="newTraining.loraConfig.alpha" min="1" max="128" class="form-control">
                <small>Scaling factor for LoRA weights</small>
              </div>
              <div class="form-group">
                <label>Dropout</label>
                <input type="number" v-model="newTraining.loraConfig.dropout" min="0" max="0.5" step="0.01" class="form-control">
                <small>Prevent overfitting</small>
              </div>
            </div>
          </div>

          <!-- Dataset Selection -->
          <div class="form-group">
            <label>Training Datasets <small>(Select multiple for combined training)</small></label>
            <div class="dataset-options">
              <!-- Existing Datasets -->
              <label class="dataset-option" v-for="dataset in availableDatasets" :key="dataset.id">
                <input type="checkbox" v-model="newTraining.selectedDatasets" :value="dataset.id" hidden>
                <div class="option-card">
                  <Icon name="dataset" size="sm" color="primary" />
                  <div class="dataset-info">
                    <span class="dataset-name">{{ dataset.name }}</span>
                    <span class="dataset-details">{{ dataset.sampleCount.toLocaleString() }} samples • {{ dataset.type }}</span>
                  </div>
                  <div class="dataset-actions">
                    <Icon name="info" size="xs" color="muted" class="info-icon" 
                          @click.stop="showDatasetInfo(dataset)" />
                  </div>
                </div>
              </label>
              
              <!-- Upload JSONL -->
              <label class="dataset-option">
                <input type="checkbox" v-model="newTraining.datasetType" value="upload" hidden>
                <div class="option-card">
                  <Icon name="upload" size="sm" color="success" />
                  <span>Upload JSONL File</span>
                </div>
              </label>
              
              <!-- Create Knowledge Base -->
              <label class="dataset-option">
                <input type="checkbox" v-model="newTraining.datasetType" value="create" hidden>
                <div class="option-card">
                  <Icon name="add" size="sm" color="info" />
                  <span>Create Knowledge Base</span>
                </div>
              </label>
            </div>
            
            <!-- Selected Datasets Summary -->
            <div v-if="newTraining.selectedDatasets.length > 0" class="selected-datasets">
              <h4>Selected Datasets ({{ newTraining.selectedDatasets.length }})</h4>
              <div class="selected-list">
                <div v-for="datasetId in newTraining.selectedDatasets" :key="datasetId" class="selected-item">
                  <span class="dataset-name">{{ getDatasetName(datasetId) }}</span>
                  <span class="dataset-samples">{{ getDatasetSamples(datasetId).toLocaleString() }} samples</span>
                  <button class="btn-icon" @click="removeDataset(datasetId)">
                    <Icon name="close" size="xs" color="danger" />
                  </button>
                </div>
              </div>
              <div class="training-strategy">
                <label>Training Strategy:</label>
                <select v-model="newTraining.trainingStrategy" class="form-control">
                  <option value="concatenate">Concatenate (Combine all datasets)</option>
                  <option value="mix">Mix (Interleave samples)</option>
                  <option value="multitask">Multi-task (Separate tasks)</option>
                </select>
                <small>
                  <span v-if="newTraining.trainingStrategy === 'concatenate'">All datasets combined into one large training set</span>
                  <span v-if="newTraining.trainingStrategy === 'mix'">Samples from different datasets mixed during training</span>
                  <span v-if="newTraining.trainingStrategy === 'multitask'">Different datasets trained as separate tasks</span>
                </small>
              </div>
            </div>
          </div>

          <!-- Role Definition -->
          <div v-if="newTraining.type === 'lora'" class="form-group">
            <label>Role Definition</label>
            <textarea 
              v-model="newTraining.roleDefinition" 
              placeholder="You are Agimat, an advanced AI assistant specialized in debugging and code analysis..."
              class="form-control"
              rows="4"
            ></textarea>
            <small>Define the AI's personality, role, and behavior</small>
          </div>

          <!-- Training Parameters -->
          <div class="training-params">
            <h3>Training Parameters</h3>
            <div class="params-grid">
              <div class="form-group">
                <label>Learning Rate</label>
                <input type="number" v-model="newTraining.params.learningRate" step="0.0001" class="form-control">
              </div>
              <div class="form-group">
                <label>Batch Size</label>
                <input type="number" v-model="newTraining.params.batchSize" min="1" max="32" class="form-control">
              </div>
              <div class="form-group">
                <label>Epochs</label>
                <input type="number" v-model="newTraining.params.epochs" min="1" max="100" class="form-control">
              </div>
              <div class="form-group">
                <label>Max Steps</label>
                <input type="number" v-model="newTraining.params.maxSteps" min="100" max="10000" class="form-control">
              </div>
            </div>
          </div>

          <!-- RAG Configuration -->
          <div v-if="newTraining.type === 'rag'" class="rag-config">
            <h3>RAG Configuration</h3>
            <div class="form-group">
              <label>Knowledge Base</label>
              <div class="file-upload">
                <input type="file" @change="handleFileUpload" multiple accept=".md,.txt,.pdf" id="file-upload">
                <label for="file-upload" class="upload-btn">
                  <span class="emoji">📄</span>
                  Upload Documents
                </label>
                <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                  <div v-for="file in uploadedFiles" :key="file.name" class="file-item">
                    <span class="emoji">📄</span>
                    <span>{{ file.name }}</span>
                    <button @click="removeFile(file)" class="btn-icon">✕</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>Chunk Size</label>
              <input type="number" v-model="newTraining.ragConfig.chunkSize" min="100" max="2000" class="form-control">
              <small>Size of text chunks for embedding</small>
            </div>
            <div class="form-group">
              <label>Top K Results</label>
              <input type="number" v-model="newTraining.ragConfig.topK" min="1" max="20" class="form-control">
              <small>Number of relevant chunks to retrieve</small>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <!-- Debug Info -->
          <div v-if="!canStartTraining" class="debug-info">
            <small class="text-muted">
              Missing: 
              <span v-if="!newTraining.jobName.trim()">Job Name, </span>
              <span v-if="!newTraining.baseModel">Base Model, </span>
              <span v-if="newTraining.selectedDatasets.length === 0 && uploadedFiles.length === 0">Datasets or Files</span>
            </small>
          </div>
          
          <button class="btn btn-secondary" @click="showTrainingModal = false">
            Cancel
          </button>
          <button class="btn btn-primary" @click="createTrainingJob" :disabled="!canStartTraining">
            Start Training
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Icon from '../components/Icon.vue';
import { io } from 'socket.io-client';
export default {
  name: 'TrainingView',
  components: {
    Icon

  },
  data() {
    return {
      showTrainingModal: false,
      uploadedFiles: [],
      availableDatasets: [],
      ollamaModels: [],
      newTraining: {
        jobName: '',
        description: '',
        jobType: 'experimental',
        maker: '',
        version: '',
        type: 'lora',
        baseModel: '',
        datasetType: 'upload',
        selectedDatasets: [],
        trainingStrategy: 'concatenate',
        roleDefinition: 'You are Agimat, an advanced AI assistant specialized in debugging and code analysis. You provide step-by-step guidance, identify issues, and offer practical solutions.',
        loraConfig: {
          rank: 8,
          alpha: 32,
          dropout: 0.05
        },
        params: {
          learningRate: 0.0002,
          batchSize: 4,
          epochs: 3,
          maxSteps: 2000
        },
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      },
      trainingJobs: [],
      chromadbCollections: 0
    };
  },
  computed: {
    canStartTraining() {
      const hasJobName = !!this.newTraining.jobName.trim();
      const hasBaseModel = !!this.newTraining.baseModel;
      const hasDatasets = this.newTraining.selectedDatasets.length > 0;
      const hasUploadedFiles = this.uploadedFiles.length > 0;
      
      // For RAG training, we need either datasets OR uploaded files (not both)
      if (this.newTraining.type === 'rag') {
        return hasJobName && hasBaseModel && (hasDatasets || hasUploadedFiles);
      }
      
      // For other training types, we need datasets OR uploaded files
      return hasJobName && hasBaseModel && (hasDatasets || hasUploadedFiles);
    },
    totalSelectedSamples() {
      return this.newTraining.selectedDatasets.reduce((total, datasetId) => {
        return total + this.getDatasetSamples(datasetId);
      }, 0);
    },
    runningJobsCount() {
      return this.trainingJobs.filter(job => job.status === 'RUNNING').length;
    },
    completedJobsCount() {
      return this.trainingJobs.filter(job => job.status === 'COMPLETED').length;
    },
    failedJobsCount() {
      return this.trainingJobs.filter(job => job.status === 'FAILED').length;
    }
  },
  methods: {
    initializeSocket() {
      // Connect to Socket.IO server
      this.socket = io('http://localhost:5000');
      
      // Listen for real-time training progress updates
      this.socket.on('training_progress', (data) => {
        console.log('📊 Real-time training progress:', data);
        this.updateTrainingProgress(data);
      });
      
      this.socket.on('connect', () => {
        console.log('🔌 Connected to Socket.IO server');
      });
      
      this.socket.on('disconnect', () => {
        console.log('🔌 Disconnected from Socket.IO server');
      });
    },
    
    updateTrainingProgress(data) {
      // Find the training job and update its progress
      const jobIndex = this.trainingJobs.findIndex(job => job.id === data.job_id);
      if (jobIndex !== -1) {
        // Update progress with real-time data
        this.trainingJobs[jobIndex].progress = data.progress;
        
        // Update step information if available
        if (data.current_step && data.total_steps) {
          this.trainingJobs[jobIndex].currentStep = data.current_step;
          this.trainingJobs[jobIndex].totalSteps = data.total_steps;
          this.trainingJobs[jobIndex].stepProgress = data.step_progress;
        }
        
        // Update epoch information if available
        if (data.epoch && data.total_epochs) {
          this.trainingJobs[jobIndex].currentEpoch = data.epoch;
          this.trainingJobs[jobIndex].totalEpochs = data.total_epochs;
        }
        
        console.log(`📈 Updated job ${data.job_id}: ${data.message}`);
      }
    },
    
    async fetchAvailableDatasets() {
      try {
        console.log('Fetching available datasets for training...');
        const response = await fetch('http://localhost:5000/api/datasets');
        const result = await response.json();
        
        if (result.success) {
          // Transform database format to frontend format
          this.availableDatasets = result.datasets.map(dataset => ({
            id: dataset.id.toString(),
            name: dataset.name,
            description: dataset.description,
            type: dataset.type,
            sampleCount: dataset.sample_count,
            createdAt: dataset.created_at,
            tags: dataset.tags || [],
            isFavorite: Boolean(dataset.is_favorite),
            lastModified: dataset.last_modified,
            size: dataset.size,
            format: dataset.format,
            license: dataset.license,
            datasetId: dataset.dataset_id,
            source: dataset.source
          }));
          
          console.log(`Loaded ${this.availableDatasets.length} datasets for training`);
        } else {
          console.error('Failed to fetch datasets:', result.error);
        }
      } catch (error) {
        console.error('Error fetching datasets:', error);
        // Don't show error to user, just log it
      }
    },
    async fetchTrainingJobs() {
      try {
        console.log('Fetching training jobs from API...');
        const response = await fetch('http://localhost:5000/api/training-jobs');
        const result = await response.json();
        
        if (result.success) {
          // Transform database format to frontend format
          this.trainingJobs = result.jobs.map(job => ({
            id: job.id.toString(),
            jobName: job.name,
            description: job.description,
            jobType: job.job_type,
            maker: job.maker,
            version: job.version,
            modelName: job.model_name || job.base_model,
            baseModel: job.base_model,
            datasetName: this.getDatasetName(job.dataset_id),
            status: job.status,
            progress: Math.round(job.progress * 100), // Convert to percentage
            currentEpoch: Math.floor(job.progress * (job.config?.params?.epochs || 10)),
            totalEpochs: job.config?.params?.epochs || 10,
            elapsedTime: this.calculateElapsedTime(job.started_at),
            type: job.training_type,
            config: job.config || {},
            errorMessage: job.error_message || null,
            isStuck: this.isJobStuck(job)
          }));
          
          console.log(`Loaded ${this.trainingJobs.length} training jobs from API`);
          
          // Check for stuck jobs and auto-detect them
          await this.detectStuckJobs();
        } else {
          console.error('Failed to fetch training jobs:', result.error);
        }
      } catch (error) {
        console.error('Error fetching training jobs:', error);
        // Don't show error to user, just log it
      }
    },
    
    calculateElapsedTime(startedAt) {
      if (!startedAt) return 0;
      const start = new Date(startedAt);
      const now = new Date();
      return Math.floor((now - start) / (1000 * 60)); // minutes
    },
    
    isJobStuck(job) {
      if (job.status !== 'RUNNING') return false;
      
      const elapsedMinutes = this.calculateElapsedTime(job.started_at);
      const timeoutMinutes = job.training_type === 'LoRA' ? 30 : 10;
      
      return elapsedMinutes > timeoutMinutes && job.progress < 0.5;
    },
    
    async detectStuckJobs() {
      try {
        const response = await fetch('http://localhost:5000/api/detect-stuck-training', {
          method: 'POST'
        });
        const result = await response.json();
        
        if (result.success && result.stuck_jobs_found > 0) {
          console.log(`Detected ${result.stuck_jobs_found} stuck training jobs`);
          // Refresh the training jobs list
          await this.fetchTrainingJobs();
        }
      } catch (error) {
        console.error('Error detecting stuck jobs:', error);
      }
    },
    async fetchOllamaModels() {
      try {
        console.log('Fetching Ollama models...');
        const response = await fetch('http://localhost:5000/api/models');
        const result = await response.json();
        
        if (result.success) {
          this.ollamaModels = result.models;
          console.log(`Loaded ${this.ollamaModels.length} Ollama models`);
        } else {
          console.error('Failed to fetch Ollama models:', result.error);
          this.ollamaModels = [];
        }
      } catch (error) {
        console.error('Error fetching Ollama models:', error);
        this.ollamaModels = [];
        // Don't show error to user, just log it
      }
    },
    getDatasetName(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId);
      return dataset ? dataset.name : 'Unknown Dataset';
    },
    getModelIcon(capabilities) {
      if (capabilities.includes('Coding') || capabilities.includes('Code Generation')) {
        return 'code';
      } else if (capabilities.includes('Reasoning') || capabilities.includes('Mathematics')) {
        return 'psychology';
      } else if (capabilities.includes('Visual Analysis')) {
        return 'visibility';
      } else if (capabilities.includes('Planning') || capabilities.includes('Task Management')) {
        return 'assignment';
      } else if (capabilities.includes('Conversation') || capabilities.includes('Instructions')) {
        return 'chat';
      } else {
        return 'smart_toy';
      }
    },
    getModelColor(capabilities) {
      if (capabilities.includes('Coding') || capabilities.includes('Code Generation')) {
        return 'success';
      } else if (capabilities.includes('Reasoning') || capabilities.includes('Mathematics')) {
        return 'info';
      } else if (capabilities.includes('Visual Analysis')) {
        return 'warning';
      } else if (capabilities.includes('Planning') || capabilities.includes('Task Management')) {
        return 'primary';
      } else if (capabilities.includes('Conversation') || capabilities.includes('Instructions')) {
        return 'secondary';
      } else {
        return 'light';
      }
    },
    getJobDisplayName(job) {
      // Show job name if it exists, otherwise show the original model name
      return job.jobName || job.modelName || job.baseModel || 'Unknown Job';
    },
    getModelDisplayOption(model) {
      const icon = this.getModelIcon(model.capabilities);
      const primaryCapability = model.capabilities[0] || 'General';
      const size = model.size;
      
      // Map icons to emojis for better display
      const iconMap = {
        'code': '💻',
        'psychology': '🧠',
        'visibility': '👁️',
        'assignment': '📋',
        'chat': '💬',
        'smart_toy': '🤖'
      };
      
      const emoji = iconMap[icon] || '🤖';
      return `${emoji} ${model.name} (${primaryCapability}) - ${size}`;
    },
    getModelDescription(capabilities) {
      const descriptions = {
        'Coding': 'Code generation, refactoring, and multi-language programming support',
        'Code Generation': 'Advanced code generation and syntax analysis',
        'Debugging': 'Code debugging, error analysis, and problem solving',
        'Reasoning': 'Mathematical reasoning, logical analysis, and complex problem solving',
        'Mathematics': 'Mathematical calculations and formula analysis',
        'Planning': 'Project planning, task management, and strategic coordination',
        'Visual Analysis': 'Code visualization, UI design, and visual documentation',
        'Conversation': 'Natural language conversation and interaction',
        'Instructions': 'Following complex instructions and task execution'
      };
      
      const primaryCapability = capabilities[0];
      return descriptions[primaryCapability] || 'General purpose AI model for various tasks';
    },
    getDatasetSamples(datasetId) {
      const dataset = this.availableDatasets.find(d => d.id === datasetId);
      return dataset ? dataset.sampleCount : 0;
    },
    removeDataset(datasetId) {
      this.newTraining.selectedDatasets = this.newTraining.selectedDatasets.filter(id => id !== datasetId);
    },
    showDatasetInfo(dataset) {
      // Show dataset details in a modal or alert
      alert(`Dataset: ${dataset.name}\n\n` +
            `Description: ${dataset.description}\n` +
            `Samples: ${dataset.sampleCount.toLocaleString()}\n` +
            `Type: ${dataset.type}\n` +
            `Format: ${dataset.format}\n` +
            `Size: ${dataset.size}\n` +
            `Source: ${dataset.source || 'Local'}`);
    },
    showSuccessMessage(message) {
      // Simple success message (you can enhance this with a toast notification)
      alert(`✅ ${message}`);
    },
    showError(message) {
      // Simple error message (you can enhance this with a toast notification)
      alert(`❌ ${message}`);
    },
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      this.uploadedFiles = [...this.uploadedFiles, ...files];
    },
    removeFile(file) {
      this.uploadedFiles = this.uploadedFiles.filter(f => f !== file);
    },
    async createTrainingJob() {
      try {
        // Prepare training job data
        const trainingData = {
          jobName: this.newTraining.jobName,
          description: this.newTraining.description,
          jobType: this.newTraining.jobType,
          maker: this.newTraining.maker,
          version: this.newTraining.version,
          baseModel: this.newTraining.baseModel,
          type: this.newTraining.type,
          selectedDatasets: this.newTraining.selectedDatasets,
          trainingStrategy: this.newTraining.trainingStrategy,
          roleDefinition: this.newTraining.roleDefinition,
          loraConfig: this.newTraining.loraConfig,
          params: this.newTraining.params,
          ragConfig: this.newTraining.ragConfig
        };

        // Call backend API to create training job
        const response = await fetch('http://localhost:5000/api/training-jobs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(trainingData)
        });

        const result = await response.json();

        if (result.success) {
          // Create frontend job object with backend data
          const newJob = {
            id: result.job_id,
            jobName: this.newTraining.jobName,
            description: this.newTraining.description,
            jobType: this.newTraining.jobType,
            maker: this.newTraining.maker,
            version: this.newTraining.version,
            modelName: result.model_name, // This is the actual model name that will be created
            baseModel: this.getModelDisplayName(this.newTraining.baseModel),
            datasetName: this.getDatasetName(),
          status: 'RUNNING',
            progress: 0,
            currentEpoch: 0,
            totalEpochs: this.newTraining.params.epochs,
            elapsedTime: 0,
            type: this.newTraining.type,
            config: { ...this.newTraining }
          };
          
          this.trainingJobs.unshift(newJob);
          this.showTrainingModal = false;
          
          // Show success message with model name
          this.showSuccessMessage(`Training job "${this.newTraining.jobName}" started! Model will be saved as "${result.model_name}"`);
          
          // Simulate training progress
          this.simulateTraining(newJob.id);
          
          // Reset form
          this.resetTrainingForm();
        } else {
          this.showError(result.error || 'Failed to start training job');
        }
      } catch (error) {
        console.error('Error starting training:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    getModelDisplayName(modelId) {
      const modelNames = {
        'agimat:latest': 'agimat:latest',
        'claude-reasoning:latest': 'claude-reasoning:latest',
        'llava:13b': 'llava:13b',
        'qwen2.5-coder:7b': 'qwen2.5-coder:7b',
        'codellama:13b': 'codellama:13b',
        'llama3.1:8b': 'llama3.1:8b'
      };
      return modelNames[modelId] || modelId;
    },
    getDatasetName() {
      if (this.newTraining.type === 'rag') {
        return `${this.uploadedFiles.length} documents (RAG)`;
      }
      return this.newTraining.datasetType === 'upload' ? 'Custom JSONL Dataset' : 'Knowledge Base Dataset';
    },
    simulateTraining(jobId) {
      const job = this.trainingJobs.find(j => j.id === jobId);
      if (!job) return;
      
      const interval = setInterval(() => {
        if (job.progress >= 100) {
          job.status = 'COMPLETED';
          clearInterval(interval);
          return;
        }
        
        job.progress += Math.random() * 5;
        job.currentEpoch = Math.floor((job.progress / 100) * job.totalEpochs);
        job.elapsedTime += 30;
        
        if (job.progress >= 100) {
          job.progress = 100;
          job.currentEpoch = job.totalEpochs;
          job.status = 'COMPLETED';
          clearInterval(interval);
        }
      }, 2000);
    },
    resetTrainingForm() {
      this.newTraining = {
        type: 'lora',
        baseModel: '',
        datasetType: 'upload',
        roleDefinition: 'You are Agimat, an advanced AI assistant specialized in debugging and code analysis. You provide step-by-step guidance, identify issues, and offer practical solutions.',
        loraConfig: {
          rank: 8,
          alpha: 32,
          dropout: 0.05
        },
        params: {
          learningRate: 0.0002,
          batchSize: 4,
          epochs: 3,
          maxSteps: 2000
        },
        ragConfig: {
          chunkSize: 1000,
          topK: 4
        }
      };
      this.uploadedFiles = [];
    },
    formatDuration(seconds) {
      if (!seconds) return '--';
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      return h > 0 ? `${h}h ${m}m` : `${m}m`;
    },
    startNewTraining() {
      this.showTrainingModal = true;
    },
    viewJobDetails(job) {
      // In a real app, this would show detailed job info
      alert(`Viewing details for job: ${job.modelName}`);
    },
    async startTraining(jobId) {
      try {
        console.log(`🚀 Starting real training for job ${jobId}`);
        
        const response = await fetch(`http://localhost:5000/api/training-jobs/${jobId}/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccessMessage(`Real training started for job ${jobId}!`);
          
          // Update job status locally
          const job = this.trainingJobs.find(j => j.id === jobId.toString());
          if (job) {
            job.status = 'RUNNING';
            job.progress = 0;
          }
          
          // Start polling for progress updates
          this.startProgressPolling(jobId);
          
        } else {
          this.showError(result.error || 'Failed to start training');
        }
        
      } catch (error) {
        console.error('Error starting training:', error);
        this.showError('Failed to connect to server. Make sure the API server is running.');
      }
    },
    
    async stopTraining(jobId) {
      try {
      if (confirm('Stop this training job?')) {
          console.log(`🛑 Stopping training for job ${jobId}`);
          
          const response = await fetch(`http://localhost:5000/api/training-jobs/${jobId}/stop`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          const result = await response.json();
          
          if (result.success) {
            this.showSuccessMessage(`Training stopped for job ${jobId}`);
            
            // Update job status locally
            const job = this.trainingJobs.find(j => j.id === jobId.toString());
            if (job) {
              job.status = 'STOPPED';
            }
            
            // Stop progress polling
            this.stopProgressPolling(jobId);
            
          } else {
            this.showError(result.error || 'Failed to stop training');
          }
        }
      } catch (error) {
        console.error('Error stopping training:', error);
        this.showError('Failed to connect to server.');
      }
    },
    
    startProgressPolling(jobId) {
      // Poll for progress updates every 5 seconds
      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/training-jobs/${jobId}/status`);
          const result = await response.json();
          
          if (result.success) {
            const status = result.status;
            const job = this.trainingJobs.find(j => j.id === jobId.toString());
            
            if (job && status.running) {
              // Job is still running, update progress
              job.status = 'RUNNING';
              // Note: Progress updates will come from the training executor
            } else if (job && !status.running) {
              // Job completed or stopped
              job.status = status.status;
              if (status.status === 'COMPLETED') {
                this.showSuccessMessage(`Training completed for job ${jobId}!`);
                // Refresh the jobs list to get updated data
                await this.fetchTrainingJobs();
              }
              this.stopProgressPolling(jobId);
            }
          }
        } catch (error) {
          console.error('Error polling training status:', error);
        }
      }, 5000);
      
      // Store interval ID for cleanup
      this.progressPollingIntervals = this.progressPollingIntervals || {};
      this.progressPollingIntervals[jobId] = pollInterval;
    },
    
    stopProgressPolling(jobId) {
      if (this.progressPollingIntervals && this.progressPollingIntervals[jobId]) {
        clearInterval(this.progressPollingIntervals[jobId]);
        delete this.progressPollingIntervals[jobId];
      }
    },
    
    stopJob(jobId) {
      // Legacy method - redirect to new stopTraining
      this.stopTraining(jobId);
    },
    async deleteJob(jobId) {
      // Find the job to get its details for confirmation
        const job = this.trainingJobs.find(j => j.id === jobId);
      if (!job) return;
      
      // Show confirmation modal with job details
      const confirmed = confirm(
        `Are you sure you want to delete this training job?\n\n` +
        `Job: ${job.jobName}\n` +
        `Type: ${job.type}\n` +
        `Status: ${job.status}\n` +
        `Model: ${job.modelName}\n\n` +
        `This action cannot be undone and will also delete:\n` +
        `- The training job record\n` +
        `- Associated ChromaDB collection (if RAG)\n` +
        `- Generated model files (if completed)`
      );
      
      if (!confirmed) return;
      
      try {
        // Delete from backend
        const response = await fetch(`http://localhost:5000/api/training-jobs/${jobId}`, {
          method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Remove from frontend array
          this.trainingJobs = this.trainingJobs.filter(j => j.id !== jobId);
          
          // Show success message with cleanup details
          console.log(`✅ Successfully deleted training job: ${job.jobName}`);
          console.log('🧹 Cleanup results:', result.cleanup_results);
          
          // Show cleanup results to user
          const cleanupMessage = result.cleanup_results && result.cleanup_results.length > 0 
            ? `\n\nCleanup completed:\n${result.cleanup_results.join('\n')}`
            : '';
          
          alert(`✅ Training job "${job.jobName}" deleted successfully!${cleanupMessage}`);
          
          // Refresh data to ensure consistency
          await this.fetchTrainingJobs();
          await this.fetchChromaDBCollections();
          
        } else {
          console.error('Failed to delete training job:', result.error);
          alert(`Failed to delete training job: ${result.error}`);
        }
        
      } catch (error) {
        console.error('Error deleting training job:', error);
        alert(`Error deleting training job: ${error.message}`);
      }
    },
    
    async fetchOllamaModels() {
      try {
        const response = await fetch('http://localhost:5000/api/models');
        const result = await response.json();
        
        if (result.success) {
          this.ollamaModels = result.models.map(model => ({
            name: model.name,
            capabilities: model.capabilities || []
          }));
          console.log('Loaded Ollama models:', this.ollamaModels.length);
        } else {
          console.error('Failed to fetch Ollama models:', result.error);
        }
      } catch (error) {
        console.error('Error fetching Ollama models:', error);
      }
    },
    
    async fetchChromaDBCollections() {
      try {
        const response = await fetch('http://localhost:5000/api/chromadb/collections');
        const result = await response.json();
        
        if (result.success) {
          this.chromadbCollections = result.total || 0;
          console.log('ChromaDB collections:', this.chromadbCollections);
        } else {
          console.error('Failed to fetch ChromaDB collections:', result.error);
          this.chromadbCollections = 0;
        }
      } catch (error) {
        console.error('Error fetching ChromaDB collections:', error);
        this.chromadbCollections = 0;
      }
    }
  },
  
  beforeUnmount() {
    // Clean up Socket.IO connection
    if (this.socket) {
      this.socket.disconnect();
    }
  },
  
  async mounted() {
    // Load available datasets, training jobs, and Ollama models when component mounts
    await this.fetchAvailableDatasets();
    await this.fetchTrainingJobs();
    await this.fetchOllamaModels();
    await this.fetchChromaDBCollections();
    
    // Initialize Socket.IO connection for real-time updates
    this.initializeSocket();
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

/* Capabilities Overview */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(var(--primary-rgb), 0.1);
}

.card-content h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.card-content p {
  margin: 0.25rem 0 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.capabilities-overview {
  margin-bottom: 2rem;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.capability-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
  transition: transform 0.3s ease;
}

.capability-card:hover {
  transform: translateY(-3px);
}

.capability-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.capability-card h3 {
  margin: 0 0 0.75rem;
  font-size: 1.2rem;
  color: var(--text-color);
}

.capability-card p {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.capability-models {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.model-tag {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-info {
  display: flex;
  justify-content: space-between;
  margin: 0.75rem 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.model-size {
  background: rgba(var(--success-rgb), 0.1);
  color: var(--success-color);
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.model-modified {
  color: var(--text-secondary);
  font-style: italic;
}

.no-models-message {
  color: var(--text-secondary);
  font-style: italic;
  margin-top: 0.5rem;
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

.job-description {
  margin: 0 0 0.75rem;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
}

.job-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.capability-tag {
  background: rgba(78, 115, 223, 0.1);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dataset-info {
  margin: 0 0 1rem;
  color: var(--secondary);
  font-size: 0.85rem;
  font-style: italic;
}

.job-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric-label {
  font-size: 0.7rem;
  color: var(--secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--primary);
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

.btn-start {
  color: #28a745;
}

.btn-start:hover {
  color: #1e7e34;
}

.btn-stop {
  color: #dc3545;
}

.btn-stop:hover {
  color: #c82333;
}

/* Modal Styles */
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
  background: var(--card-bg);
  border-radius: 12px;
  width: 100%;
  /* max-width: 800px; */
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

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Training Type Cards */
.training-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.training-type-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
}

.training-type-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.training-type-card.active {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.training-type-card h4 {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.training-type-card p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--secondary);
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

/* Configuration Sections */
.lora-config,
.training-params,
.rag-config {
  background: rgba(78, 115, 223, 0.02);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
  border: 1px solid rgba(78, 115, 223, 0.1);
}

.lora-config h3,
.training-params h3,
.rag-config h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.config-grid,
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

/* Dataset Options */
.dataset-options {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.dataset-option {
  flex: 1;
}

.option-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.dataset-option input:checked + .option-card {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

.option-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* File Upload */
.file-upload {
  margin-top: 0.5rem;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--card-bg);
  border: 2px dashed rgba(78, 115, 223, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color);
}

.upload-btn:hover {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
}

#file-upload {
  display: none;
}

.uploaded-files {
  margin-top: 1rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.file-item .btn-icon {
  width: 24px;
  height: 24px;
  font-size: 0.8rem;
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

/* Responsive */
@media (max-width: 768px) {
  .capabilities-grid {
    grid-template-columns: 1fr;
  }
  
  .training-types {
    grid-template-columns: 1fr;
  }
  
  .config-grid,
  .params-grid {
    grid-template-columns: 1fr;
  }
  
  .dataset-options {
    flex-direction: column;
  }
  
  .modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .job-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Dataset Options Styling */
.dataset-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dataset-option {
  cursor: pointer;
}

.dataset-option .option-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--card-bg);
  border: 2px solid transparent;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.dataset-option:hover .option-card {
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.dataset-option input:checked + .option-card {
  border-color: var(--primary);
  background: rgba(78, 115, 223, 0.05);
  box-shadow: var(--shadow);
}

.dataset-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dataset-name {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.95rem;
}

.dataset-details {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.dataset-actions {
  margin-left: auto;
}

.info-icon {
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.info-icon:hover {
  opacity: 1;
}

.selected-datasets {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.selected-datasets h4 {
  margin: 0 0 0.75rem 0;
  color: var(--primary);
  font-size: 1rem;
}

.selected-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.selected-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: white;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.selected-item .dataset-name {
  font-weight: 500;
  color: var(--text-color);
}

.selected-item .dataset-samples {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-left: auto;
  margin-right: 0.5rem;
}

.training-strategy {
  margin-top: 1rem;
}

.training-strategy label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.training-strategy small {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-style: italic;
}

.debug-info {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: rgba(231, 74, 59, 0.1);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(231, 74, 59, 0.2);
}

.debug-info small {
  color: var(--danger);
  font-weight: 500;
}

/* Training Metadata Styling */
.training-metadata {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius);
  border: 1px solid rgba(78, 115, 223, 0.2);
}

.training-metadata h3 {
  margin: 0 0 1rem 0;
  color: var(--primary);
  font-size: 1.1rem;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.required {
  color: var(--danger);
  font-weight: bold;
}

/* Job Metadata Display */
.job-metadata {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(78, 115, 223, 0.05);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(78, 115, 223, 0.1);
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
  min-width: 80px;
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
</style>
