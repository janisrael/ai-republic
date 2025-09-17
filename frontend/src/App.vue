<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isMobileMenuOpen = ref(false);
const activeRoute = ref('dashboard');

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const navigateTo = (routeName) => {
  // Convert route name to lowercase to match our activeRoute values
  const normalizedRoute = routeName.toLowerCase();
  activeRoute.value = normalizedRoute;
  isMobileMenuOpen.value = false;
  
  // Use the route name directly since that's what's defined in the router
  router.push({ name: routeName }).catch(err => {
    // Ignore the vuex err regarding  navigating to the page they are already on.
    if (err.name !== 'NavigationDuplicated') {
      console.error('Navigation error:', err);
    }
  });
};

// Set initial active route
const updateActiveRoute = () => {
  const route = router.currentRoute.value;
  if (route.name) {
    activeRoute.value = route.name.toLowerCase();
  }
};

// Call on initial load
updateActiveRoute();

// Watch for route changes
router.afterEach((to) => {
  if (to.name) {
    activeRoute.value = to.name.toLowerCase();
  }
});

onMounted(() => {
  // Check if we're on mobile
  const checkIfMobile = () => {
    isMobileMenuOpen.value = window.innerWidth > 992;
  };
  
  checkIfMobile();
  window.addEventListener('resize', checkIfMobile);
  
  return () => {
    window.removeEventListener('resize', checkIfMobile);
  };
});
</script>

<template>
  <div class="dashboard-layout">
    <!-- Mobile Menu Toggle -->
    <button 
      class="mobile-menu-toggle" 
      @click="toggleMobileMenu"
      :aria-label="isMobileMenuOpen ? 'Close menu' : 'Open menu'"
    >
      <span class="material-icons-round">{{ isMobileMenuOpen ? 'close' : 'menu' }}</span>
    </button>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'mobile-visible': isMobileMenuOpen }">
      <div class="logo-container">
        <h2>AI Republic</h2>
        <p>Model Training Dashboard</p>
      </div>
      
      <ul class="nav-menu">
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link" 
            :class="{ 'active': activeRoute === 'dashboard' }"
            @click.prevent="navigateTo('Dashboard')"
          >
            <span class="material-icons-round">dashboard</span>
            <span>Dashboard</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'models' }"
            @click.prevent="navigateTo('Models')"
          >
            <span class="material-icons-round">smart_toy</span>
            <span>Models</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'training' }"
            @click.prevent="navigateTo('Training')"
          >
            <span class="material-icons-round">model_training</span>
            <span>Training</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'datasets' }"
            @click.prevent="navigateTo('Datasets')"
          >
            <span class="material-icons-round">dataset</span>
            <span>Datasets</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            href="#" 
            class="nav-link"
            :class="{ 'active': activeRoute === 'evaluation' }"
            @click.prevent="navigateTo('Evaluation')"
          >
            <span class="material-icons-round">assessment</span>
            <span>Evaluation</span>
          </a>
        </li>
      </ul>
      
      <!-- Sidebar Footer with User Info -->
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <span class="material-icons-round">account_circle</span>
          </div>
          <div class="user-details">
            <h4>John Doe</h4>
            <p>Administrator</p>
          </div>
          <button class="btn btn-sm btn-outline">
            <span class="material-icons-round">logout</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <router-view v-if="$route"></router-view>
      <div v-else>
        <h1>Welcome to AI Refinement Dashboard</h1>
        <p>Select an option from the sidebar to get started.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Material Icons */
.material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-flex;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

/* Navigation Menu */
.nav-menu {
  list-style: none;
  padding: 0.5rem 1rem;
  margin: 0;
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}

.nav-item {
  margin-bottom: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  color: var(--text-color);
  text-decoration: none;
  transition: var(--transition);
  border-radius: var(--radius);
  background: var(--card-bg);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 500;
}

.nav-link:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  color: var(--primary);
}

.nav-link:active {
  transform: translateY(0);
  box-shadow: var(--shadow-inset);
}

.nav-link.active {
  background: var(--primary);
  color: white;
  box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.2),
              inset -3px -3px 6px rgba(122, 159, 245, 0.3);
}

.nav-link .material-icons-round {
  font-size: 1.25rem;
  width: 1.5rem;
  text-align: center;
  transition: transform 0.2s ease;
}

.nav-link:hover .material-icons-round {
  transform: scale(1.1);
}

.nav-link.active .material-icons-round {
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.dashboard-layout {
  /* display: flex; */
  min-height: 100vh;
  background-color: var(--bg-color);
  /* padding-left: 280px; */
  transition: padding 0.3s ease;
}

.sidebar {
  width: 280px;
  background: var(--card-bg);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  padding: 1.5rem 0;
  box-shadow: var(--shadow);
  z-index: 100;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.5);
}

/* Sidebar Header */
.logo-container {
  padding: 0 1.5rem 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  text-align: center;
}

.logo-container h2 {
  margin: 0;
  color: var(--primary);
  font-weight: 700;
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.logo-container p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* Mobile Menu Toggle */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 1100;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: var(--card-bg);
  box-shadow: var(--shadow);
  color: var(--text-color);
  cursor: pointer;
  transition: var(--transition);
  align-items: center;
  justify-content: center;
}

.mobile-menu-toggle:active {
  box-shadow: var(--shadow-inset);
}

.mobile-menu-toggle .material-icons-round {
  font-size: 1.5rem;
}

.sidebar {
  position: relative;
  transition: transform 0.3s ease;
}

@media (max-width: 992px) {
  .dashboard-layout {
    padding-left: 0;
  }

  .sidebar {
    transform: translateX(-100%);
    box-shadow: 8px 0 16px rgba(0, 0, 0, 0.1), 
                -4px 0 8px rgba(255, 255, 255, 0.8);
  }
  
  .sidebar.mobile-visible {
    transform: translateX(0);
    box-shadow: 8px 0 16px rgba(0, 0, 0, 0.1), 
                -4px 0 8px rgba(255, 255, 255, 0.8);
  }
  
  .mobile-menu-toggle {
    display: flex;
  }
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1.5rem;
  margin-top: auto;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--card-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
  color: var(--primary);
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-details h4 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-details p {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
