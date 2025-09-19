import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/main.css';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

const app = createApp(App);

app.use(router);

// Add global error handler
app.config.errorHandler = (err) => {
  console.error('Vue error:', err);
};

// Mount the app
app.mount('#app');
