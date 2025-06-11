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
        <h1 class="text-xl font-bold">⚙️ Settings</h1>
      </div>
      <div class="navbar-end">
        <ThemeToggle />
      </div>
    </div>

    <!-- Settings Content -->
    <div class="container mx-auto px-4 py-6 max-w-4xl">
      <!-- General Settings -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">🎨 Appearance</h2>
          
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-medium">Theme</span>
            </label>
            <div class="flex gap-4">
              <label class="label cursor-pointer">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  :checked="themeStore.theme === 'light'"
                  @change="() => themeStore.theme !== 'light' && themeStore.toggleTheme()"
                  class="radio radio-primary"
                />
                <span class="label-text ml-2">Light</span>
              </label>
              <label class="label cursor-pointer">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  :checked="themeStore.theme === 'dark'"
                  @change="() => themeStore.theme !== 'dark' && themeStore.toggleTheme()"
                  class="radio radio-primary"
                />
                <span class="label-text ml-2">Dark</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">🔒 Security</h2>
          
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-medium">Auto-lock after inactivity</span>
            </label>
            <select class="select select-bordered w-full max-w-xs">
              <option>Never</option>
              <option>5 minutes</option>
              <option>15 minutes</option>
              <option>30 minutes</option>
              <option>1 hour</option>
            </select>
          </div>

          <div class="form-control mb-4">
            <label class="label cursor-pointer">
              <span class="label-text font-medium">Require password on startup</span>
              <input type="checkbox" class="checkbox checkbox-primary" />
            </label>
          </div>

          <div class="form-control mb-4">
            <label class="label cursor-pointer">
              <span class="label-text font-medium">Clear clipboard after copying</span>
              <input type="checkbox" class="checkbox checkbox-primary" checked />
            </label>
          </div>
        </div>
      </div>

      <!-- Storage Settings -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">💾 Storage</h2>
          
          <div class="stats shadow w-full mb-4">
            <div class="stat">
              <div class="stat-title">Total Images</div>
              <div class="stat-value text-primary">{{ vaultStore.images.length }}</div>
            </div>
            <div class="stat">
              <div class="stat-title">Storage Used</div>
              <div class="stat-value text-secondary">{{ formatStorageSize(totalStorageUsed) }}</div>
            </div>
          </div>

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-medium">Vault location</span>
            </label>
            <div class="input-group">
              <input
                type="text"
                value="~/Documents/GraphiVault"
                readonly
                class="input input-bordered flex-1"
              />
              <button class="btn btn-outline">Change</button>
            </div>
          </div>

          <div class="form-control mb-4">
            <label class="label cursor-pointer">
              <span class="label-text font-medium">Automatically generate thumbnails</span>
              <input type="checkbox" class="checkbox checkbox-primary" checked />
            </label>
          </div>
        </div>
      </div>

      <!-- About -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">ℹ️ About</h2>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="font-medium">Version</span>
              <span>1.0.0</span>
            </div>
            <div class="flex justify-between">
              <span class="font-medium">Build</span>
              <span>2025.06.11</span>
            </div>
            <div class="flex justify-between">
              <span class="font-medium">License</span>
              <span>MIT</span>
            </div>
          </div>

          <div class="divider"></div>

          <div class="flex gap-2">
            <button class="btn btn-outline btn-sm">Check for Updates</button>
            <button class="btn btn-outline btn-sm">View Changelog</button>
            <button class="btn btn-outline btn-sm">Report Issue</button>
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
