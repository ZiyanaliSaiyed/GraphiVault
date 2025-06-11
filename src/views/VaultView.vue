<template>
  <div class="min-h-screen bg-base-100">
    <!-- Header -->
    <div class="navbar bg-base-100 shadow-lg border-b border-base-300">
      <div class="navbar-start">
        <RouterLink to="/" class="btn btn-ghost">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </RouterLink>
      </div>
      <div class="navbar-center">
        <h1 class="text-xl font-bold">🛡️ My Vault</h1>
      </div>
      <div class="navbar-end">
        <ThemeToggle />
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-6">
      <!-- Toolbar -->
      <div class="flex flex-col lg:flex-row gap-4 mb-6">
        <!-- Search -->
        <div class="flex-1">
          <div class="form-control">
            <div class="input-group">
              <input
                v-model="vaultStore.searchQuery"
                type="text"
                placeholder="Search images..."
                class="input input-bordered w-full"
              />
              <button class="btn btn-square">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <FileUpload @files-selected="handleFilesSelected" />
          <button
            v-if="vaultStore.selectedImages.size > 0"
            @click="handleDelete"
            class="btn btn-error"
          >
            Delete Selected ({{ vaultStore.selectedImages.size }})
          </button>
          <button @click="vaultStore.clearSelection" class="btn btn-outline">
            Clear Selection
          </button>
        </div>
      </div>

      <!-- Tags Filter -->
      <div v-if="vaultStore.allTags.length > 0" class="mb-6">
        <div class="flex flex-wrap gap-2">
          <span class="text-sm font-medium text-base-content/70">Filter by tags:</span>
          <button
            v-for="tag in vaultStore.allTags"
            :key="tag"
            @click="toggleTagFilter(tag)"
            :class="[
              'badge badge-outline badge-sm cursor-pointer',
              vaultStore.selectedTags.includes(tag) ? 'badge-primary' : ''
            ]"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Image Grid -->
      <div v-if="vaultStore.filteredImages.length > 0" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <ImageCard
          v-for="image in vaultStore.filteredImages"
          :key="image.id"
          :image="image"
          :selected="vaultStore.selectedImages.has(image.id)"
          @toggle-select="vaultStore.toggleImageSelection"
        />
      </div>

      <!-- Empty State -->
      <div v-else-if="!vaultStore.isLoading" class="text-center py-12">
        <div class="text-6xl mb-4">📁</div>
        <h3 class="text-2xl font-bold mb-2">Your vault is empty</h3>
        <p class="text-base-content/70 mb-6">
          {{ vaultStore.searchQuery || vaultStore.selectedTags.length > 0 
             ? 'No images match your search criteria' 
             : 'Start by adding some images to your secure vault' }}
        </p>
        <FileUpload @files-selected="handleFilesSelected" />
      </div>

      <!-- Loading State -->
      <div v-if="vaultStore.isLoading" class="text-center py-12">
        <div class="loading loading-spinner loading-lg"></div>
        <p class="mt-4">Processing images...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useVaultStore } from '../stores/vault'
import ThemeToggle from '../components/ThemeToggle.vue'
import FileUpload from '../components/FileUpload.vue'
import ImageCard from '../components/ImageCard.vue'

const vaultStore = useVaultStore()

const handleFilesSelected = (files: File[]) => {
  vaultStore.addImages(files)
}

const handleDelete = () => {
  if (confirm(`Are you sure you want to delete ${vaultStore.selectedImages.size} image(s)?`)) {
    vaultStore.deleteSelectedImages()
  }
}

const toggleTagFilter = (tag: string) => {
  const index = vaultStore.selectedTags.indexOf(tag)
  if (index > -1) {
    vaultStore.selectedTags.splice(index, 1)
  } else {
    vaultStore.selectedTags.push(tag)
  }
}
</script>
