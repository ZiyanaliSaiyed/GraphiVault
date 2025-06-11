<template>
  <div id="app" class="min-h-screen bg-gv-primary text-gv-text">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'
import { useVaultStore } from './stores/vault'

const themeStore = useThemeStore()
const vaultStore = useVaultStore()

onMounted(() => {
  // Initialize theme system first
  themeStore.initializeTheme()
  
  // Add a small delay to ensure DOM is ready
  setTimeout(() => {
    themeStore.applyTheme()
  }, 100)

  // Initialize vault store
  vaultStore.initialize()
})
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
  /* Modern font smoothing - keeping vendor prefixes as they're still needed for font rendering */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* Modern CSS for cross-browser text scaling */
  text-size-adjust: 100%;
  color-scheme: dark;
}
</style>
