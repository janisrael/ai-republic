<template>
  <div class="icon-showcase">
    <h2>🎨 Icon System Showcase</h2>
    
    <!-- Sizes -->
    <section class="showcase-section">
      <h3>Sizes</h3>
      <div class="icon-group">
        <span class="material-icons-round icon-xs">home</span>
        <span class="material-icons-round icon-sm">home</span>
        <span class="material-icons-round icon-md">home</span>
        <span class="material-icons-round icon-lg">home</span>
        <span class="material-icons-round icon-xl">home</span>
        <span class="material-icons-round icon-xxl">home</span>
      </div>
    </section>

    <!-- Colors -->
    <section class="showcase-section">
      <h3>Colors</h3>
      <div class="icon-group">
        <span class="material-icons-round icon-primary">favorite</span>
        <span class="material-icons-round icon-secondary">favorite</span>
        <span class="material-icons-round icon-success">favorite</span>
        <span class="material-icons-round icon-info">favorite</span>
        <span class="material-icons-round icon-warning">favorite</span>
        <span class="material-icons-round icon-danger">favorite</span>
        <span class="material-icons-round icon-dark">favorite</span>
        <span class="material-icons-round icon-muted">favorite</span>
      </div>
    </section>

    <!-- States -->
    <section class="showcase-section">
      <h3>States</h3>
      <div class="icon-group">
        <span class="material-icons-round icon-hover">touch_app</span>
        <span class="material-icons-round icon-spin">refresh</span>
        <span class="material-icons-round icon-hover icon-primary">favorite</span>
      </div>
    </section>

    <!-- AI Dashboard Icons -->
    <section class="showcase-section">
      <h3>AI Dashboard Icons</h3>
      <div class="dashboard-icons">
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">psychology</span>
          </div>
          <span>AI/ML</span>
        </div>
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">model_training</span>
          </div>
          <span>Training</span>
        </div>
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">dataset</span>
          </div>
          <span>Dataset</span>
        </div>
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">rocket_launch</span>
          </div>
          <span>Deploy</span>
        </div>
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">assessment</span>
          </div>
          <span>Evaluate</span>
        </div>
        <div class="icon-card">
          <div class="card-icon">
            <span class="material-icons-round">analytics</span>
          </div>
          <span>Analytics</span>
        </div>
      </div>
    </section>

    <!-- Status Indicators -->
    <section class="showcase-section">
      <h3>Status Indicators</h3>
      <div class="status-examples">
        <div class="status-item">
          <span class="status-icon success">
            <span class="material-icons-round">check_circle</span>
          </span>
          <span>Training Complete</span>
        </div>
        <div class="status-item">
          <span class="status-icon warning">
            <span class="material-icons-round">warning</span>
          </span>
          <span>Training Pending</span>
        </div>
        <div class="status-item">
          <span class="status-icon danger">
            <span class="material-icons-round">error</span>
          </span>
          <span>Training Failed</span>
        </div>
        <div class="status-item">
          <span class="status-icon info">
            <span class="material-icons-round">info</span>
          </span>
          <span>Training Info</span>
        </div>
      </div>
    </section>

    <!-- Icon with Text Examples -->
    <section class="showcase-section">
      <h3>Icon with Text</h3>
      <div class="text-examples">
        <div class="icon-text">
          <span class="material-icons-round icon-primary">play_arrow</span>
          <span>Start Training</span>
        </div>
        <div class="icon-text">
          <span class="material-icons-round icon-success">upload</span>
          <span>Upload Dataset</span>
        </div>
        <div class="icon-text">
          <span class="material-icons-round icon-info">assessment</span>
          <span>Evaluate Model</span>
        </div>
        <div class="icon-text">
          <span class="material-icons-round icon-warning">rocket_launch</span>
          <span>Deploy Model</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'IconShowcase'
}
</script>

<style scoped>
.icon-showcase {
  padding: var(--spacer-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.showcase-section {
  margin-bottom: var(--spacer-xl);
}

.showcase-section h3 {
  margin-bottom: var(--spacer);
  color: var(--text-color);
  font-size: 1.25rem;
}

.dashboard-icons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacer);
}

.icon-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacer);
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.icon-card span:last-child {
  margin-top: var(--spacer-sm);
  font-size: 0.875rem;
  color: var(--text-muted);
}

.status-examples {
  display: flex;
  flex-direction: column;
  gap: var(--spacer);
}

.status-item {
  display: flex;
  align-items: center;
  padding: var(--spacer-sm);
  background: var(--card-bg);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.text-examples {
  display: flex;
  flex-direction: column;
  gap: var(--spacer);
}

.text-examples .icon-text {
  padding: var(--spacer-sm);
  background: var(--card-bg);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}
</style>
