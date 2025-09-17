<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Welcome back! Here's an overview of your AI models and training.</p>
    </div>

    <!-- Stats Cards -->
    <div class="dashboard-grid">
      <div class="neumorphic-card stats-card">
        <div class="stats-icon">
          <span class="material-icons-round">smart_toy</span>
        </div>
        <div class="stats-info">
          <h3>5</h3>
          <p>Active Models</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon training">
          <span class="material-icons-round">bolt</span>
        </div>
        <div class="stats-info">
          <h3>2</h3>
          <p>Training Jobs</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon dataset">
          <span class="material-icons-round">dataset</span>
        </div>
        <div class="stats-info">
          <h3>12</h3>
          <p>Datasets</p>
        </div>
      </div>

      <div class="neumorphic-card stats-card">
        <div class="stats-icon accuracy">
          <span class="material-icons-round">track_changes</span>
        </div>
        <div class="stats-info">
          <h3>92.5%</h3>
          <p>Avg. Accuracy</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity and Model Performance -->
    <div class="dashboard-row">
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Recent Activity</h3>
            <button class="btn btn-sm btn-secondary">View All</button>
          </div>
          <ul class="activity-list">
            <li v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <span class="material-icons-round">{{ activity.icon }}</span>
              </div>
              <div class="activity-details">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div class="dashboard-col">
        <div class="neumorphic-card">
          <div class="card-header">
            <h3>Model Performance</h3>
            <select class="form-control form-control-sm" style="width: auto;">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 90 days</option>
            </select>
          </div>
          <div class="chart-container">
            <LineChart :chart-data="chartData" :options="chartOptions" />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="neumorphic-card quick-actions">
      <h3>Quick Actions</h3>
      <div class="actions-grid">
        <button class="action-btn" @click="startNewTraining">
          <span class="material-icons-round icon-primary">play_arrow</span>
          <span>Start New Training</span>
        </button>
        <button class="action-btn" @click="uploadDataset">
          <span class="material-icons-round icon-success">upload</span>
          <span>Upload Dataset</span>
        </button>
        <button class="action-btn" @click="evaluateModel">
          <span class="material-icons-round icon-info">assessment</span>
          <span>Evaluate Model</span>
        </button>
        <button class="action-btn" @click="deployModel">
          <span class="material-icons-round icon-warning">rocket_launch</span>
          <span>Deploy Model</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from 'chart.js';
import { ref, onMounted, watch } from 'vue';

// Register ChartJS components
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale
);

// Create a custom LineChart component
const LineChart = {
  name: 'LineChart',
  extends: Line,
  props: {
    chartData: {
      type: Object,
      required: true
    },
    chartOptions: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const chartData = ref(props.chartData);
    const chartOptions = ref(props.chartOptions);
    const chartInstance = ref(null);

    onMounted(() => {
      if (chartInstance.value) {
        chartInstance.value.update();
      }
    });

    watch(() => props.chartData, (newData) => {
      chartData.value = newData;
      if (chartInstance.value) {
        chartInstance.value.data = newData;
        chartInstance.value.update();
      }
    }, { deep: true });

    watch(() => props.chartOptions, (newOptions) => {
      chartOptions.value = newOptions;
      if (chartInstance.value) {
        chartInstance.value.options = newOptions;
        chartInstance.value.update();
      }
    }, { deep: true });

    return {
      chartData,
      chartOptions,
      chartInstance
    };
  },
  mounted() {
    this.renderChart(this.chartData, this.chartOptions);
    this.chartInstance = this.$data._chart;
  }
};

export default {
  name: 'DashboardView',
  components: {
    LineChart
  },
  data() {
    return {
      recentActivities: [
        { 
          type: 'training',
          icon: 'bolt',
          text: 'Training job "Image Classifier v2.1" completed successfully',
          time: '10 minutes ago'
        },
        {
          type: 'model',
          icon: 'smart_toy',
          text: 'New model version 3.2.0 deployed to production',
          time: '2 hours ago'
        },
        {
          type: 'dataset',
          icon: 'dataset',
          text: 'New dataset "Street View Images Q3-2023" uploaded',
          time: '1 day ago'
        },
        {
          type: 'evaluation',
          icon: 'trending_up',
          text: 'Model accuracy improved to 94.2% on test set',
          time: '2 days ago'
        },
        {
          type: 'alert',
          icon: 'warning',
          text: 'Training job #1245 failed - Insufficient GPU memory',
          time: '3 days ago'
        }
      ],
      chartData: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Accuracy',
            data: [85, 82, 88, 87, 90, 91, 92.5],
            borderColor: '#4e73df',
            backgroundColor: 'rgba(78, 115, 223, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
          },
          {
            label: 'Loss',
            data: [1.2, 0.9, 0.8, 0.7, 0.6, 0.5, 0.45],
            borderColor: '#e74a3b',
            borderDash: [5, 5],
            backgroundColor: 'transparent',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              size: 13
            },
            padding: 12,
            cornerRadius: 8
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              padding: 10
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              padding: 10
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            hoverRadius: 6,
            hoverBorderWidth: 2
          }
        }
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    };
  },
  methods: {
    startNewTraining() {
      this.$router.push('/training');
    },
    uploadDataset() {
      this.$router.push('/datasets?action=upload');
    },
    evaluateModel() {
      this.$router.push('/evaluation');
    },
    deployModel() {
      // In a real app, this would open a deployment dialog
      alert('Deployment dialog would open here');
    }
  }
};
</script>

<style scoped>
:root {
  --primary-color: #4e73df;
  --success-color: #1cc88a;
  --info-color: #36b9cc;
  --warning-color: #f6c23e;
  --danger-color: #e74a3b;
  --light-color: #f8f9fc;
  --dark-color: #5a5c69;
}

.dashboard-container {
  padding: 1.5rem;
  /* max-width: 1400px; */
  margin: 0 auto;
  font-family: 'Roboto', sans-serif;
}

.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.page-header p {
  color: var(--secondary);
  margin: 0;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
  font-size: 1.8rem;
  background: linear-gradient(145deg, #caced3, #f0f5fd);
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.stats-icon i {
  font-style: normal;
}

.stats-icon.training {
  color: #f6c23e;
}

.stats-icon.dataset {
  color: #1cc88a;
}

.stats-icon.accuracy {
  color: #4e73df;
}

.stats-info h3 {
  font-size: 1.8rem;
  margin: 0 0 0.25rem;
  color: var(--text-color);
}

.stats-info p {
  margin: 0;
  color: var(--secondary);
  font-size: 0.9rem;
}

.dashboard-row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -0.75rem 1.5rem;
}

.dashboard-col {
  flex: 1 0 0%;
  padding: 0 0.75rem;
  min-width: 300px;
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-color);
}

.activity-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.activity-item {
  display: flex;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.2rem;
  background: var(--card-bg);
  box-shadow: 3px 3px 6px var(--shadow-dark), 
              -3px -3px 6px var(--shadow-light);
}

.activity-icon.training {
  color: #f6c23e;
}

.activity-icon.evaluation {
  color: #36b9cc;
}

.activity-icon.deployment {
  color: #1cc88a;
}

.activity-icon.dataset {
  color: #4e73df;
}

.activity-icon.model {
  color: #e74a3b;
}

.activity-details {
  flex: 1;
}

.activity-text {
  margin: 0 0 0.25rem;
  color: var(--text-color);
  font-size: 0.9rem;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--secondary);
}

.chart-container {
  height: 300px;
  position: relative;
  margin: 0 -1rem -1rem;
}

.quick-actions {
  margin-top: 1.5rem;
}

.quick-actions h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-color);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
  border: none;
  background: var(--card-bg);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 5px 5px 10px var(--shadow-dark), 
              -5px -5px 10px var(--shadow-light);
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 8px 8px 16px var(--shadow-dark), 
              -8px -8px 16px var(--shadow-light);
}

.action-btn i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-style: normal;
}

.action-btn span {
  font-size: 0.9rem;
  color: var(--text-color);
  font-weight: 500;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-col {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>
