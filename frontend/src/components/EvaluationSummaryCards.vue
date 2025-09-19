<template>
  <div class="summary-cards">
    <div class="summary-card shadow-soft" v-for="(metric, key) in metrics" :key="key">
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
      <!-- ECharts Chart -->
      <div class="chart-container" :ref="`chart-${key}`" :style="{ width: '120px', height: '120px' }"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'EvaluationSummaryCards',
  props: {
    metrics: {
      type: Object,
      required: true
    },
    evaluations: {
      type: Array,
      default: () => []
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts();
    });
  },
  watch: {
    evaluations: {
      handler() {
        this.$nextTick(() => {
          this.initCharts();
        });
      },
      deep: true
    }
  },
  methods: {
    initCharts() {
      Object.keys(this.metrics).forEach(key => {
        const chartRef = this.$refs[`chart-${key}`];
        if (chartRef && chartRef[0]) {
          this.createChart(chartRef[0], key);
        }
      });
    },
    
    createChart(container, metricKey) {
      const chart = echarts.init(container);
      
      // Get data for this metric
      const data = this.getMetricData(metricKey);
      
      // Create multiple data points to show a proper area chart
      const chartData = [];
      const maxValue = metricKey === 'accuracy' ? 100 : Math.max(data.value * 1.5, 10);
      
      // Create 5 data points for a smooth area chart
      for (let i = 0; i < 5; i++) {
        const progress = i / 4;
        const value = data.value * (0.8 + 0.4 * progress); // Slight variation around the actual value
        chartData.push(value);
      }
      
      const option = {
        grid: {
          left: '5%',
          right: '5%',
          top: '5%',
          bottom: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['', '', '', '', ''],
          show: false
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: maxValue,
          show: false
        },
        series: [{
          name: metricKey === 'accuracy' ? 'Accuracy' : metricKey === 'models' ? 'Models' : 'Datasets',
          type: 'line',
          data: chartData,
          smooth: true,
          lineStyle: {
            color: this.getMetricColor(data.value, metricKey),
            width: 3
          },
          itemStyle: {
            color: this.getMetricColor(data.value, metricKey),
            borderColor: '#fff',
            borderWidth: 2
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: this.getMetricColorWithOpacity(data.value, metricKey, 0.4)
                },
                {
                  offset: 1,
                  color: this.getMetricColorWithOpacity(data.value, metricKey, 0.1)
                }
              ]
            }
          },
          symbol: 'none', // Remove dots for cleaner look
          emphasis: {
            itemStyle: {
              color: this.getMetricColor(data.value, metricKey),
              borderColor: '#fff',
              borderWidth: 3,
              shadowBlur: 10,
              shadowColor: this.getMetricColorWithOpacity(data.value, metricKey, 0.5)
            }
          }
        }]
      };
      
      chart.setOption(option);
      
      // Store chart instance for cleanup
      if (!this.chartInstances) {
        this.chartInstances = [];
      }
      this.chartInstances.push(chart);
    },
    
    getMetricData(metricKey) {
      if (metricKey === 'accuracy') {
        // Calculate average accuracy from evaluations with real data
        const evaluationsWithData = this.evaluations.filter(evaluation => 
          evaluation.metrics && evaluation.metrics.accuracy > 0
        );
        
        if (evaluationsWithData.length > 0) {
          const avgAccuracy = evaluationsWithData.reduce((sum, evaluation) => 
            sum + evaluation.metrics.accuracy, 0
          ) / evaluationsWithData.length;
          return { value: avgAccuracy };
        }
        return { value: 0 };
      } else if (metricKey === 'models') {
        return { value: this.evaluations.length };
      } else if (metricKey === 'datasets') {
        const uniqueDatasets = new Set(this.evaluations.map(evaluation => evaluation.datasetId)).size;
        return { value: uniqueDatasets };
      }
      return { value: 0 };
    },
    
    getMetricColor(value, metricKey) {
      if (metricKey === 'accuracy') {
        if (value >= 80) return '#2e7d32';
        if (value >= 60) return '#1976d2';
        if (value >= 40) return '#ed6c02';
        return '#d32f2f';
      } else if (metricKey === 'models') {
        return '#1976d2';
      } else if (metricKey === 'datasets') {
        return '#e65100';
      }
      return '#666';
    },
    
    getMetricColorWithOpacity(value, metricKey, opacity) {
      const baseColor = this.getMetricColor(value, metricKey);
      // Convert hex to rgba
      const hex = baseColor.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16);
      const g = parseInt(hex.substr(2, 2), 16);
      const b = parseInt(hex.substr(4, 2), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
  },
  
  beforeUnmount() {
    // Cleanup chart instances
    if (this.chartInstances) {
      this.chartInstances.forEach(chart => {
        chart.dispose();
      });
    }
  }
};
</script>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  border: 1px solid #eee;
  position: relative;
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

.summary-icon.accuracy {
  background-color: #e3f2fd;
  color: #1976d2;
}

.summary-icon.models {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.summary-icon.datasets {
  background-color: #fff3e0;
  color: #e65100;
}

.summary-details {
  flex: 1;
}

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

.trend.positive {
  color: #2e7d32;
}

.trend.negative {
  color: #d32f2f;
}

.chart-container {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
</style>
