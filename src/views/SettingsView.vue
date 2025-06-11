<template>
  <div class="min-h-screen gv-vault-bg">
    <!-- Header - GraphiVault Style -->
    <nav class="gv-navbar fixed w-full top-0 z-50">
      <div class="container mx-auto px-6">
        <div class="flex items-center justify-between h-16">
          <RouterLink to="/" class="flex items-center space-x-3 group gv-transition-smooth hover:text-blue-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="gv-text-meta">BACK</span>
          </RouterLink>
          
          <div class="flex items-center space-x-3">
            <span class="text-2xl">⚙️</span>
            <h1 class="gv-heading-md gv-text-gradient font-mono">Settings</h1>
          </div>
          
          <ThemeToggle />
        </div>
      </div>
    </nav>    <!-- Settings Content -->
    <div class="pt-20 pb-16 px-6">
      <div class="container mx-auto max-w-4xl">
        <!-- Appearance Settings -->
        <div class="gv-card mb-8 p-8 animate-slide-up">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"/>
              </svg>
            </div>
            <h2 class="gv-heading-md text-blue-300">Interface</h2>
          </div>
          
          <div class="space-y-6">
            <div>
              <label class="block gv-text-meta mb-3">THEME PREFERENCE</label>
              <div class="flex gap-4">
                <label class="flex items-center space-x-3 cursor-pointer group">
                  <input
                    type="radio"
                    name="theme"
                    value="light"
                    :checked="themeStore.theme === 'graphivault-light'"
                    @change="() => themeStore.theme !== 'graphivault-light' && themeStore.toggleTheme()"
                    class="w-4 h-4 text-blue-500 border-gray-600 focus:ring-blue-500 focus:ring-2"
                  />
                  <span class="gv-text-body group-hover:text-blue-400 gv-transition-smooth">Light Mode</span>
                </label>
                <label class="flex items-center space-x-3 cursor-pointer group">
                  <input
                    type="radio"
                    name="theme"
                    value="dark"
                    :checked="themeStore.theme === 'graphivault'"
                    @change="() => themeStore.theme !== 'graphivault' && themeStore.toggleTheme()"
                    class="w-4 h-4 text-blue-500 border-gray-600 focus:ring-blue-500 focus:ring-2"
                  />
                  <span class="gv-text-body group-hover:text-blue-400 gv-transition-smooth">Dark Mode</span>
                </label>
              </div>
            </div>
          </div>
        </div>        <!-- Security Settings -->
        <div class="gv-card mb-8 p-8 animate-slide-up" style="animation-delay: 0.1s">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h2 class="gv-heading-md text-emerald-300">Security Protocol</h2>
          </div>
          
          <div class="space-y-6">
            <div>
              <label class="block gv-text-meta mb-3">AUTO-LOCK TIMEOUT</label>
              <select class="gv-input w-full max-w-xs">
                <option>Never</option>
                <option>5 minutes</option>
                <option>15 minutes</option>
                <option>30 minutes</option>
                <option>1 hour</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 border border-gray-700/50">
              <div>
                <span class="gv-text-body font-medium">Require authentication on startup</span>
                <p class="gv-text-meta text-xs mt-1">Force password entry when opening GraphiVault</p>
              </div>
              <input type="checkbox" class="w-5 h-5 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2" />
            </div>

            <div class="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 border border-gray-700/50">
              <div>
                <span class="gv-text-body font-medium">Clear clipboard after copying</span>
                <p class="gv-text-meta text-xs mt-1">Automatically clear sensitive data from clipboard</p>
              </div>
              <input type="checkbox" class="w-5 h-5 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2" checked />
            </div>
          </div>
        </div>        <!-- Storage Settings -->
        <div class="gv-card mb-8 p-8 animate-slide-up" style="animation-delay: 0.2s">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
              </svg>
            </div>
            <h2 class="gv-heading-md text-purple-300">Vault Storage</h2>
          </div>
          
          <!-- Storage Stats -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div class="p-4 rounded-lg bg-gray-900/50 border border-gray-700/50">
              <div class="flex items-center justify-between">
                <span class="gv-text-meta">TOTAL IMAGES</span>
                <span class="text-2xl font-bold text-blue-400">{{ vaultStore.images.length }}</span>
              </div>
            </div>
            <div class="p-4 rounded-lg bg-gray-900/50 border border-gray-700/50">
              <div class="flex items-center justify-between">
                <span class="gv-text-meta">STORAGE USED</span>
                <span class="text-2xl font-bold text-emerald-400">{{ formatStorageSize(totalStorageUsed) }}</span>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div>
              <label class="block gv-text-meta mb-3">VAULT LOCATION</label>
              <div class="flex gap-3">
                <input
                  type="text"
                  value="~/Documents/GraphiVault"
                  readonly
                  class="gv-input flex-1 font-mono text-sm"
                />
                <button class="gv-button-outline px-4 py-2 text-sm">Browse</button>
              </div>
            </div>

            <div class="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 border border-gray-700/50">
              <div>
                <span class="gv-text-body font-medium">Generate thumbnails automatically</span>
                <p class="gv-text-meta text-xs mt-1">Create preview images for faster vault navigation</p>
              </div>
              <input type="checkbox" class="w-5 h-5 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2" checked />
            </div>
          </div>
        </div>        <!-- About Section -->
        <div class="gv-card p-8 animate-slide-up" style="animation-delay: 0.3s">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-gray-700/50 border border-gray-600/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h2 class="gv-heading-md text-gray-300">System Information</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="p-4 rounded-lg bg-gray-900/30 border border-gray-700/30">
              <div class="gv-text-meta mb-1">VERSION</div>
              <div class="text-lg font-bold text-gray-200 font-mono">1.0.0</div>
            </div>
            <div class="p-4 rounded-lg bg-gray-900/30 border border-gray-700/30">
              <div class="gv-text-meta mb-1">BUILD</div>
              <div class="text-lg font-bold text-gray-200 font-mono">2025.06.11</div>
            </div>
            <div class="p-4 rounded-lg bg-gray-900/30 border border-gray-700/30">
              <div class="gv-text-meta mb-1">LICENSE</div>
              <div class="text-lg font-bold text-gray-200 font-mono">MIT</div>
            </div>
          </div>

          <div class="border-t border-gray-700/50 pt-6">
            <div class="flex flex-wrap gap-3">
              <button class="gv-button-outline text-sm">Check Updates</button>
              <button class="gv-button-outline text-sm">View Changelog</button>
              <button class="gv-button-outline text-sm">Report Issue</button>
              <button class="gv-button-outline text-sm">Export Logs</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { useVaultStore } from '../stores/vault'
import ThemeToggle from '../components/ThemeToggle.vue'

const themeStore = useThemeStore()
const vaultStore = useVaultStore()

const totalStorageUsed = computed(() => {
  return vaultStore.images.reduce((total, image) => total + image.size, 0)
})

const formatStorageSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
