<template>
  <div class="relative">
    <input
      ref="fileInput"
      type="file"
      multiple
      accept="image/*"
      class="hidden"
      @change="handleFileChange"
    />
    
    <button
      @click="openFileDialog"
      class="btn btn-primary"
      :disabled="isUploading"
    >
      <svg v-if="!isUploading" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      <span v-if="isUploading" class="loading loading-spinner loading-sm mr-2"></span>
      {{ isUploading ? 'Processing...' : 'Add Images' }}
    </button>

    <!-- Drag and Drop Overlay -->
    <div
      v-if="isDragOver"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @drop.prevent="handleDrop"
      @dragover.prevent
      @dragleave="isDragOver = false"
    >
      <div class="bg-base-100 rounded-lg p-8 text-center max-w-md">
        <div class="text-4xl mb-4">📁</div>
        <h3 class="text-xl font-bold mb-2">Drop your images here</h3>
        <p class="text-base-content/70">Release to add them to your vault</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { addImage } from '@/utils/tauri'
import { useVaultStore } from '@/stores/vault'

interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  filesSelected: [files: File[]]
}>()

const vaultStore = useVaultStore()

const fileInput = ref<HTMLInputElement>()
const isUploading = ref(false)
const isDragOver = ref(false)

const openFileDialog = () => {
  if (props.disabled || isUploading.value) return
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    processFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  
  if (props.disabled || isUploading.value) return
  
  const files = Array.from(event.dataTransfer?.files || [])
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (imageFiles.length > 0) {
    processFiles(imageFiles)
  }
}

const processFiles = async (files: File[]) => {
  if (files.length === 0) return
  
  isUploading.value = true
  
  try {
    // Validate file types and sizes
    const validFiles = files.filter(file => {
      const isValidType = file.type.startsWith('image/')
      const isValidSize = file.size <= 50 * 1024 * 1024 // 50MB limit
      
      if (!isValidType) {
        console.warn(`Skipping ${file.name}: Not an image file`)
      }
      if (!isValidSize) {
        console.warn(`Skipping ${file.name}: File too large (max 50MB)`)
      }
      
      return isValidType && isValidSize
    })
    
    if (validFiles.length > 0) {
      // Process each file
      for (const file of validFiles) {
        try {
          // Read the file as a base64 string
          const base64String = await readFileAsBase64(file)
          console.log(`Converting ${file.name} to base64`)
          
          // Set default tags
          const tags = ['imported', 'dashboard-upload']
          
          console.log(`Uploading ${file.name} with tags:`, tags)
          
          // Call the backend to add the image
          await addImage(base64String, tags, vaultStore.vaultPassword || undefined)
          
          console.log(`Successfully uploaded ${file.name}`)
        } catch (error) {
          console.error(`Error processing file ${file.name}:`, error)
        }
      }
      
      // Emit the event for the parent component
      emit('filesSelected', validFiles)
    }
  } catch (error) {
    console.error('Error processing files:', error)
  } finally {
    isUploading.value = false
    // Clear the input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

// Helper function to read a file as a base64 string
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      if (event.target?.result) {
        // The result will be in the format: "data:image/png;base64,iVBORw0KGgo..."
        // We need to strip the prefix "data:image/png;base64,"
        const base64String = (event.target.result as string).split(',')[1]
        resolve(base64String)
      } else {
        reject(new Error('Failed to read file'))
      }
    }
    reader.onerror = (error) => {
      reject(error)
    }
    reader.readAsDataURL(file)
  })
}

const handleGlobalDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleGlobalDragLeave = (event: DragEvent) => {
  // Only hide if leaving the window
  if (!event.relatedTarget) {
    isDragOver.value = false
  }
}

onMounted(() => {
  document.addEventListener('dragover', handleGlobalDragOver)
  document.addEventListener('dragleave', handleGlobalDragLeave)
})

onUnmounted(() => {
  document.removeEventListener('dragover', handleGlobalDragOver)
  document.removeEventListener('dragleave', handleGlobalDragLeave)
})
</script>
