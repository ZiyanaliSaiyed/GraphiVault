<template>
  <div class="platform-indicator">
    <div class="flex items-center gap-2 text-sm text-gv-muted">
      <div class="flex items-center gap-1">
        <div 
          :class="[
            'w-2 h-2 rounded-full',
            isTauri() ? 'bg-green-500' : 'bg-blue-500'
          ]"
        ></div>
        <span>{{ platformText }}</span>
      </div>
      
      <!-- Show additional info in development -->
      <div v-if="showDetails" class="text-xs opacity-75">
        {{ environmentInfo.platform }} • {{ environmentInfo.userAgent.split(' ')[0] }}
      </div>
    </div>
    
    <!-- Warning for web mode -->
    <div v-if="!isTauri" class="mt-2 p-2 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-400">
      <p class="font-medium">🌐 Browser Mode</p>
      <p>Limited functionality - files are stored temporarily. For full features, use the desktop app.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { isTauri, getEnvironmentInfo } from '../utils/tauri'

interface Props {
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})

const environmentInfo = getEnvironmentInfo()

const platformText = computed(() => {
  return isTauri() ? 'Desktop App' : 'Web Browser'
})
</script>

<style scoped>
.platform-indicator {
  @apply select-none;
}
</style>
