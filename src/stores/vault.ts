import { defineStore } from 'pinia'
import { ref, computed, onMounted } from 'vue'
import { tauriAPI, isTauri } from '../utils/tauri'
import type { ImageRecord } from '../types/database'

export interface ImageFile {
  id: string
  name: string
  path: string
  size: number
  type: string
  dateAdded: Date
  dateModified: Date
  tags: string[]
  metadata: Record<string, any>
  isEncrypted: boolean
  thumbnailPath?: string
}

// Convert ImageRecord to ImageFile
const convertImageRecord = (record: ImageRecord): ImageFile => ({
  id: record.id.toString(),
  name: record.file_name,
  path: record.storage_path,
  size: record.file_size,
  type: 'image/jpeg', // Default type, would be determined from file
  dateAdded: new Date(record.created_at),
  dateModified: new Date(record.updated_at),
  tags: [], // Tags would be loaded separately
  metadata: {},
  isEncrypted: true, // All images in vault are encrypted
  thumbnailPath: undefined
})

export const useVaultStore = defineStore('vault', () => {
  const images = ref<ImageFile[]>([])
  const selectedImages = ref<Set<string>>(new Set())
  const searchQuery = ref('')
  const selectedTags = ref<string[]>([])
  const isLoading = ref(false)
  const isVaultLocked = ref(true)
  const searchResults = ref<any[]>([])
  
  // Session storage for vault password (in memory only, cleared on page refresh)
  const vaultPassword = ref<string | null>(null)

  const filteredImages = computed(() => {
    let filtered = images.value

    // Filter by search query
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(img =>
        img.name.toLowerCase().includes(query) ||
        img.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }

    // Filter by selected tags
    if (selectedTags.value.length > 0) {
      filtered = filtered.filter(img =>
        selectedTags.value.every(tag => img.tags.includes(tag))
      )
    }

    return filtered
  })
  const allTags = computed(() => {
    const tags = new Set<string>()
    images.value.forEach(img => {
      img.tags.forEach(tag => tags.add(tag))
    })
    return Array.from(tags).sort()
  })
  
  const addImages = async (files: File[]) => {
    isLoading.value = true
    try {
      for (const file of files) {
        // Calculate basic file hash (in real implementation, would be more robust)
        const fileHash = `hash_${Date.now()}_${Math.random()}`
        
        const imageId = await tauriAPI.addImage(
          fileHash,
          file.name,
          file.name, // storage path
          file.size
        )
        
        // Create ImageFile from the data we have
        const imageFile: ImageFile = {
          id: imageId.toString(),
          name: file.name,
          path: file.name,
          size: file.size,
          type: file.type,
          dateAdded: new Date(),
          dateModified: new Date(file.lastModified),
          tags: [],
          metadata: {
            webkitRelativePath: (file as any).webkitRelativePath || ''
          },
          isEncrypted: true,
          thumbnailPath: undefined
        }
        
        images.value.push(imageFile)
      }
    } catch (error) {
      console.error('Error adding images:', error)
    } finally {
      isLoading.value = false
    }
  }

  const loadImages = async () => {
    isLoading.value = true
    try {
      const imageRecords = await tauriAPI.getImages()
      images.value = imageRecords.map(convertImageRecord)
    } catch (error) {
      console.error('Error loading images:', error)
    } finally {
      isLoading.value = false
    }
  }

  const setVaultLocked = (locked: boolean) => {
    isVaultLocked.value = locked
    // Clear password when vault is locked
    if (locked) {
      vaultPassword.value = null
    }
  }
  
  const setVaultPassword = (password: string | null) => {
    vaultPassword.value = password
  }

  const clearImages = () => {
    images.value = []
    selectedImages.value.clear()
    searchResults.value = []
  }

  const setSearchResults = (results: any[]) => {
    searchResults.value = results
  }

  const refreshImages = async () => {
    isLoading.value = true
    try {
      console.log('🔄 Refreshing vault images...')
      
      // Try to get all images through search
      const result = await tauriAPI.searchImages('', [])
      
      if (result.success) {
        if (result.data?.results) {
          console.log(`✅ Found ${result.data.results.length} images in vault`)
          
          // Convert backend results to ImageFile format
          images.value = result.data.results.map((result: any) => ({
            id: result.id,
            name: result.name,
            path: '', // Will be loaded on demand
            size: result.size,
            type: result.mime_type,
            dateAdded: new Date(result.date_added),
            dateModified: new Date(result.date_added),
            tags: result.tags || [],
            metadata: result.metadata || {},
            isEncrypted: result.is_encrypted,
            thumbnailPath: result.thumbnail_path
          }))
        } else {
          console.log('📭 No images found in vault')
          images.value = []
        }
      } else {
        console.error('❌ Failed to refresh images:', result.error)
        // Try fallback method if available
        images.value = []
      }
    } catch (error) {
      console.error('❌ Error refreshing images:', error)
      images.value = []
    } finally {
      isLoading.value = false
    }
  }

  const deleteSelectedImages = async () => {
    isLoading.value = true
    try {
      // Delete images using the backend (not implemented in current IPC gateway)
      // For now, just remove from local state
      const imagesToDelete = Array.from(selectedImages.value)
      images.value = images.value.filter(img => !imagesToDelete.includes(img.id))
      selectedImages.value.clear()
    } catch (error) {
      console.error('Error deleting images:', error)
    } finally {
      isLoading.value = false
    }
  }

  const toggleImageSelection = (id: string) => {
    if (selectedImages.value.has(id)) {
      selectedImages.value.delete(id)
    } else {
      selectedImages.value.add(id)
    }
  }
  const clearSelection = () => {
    selectedImages.value.clear()
  }

  // Initialize data when store is created
  const initialize = async () => {
    try {
      await tauriAPI.initDatabase()
      await loadImages()
    } catch (error) {
      console.error('Error initializing vault store:', error)
    }
  }
  return {
    // State
    images,
    selectedImages,
    searchQuery,
    selectedTags,
    isLoading,
    isVaultLocked,
    searchResults,
    vaultPassword,
    
    // Computed
    filteredImages,
    allTags,
    
    // Actions
    addImages,
    loadImages,
    toggleImageSelection,
    clearSelection,
    initialize,
    setVaultLocked,
    setVaultPassword,
    clearImages,
    setSearchResults,
    refreshImages,
    deleteSelectedImages
  }
})
