<template>
  <div id="app" class="min-h-screen bg-gv-primary text-gv-text">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initializeTheme()
  // Set GraphiVault as default theme
  document.documentElement.setAttribute('data-theme', 'graphivault')
})
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color-scheme: dark;
}
</style>
