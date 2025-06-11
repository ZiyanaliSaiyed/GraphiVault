import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)
  const theme = ref<'light' | 'dark'>('light')

  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    
    if (savedTheme) {
      theme.value = savedTheme as 'light' | 'dark'
    } else {
      theme.value = prefersDark ? 'dark' : 'light'
    }
    
    isDark.value = theme.value === 'dark'
    applyTheme()
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    isDark.value = theme.value === 'dark'
    localStorage.setItem('theme', theme.value)
    applyTheme()
  }

  const applyTheme = () => {
    document.documentElement.setAttribute('data-theme', theme.value)
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  return {
    isDark,
    theme,
    initializeTheme,
    toggleTheme
  }
})
