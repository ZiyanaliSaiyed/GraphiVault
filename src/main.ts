import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'
import { useThemeStore } from './stores/theme'

const app = createApp(App)

// Initialize theme before mounting
const themeStore = useThemeStore()
themeStore.initializeTheme()

app.use(createPinia())
app.use(router)

app.mount('#app')
