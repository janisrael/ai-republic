import { createRouter, createWebHistory } from 'vue-router';

// Lazy load components for better performance
const Dashboard = () => import('@/views/Dashboard.vue');
const Models = () => import('@/views/Models.vue');
const ModelComparison = () => import('@/views/ModelComparison.vue');
const Training = () => import('@/views/Training.vue');
const Datasets = () => import('@/views/Datasets.vue');
const Evaluation = () => import('@/views/Evaluation.vue');
const TrainingHistory = () => import('@/views/TrainingHistory.vue');
const AIRoom = () => import('@/views/AIRoom.vue');

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard' }
  },
  {
    path: '/models',
    name: 'Models',
    component: Models,
    meta: { title: 'Models' }
  },
  {
    path: '/model-comparison',
    name: 'ModelComparison',
    component: ModelComparison,
    meta: { title: 'Model Comparison' }
  },
  {
    path: '/training',
    name: 'Training',
    component: Training,
    meta: { title: 'Model Training' }
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: Datasets,
    meta: { title: 'Datasets' }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: Evaluation,
    meta: { title: 'Model Evaluation' }
  },
  {
    path: '/training-history',
    name: 'TrainingHistory',
    component: TrainingHistory,
    meta: { title: 'Training History' }
  },
  {
    path: '/ai-room',
    name: 'AIRoom',
    component: AIRoom,
    meta: { title: 'AI Room' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

// Update page title based on route meta
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} | AI Refinement` : 'AI Refinement';
  next();
});

export default router;
