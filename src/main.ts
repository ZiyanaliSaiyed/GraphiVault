import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize theme after Pinia is available
import { useThemeStore } from './stores/theme'
const themeStore = useThemeStore()
themeStore.initializeTheme()

app.mount('#app')
