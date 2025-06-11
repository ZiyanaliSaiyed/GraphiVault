import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

export const useVaultStore = defineStore('vault', () => {
  const images = ref<ImageFile[]>([])
  const selectedImages = ref<Set<string>>(new Set())
  const searchQuery = ref('')
  const selectedTags = ref<string[]>([])
  const isLoading = ref(false)

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
      // TODO: Implement file processing and encryption
      console.log('Adding images:', files)
    } catch (error) {
      console.error('Error adding images:', error)
    } finally {
      isLoading.value = false
    }
  }

  const deleteSelectedImages = async () => {
    // TODO: Implement image deletion
    console.log('Deleting images:', Array.from(selectedImages.value))
    selectedImages.value.clear()
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

  return {
    images,
    selectedImages,
    searchQuery,
    selectedTags,
    isLoading,
    filteredImages,
    allTags,
    addImages,
    deleteSelectedImages,
    toggleImageSelection,
    clearSelection
  }
})
