<template>
  <div
    class="relative group cursor-pointer"
    @click="toggleSelect"
  >
    <!-- Image Container -->
    <div
      :class="[
        'aspect-square rounded-lg overflow-hidden border-2 transition-all duration-200',
        selected ? 'border-primary shadow-lg' : 'border-transparent hover:border-base-300'
      ]"
    >
      <!-- Image Display -->
      <div v-if="decryptedImageSrc" class="w-full h-full flex items-center justify-center">
        <img :src="decryptedImageSrc" alt="Image" class="object-cover w-full h-full" />
      </div>
      <!-- Placeholder if not loaded -->
      <div v-else class="w-full h-full bg-base-200 flex items-center justify-center">
        <div class="text-center">
          <div class="text-2xl mb-2">🖼️</div>
          <div class="text-xs text-base-content/50 px-2">
            {{ image.name }}
          </div>
        </div>
      </div>

      <!-- Selection Overlay -->
      <div
        v-if="selected"
        class="absolute inset-0 bg-primary/20 flex items-center justify-center"
      >
        <div class="bg-primary text-primary-content rounded-full p-2">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>

      <!-- Hover Overlay -->
      <div
        v-else
        class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center"
      >
        <div class="text-white text-center">
          <svg class="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <div class="text-xs">Click to select</div>
        </div>
      </div>

      <!-- Encryption Badge -->
      <div
        v-if="image.isEncrypted"
        class="absolute top-2 right-2 bg-success text-success-content rounded-full p-1"
        title="Encrypted"
      >
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Image Info -->
    <div class="mt-2 px-1">
      <div class="text-xs font-medium truncate" :title="image.name">
        {{ image.name }}
      </div>
      <div class="text-xs text-base-content/60 mt-1">
        {{ formatFileSize(image.size) }} • {{ formatDate(image.dateAdded) }}
      </div>
      
      <!-- Tags -->
      <div v-if="image.tags.length > 0" class="flex flex-wrap gap-1 mt-2">
        <span
          v-for="tag in image.tags.slice(0, 3)"
          :key="tag"
          class="badge badge-xs badge-outline"
        >
          {{ tag }}
        </span>
        <span
          v-if="image.tags.length > 3"
          class="badge badge-xs badge-outline"
        >
          +{{ image.tags.length - 3 }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { format } from 'date-fns'
import { ref, onMounted } from 'vue'
import { tauriAPI } from '../utils/tauri'
import type { ImageFile } from '../stores/vault'

interface Props {
  image: ImageFile
  selected: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleSelect: [id: string]
}>()

const decryptedImageSrc = ref<string | null>(null)

const toggleSelect = () => {
  emit('toggleSelect', props.image.id)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (date: Date): string => {
  return format(date, 'MMM dd')
}

onMounted(async () => {
  if (props.image.isEncrypted) {
    try {
      const result = await tauriAPI.getDecryptedImage(Number(props.image.id))
      if (result.success && result.data?.image_data) {
        decryptedImageSrc.value = `data:image/png;base64,${result.data.image_data}`
      }
    } catch (err) {
      decryptedImageSrc.value = null
    }
  }
})
</script>
