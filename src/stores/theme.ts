import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true) // Default to dark for GraphiVault
  const theme = ref<'graphivault' | 'graphivault-light'>('graphivault')

  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('graphivault-theme')
    
    if (savedTheme && (savedTheme === 'graphivault' || savedTheme === 'graphivault-light')) {
      theme.value = savedTheme as 'graphivault' | 'graphivault-light'
    } else {
      // GraphiVault defaults to dark theme (privacy-first mindset)
      theme.value = 'graphivault'
    }
    
    isDark.value = theme.value === 'graphivault'
    applyTheme()
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'graphivault' ? 'graphivault-light' : 'graphivault'
    isDark.value = theme.value === 'graphivault'
    localStorage.setItem('graphivault-theme', theme.value)
    applyTheme()
  }
  const applyTheme = () => {
    // Apply the theme to the document
    document.documentElement.setAttribute('data-theme', theme.value)
    document.documentElement.classList.toggle('dark', isDark.value)
    
    // Force immediate visual update
    const root = document.documentElement
    root.style.setProperty('--tw-bg-opacity', '1')
    
    // Apply GraphiVault-specific body styles
    if (isDark.value) {
      document.body.style.backgroundColor = '#0D1117'
      document.body.style.color = '#E5E7EB'
      root.style.colorScheme = 'dark'
    } else {
      document.body.style.backgroundColor = '#ffffff'
      document.body.style.color = '#1e293b'
      root.style.colorScheme = 'light'
    }
    
    // Trigger a reflow to ensure changes are applied
    document.body.offsetHeight
  }
  return {
    isDark,
    theme,
    initializeTheme,
    toggleTheme,
    applyTheme
  }
})
