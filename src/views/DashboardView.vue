<template>
  <div class="min-h-screen gv-vault-bg">
    <!-- Vault Unlock Screen -->
    <div v-if="vaultStore.isVaultLocked" class="flex items-center justify-center min-h-screen">
      <VaultUnlock 
        @vault-unlocked="handleVaultUnlocked"
        @vault-initialized="handleVaultInitialized"
      />
    </div>

    <!-- Dashboard Content (when vault is unlocked) -->
    <div v-else>
      <!-- Header - GraphiVault Style -->
      <nav class="gv-navbar fixed w-full top-0 z-50">
        <div class="container mx-auto px-6">
          <div class="flex items-center justify-between h-16">
            <RouterLink to="/" class="flex items-center space-x-3 group gv-transition-smooth hover:text-blue-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span class="gv-text-meta">HOME</span>
            </RouterLink>
            
            <div class="flex items-center space-x-3">
              <span class="text-2xl">🛡️</span>
              <h1 class="gv-heading-md gv-text-gradient font-mono">Dashboard</h1>
            </div>
            
            <div class="flex items-center space-x-3">
              <button 
                @click="handleLockVault"
                class="gv-button-outline px-4 py-2 text-sm"
                title="Lock Vault"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Lock
              </button>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </nav>

      <!-- Main Dashboard Content -->
      <div class="pt-20 pb-16 px-6">
        <div class="container mx-auto max-w-7xl">
          
          <!-- Welcome Section -->
          <div class="mb-8 animate-slide-up">
            <div class="gv-card p-8 border border-emerald-500/20 bg-gradient-to-r from-emerald-500/5 to-blue-500/5">
              <div class="flex items-center justify-between">
                <div>
                  <h2 class="gv-heading-lg text-emerald-300 mb-2">🔓 Vault Unlocked</h2>
                  <p class="gv-text-body text-gray-300">Welcome back! Your secure vault is ready for use.</p>
                  <p class="gv-text-meta text-gray-400 mt-1">Last accessed: {{ lastAccessTime }}</p>
                </div>
                <div class="text-6xl opacity-20">🛡️</div>
              </div>
            </div>
          </div>

          <!-- Statistics Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <!-- Total Images -->
            <div class="gv-card p-6 hover:border-blue-500/30 gv-transition-smooth animate-slide-up" style="animation-delay: 0.1s">
              <div class="flex items-center justify-between mb-4">
                <div class="w-12 h-12 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-blue-400">{{ vaultStore.images.length }}</div>
                  <div class="gv-text-meta">Total Images</div>
                </div>
              </div>
              <div class="text-xs text-gray-400">
                {{ vaultStore.images.length > 0 ? `+${recentlyAdded} this week` : 'Start adding images to your vault' }}
              </div>
            </div>

            <!-- Storage Used -->
            <div class="gv-card p-6 hover:border-emerald-500/30 gv-transition-smooth animate-slide-up" style="animation-delay: 0.2s">
              <div class="flex items-center justify-between mb-4">
                <div class="w-12 h-12 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-emerald-400">{{ formatStorageSize(totalStorageUsed) }}</div>
                  <div class="gv-text-meta">Storage Used</div>
                </div>
              </div>
              <div class="text-xs text-gray-400">Encrypted & compressed</div>
            </div>

            <!-- Security Status -->
            <div class="gv-card p-6 hover:border-purple-500/30 gv-transition-smooth animate-slide-up" style="animation-delay: 0.3s">
              <div class="flex items-center justify-between mb-4">
                <div class="w-12 h-12 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-purple-400">AES-256</div>
                  <div class="gv-text-meta">Security Level</div>
                </div>
              </div>
              <div class="text-xs text-green-400">✓ All systems secure</div>
            </div>

            <!-- Tags Count -->
            <div class="gv-card p-6 hover:border-orange-500/30 gv-transition-smooth animate-slide-up" style="animation-delay: 0.4s">
              <div class="flex items-center justify-between mb-4">
                <div class="w-12 h-12 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-orange-400">{{ vaultStore.allTags.length }}</div>
                  <div class="gv-text-meta">Tags Created</div>
                </div>
              </div>
              <div class="text-xs text-gray-400">Organize your collection</div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Actions Panel -->
            <div class="gv-card p-8 animate-slide-up" style="animation-delay: 0.5s">
              <div class="flex items-center space-x-3 mb-6">
                <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 class="gv-heading-md text-blue-300">Quick Actions</h3>
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <RouterLink 
                  to="/vault" 
                  class="gv-card p-4 hover:border-blue-500/40 gv-transition-smooth group cursor-pointer"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-blue-400 group-hover:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <div>
                      <div class="gv-text-body font-medium group-hover:text-blue-300">Browse Vault</div>
                      <div class="gv-text-meta text-xs">View all images</div>
                    </div>
                  </div>
                </RouterLink>

                <button 
                  @click="triggerFileUpload"
                  class="gv-card p-4 hover:border-emerald-500/40 gv-transition-smooth group cursor-pointer"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-emerald-400 group-hover:text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <div>
                      <div class="gv-text-body font-medium group-hover:text-emerald-300">Add Images</div>
                      <div class="gv-text-meta text-xs">Upload new files</div>
                    </div>
                  </div>
                </button>

                <RouterLink 
                  to="/settings" 
                  class="gv-card p-4 hover:border-purple-500/40 gv-transition-smooth group cursor-pointer"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-purple-400 group-hover:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <div>
                      <div class="gv-text-body font-medium group-hover:text-purple-300">Settings</div>
                      <div class="gv-text-meta text-xs">Configure vault</div>
                    </div>
                  </div>
                </RouterLink>

                <button 
                  @click="performSearch"
                  class="gv-card p-4 hover:border-orange-500/40 gv-transition-smooth group cursor-pointer"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="w-5 h-5 text-orange-400 group-hover:text-orange-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <div>
                      <div class="gv-text-body font-medium group-hover:text-orange-300">Search</div>
                      <div class="gv-text-meta text-xs">Find images</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="gv-card p-8 animate-slide-up" style="animation-delay: 0.6s">
              <div class="flex items-center space-x-3 mb-6">
                <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 class="gv-heading-md text-emerald-300">Recent Activity</h3>
              </div>
              
              <div v-if="recentImages.length > 0" class="space-y-3">
                <div 
                  v-for="image in recentImages" 
                  :key="image.id"
                  class="flex items-center space-x-3 p-3 rounded-lg bg-gray-900/30 border border-gray-700/30 hover:border-gray-600/50 gv-transition-smooth"
                >
                  <div class="w-10 h-10 rounded-lg bg-gray-700/50 flex items-center justify-center">
                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <div class="gv-text-body text-sm font-medium">{{ image.name }}</div>
                    <div class="gv-text-meta text-xs">Added {{ formatRelativeTime(image.dateAdded) }}</div>
                  </div>
                  <div class="text-xs px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {{ formatFileSize(image.size) }}
                  </div>
                </div>
              </div>
              
              <div v-else class="text-center py-8">
                <div class="text-4xl mb-3">📷</div>
                <div class="gv-text-body text-gray-400">No images yet</div>
                <div class="gv-text-meta text-xs text-gray-500 mt-1">Upload your first image to get started</div>
              </div>
            </div>
          </div>

          <!-- Security Status -->
          <div class="gv-card p-8 animate-slide-up" style="animation-delay: 0.7s">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 class="gv-heading-md text-green-300">Security Status</h3>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                <div>
                  <div class="gv-text-body text-sm font-medium">Encryption Active</div>
                  <div class="gv-text-meta text-xs">AES-256-GCM with PBKDF2</div>
                </div>
              </div>
              
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                <div>
                  <div class="gv-text-body text-sm font-medium">Offline Mode</div>
                  <div class="gv-text-meta text-xs">No network dependencies</div>
                </div>
              </div>
              
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                <div>
                  <div class="gv-text-body text-sm font-medium">Session Protected</div>
                  <div class="gv-text-meta text-xs">Auto-lock configured</div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Hidden File Input for Upload -->
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        class="hidden"
        @change="handleFileUpload"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useVaultStore } from '../stores/vault'
import { tauriAPI } from '../utils/tauri'
import ThemeToggle from '../components/ThemeToggle.vue'
import VaultUnlock from '../components/VaultUnlock.vue'

const router = useRouter()
const vaultStore = useVaultStore()
const fileInput = ref<HTMLInputElement>()

// Computed properties
const totalStorageUsed = computed(() => {
  return vaultStore.images.reduce((total, image) => total + image.size, 0)
})

const recentImages = computed(() => {
  return [...vaultStore.images]
    .sort((a, b) => new Date(b.dateAdded).getTime() - new Date(a.dateAdded).getTime())
    .slice(0, 5)
})

const recentlyAdded = computed(() => {
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  return vaultStore.images.filter(img => new Date(img.dateAdded) > oneWeekAgo).length
})

const lastAccessTime = ref(new Date().toLocaleString())

// Methods
const formatStorageSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatRelativeTime = (date: Date): string => {
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return

  try {
    for (const file of Array.from(files)) {
      // Create a temporary file path (in a real app, this would be handled differently)
      const tempPath = URL.createObjectURL(file)
      
      // Extract tags from filename or use default tags
      const tags = ['imported', 'dashboard-upload']
      
      // Process the image through the Python backend
      const result = await tauriAPI.processImageFile(tempPath, tags)
      
      if (result.success) {
        console.log('Image processed successfully:', result.data)
      } else {
        console.error('Failed to process image:', result.error)
      }
    }
    
    // Refresh the vault contents
    await vaultStore.refreshImages()
    
    // Clear the input
    target.value = ''
  } catch (error) {
    console.error('Error processing files:', error)
  }
}

const performSearch = () => {
  router.push('/vault')
  // Focus on search input when navigating to vault
  setTimeout(() => {
    const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement
    searchInput?.focus()
  }, 100)
}

const handleLockVault = async () => {
  try {
    const result = await tauriAPI.lockVault()
    if (result.success) {
      vaultStore.setVaultLocked(true)
      vaultStore.clearImages()
      router.push('/vault')
    }
  } catch (error) {
    console.error('Failed to lock vault:', error)
  }
}

// Add authentication handlers
const handleVaultUnlocked = async () => {
  console.log('Vault unlocked successfully')
  await vaultStore.refreshImages()
}

const handleVaultInitialized = async () => {
  console.log('Vault initialized successfully')
  await vaultStore.refreshImages()
}

// Initialize dashboard data
onMounted(async () => {
  await vaultStore.refreshImages()
})
</script>
