<template>
  <div class="vault-unlock-container p-6 max-w-md mx-auto bg-gv-secondary rounded-lg shadow-lg">
    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold text-gv-text mb-2">
        {{ isInitialized ? 'Unlock Vault' : 'Initialize Vault' }}
      </h2>
      <p class="text-gv-text-muted">
        {{ isInitialized ? 'Enter your master password to access your encrypted vault.' : 'Create a master password to initialize your new vault.' }}
      </p>
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="password" class="block text-sm font-medium text-gv-text mb-2">
          Master Password
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          class="w-full px-3 py-2 border border-gv-border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-gv-accent focus:border-gv-accent bg-gv-primary text-gv-text"
          :disabled="isLoading"
          placeholder="Enter your master password"
          @keyup.enter="handleSubmit"
        />
      </div>
      
      <div v-if="!isInitialized">
        <label for="confirmPassword" class="block text-sm font-medium text-gv-text mb-2">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          type="password"
          required
          class="w-full px-3 py-2 border border-gv-border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-gv-accent focus:border-gv-accent bg-gv-primary text-gv-text"
          :disabled="isLoading"
          placeholder="Confirm your master password"
          @keyup.enter="handleSubmit"
        />
      </div>
      
      <button
        type="submit"
        :disabled="isLoading || !isPasswordValid"
        class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gv-accent hover:bg-gv-accent-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gv-accent disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isInitialized ? 'Unlocking...' : 'Initializing...' }}
        </span>
        <span v-else>
          {{ isInitialized ? 'Unlock Vault' : 'Initialize Vault' }}
        </span>
      </button>
    </form>
    
    <div v-if="errorMessage" class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ errorMessage }}
    </div>
    
    <div v-if="successMessage" class="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
      {{ successMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { tauriAPI } from '../utils/tauri'
import { useVaultStore } from '../stores/vault'

const emit = defineEmits<{
  vaultUnlocked: []
  vaultInitialized: []
}>()

const vaultStore = useVaultStore()

const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isInitialized = ref(false)

const isPasswordValid = computed(() => {
  const hasPassword = password.value && password.value.length >= 3 // Relaxed for testing
  console.log('🔑 Password validation check:', {
    hasPassword,
    passwordLength: password.value?.length || 0,
    isInitialized: isInitialized.value,
    confirmPasswordMatch: !isInitialized.value ? password.value === confirmPassword.value : true
  })
  
  if (!hasPassword) return false
  
  if (!isInitialized.value) {
    // For new vault, passwords must match and be at least 3 chars (relaxed for testing)
    return password.value === confirmPassword.value && password.value.length >= 3
  }
  
  // For existing vault, just need the password
  return password.value.length >= 3
})

const checkVaultStatus = async () => {
  try {
    console.log('🔍 Checking vault status...')
    // Check if vault is already initialized by trying to get vault info
    const vaultInfo = await tauriAPI.getVaultInfo()
    console.log('📊 Vault info:', vaultInfo)
    isInitialized.value = vaultInfo.status === 'active' || vaultInfo.total_images >= 0
    console.log('🏁 Vault initialization status:', isInitialized.value)
  } catch (error) {
    console.log('⚠️ Could not get vault info, assuming uninitialized:', error)
    // If we can't get vault info, assume it needs to be initialized
    isInitialized.value = false
  }
}

const handleSubmit = async () => {
  console.log('🔐 Vault unlock attempt started', {
    password: password.value ? '***' : 'empty',
    isPasswordValid: isPasswordValid.value,
    isInitialized: isInitialized.value,
    isLoading: isLoading.value
  })
  
  if (!isPasswordValid.value) {
    console.log('❌ Password validation failed')
    return
  }
  
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    let result
    
    if (isInitialized.value) {
      // Unlock existing vault
      console.log('🔓 Attempting to unlock existing vault...')
      result = await tauriAPI.unlockVault(password.value)
    } else {
      // Initialize new vault
      console.log('🆕 Attempting to initialize new vault...')
      result = await tauriAPI.initializeVault(password.value)
    }
    
    console.log('🔐 Backend response:', result)
    
    if (result.success) {
      successMessage.value = result.message || 'Operation completed successfully'
      
      // Update vault store state
      console.log('✅ Updating vault store state to unlocked')
      vaultStore.setVaultLocked(false)
      
      // Emit appropriate event
      if (isInitialized.value) {
        console.log('📢 Emitting vaultUnlocked event')
        emit('vaultUnlocked')
      } else {
        console.log('📢 Emitting vaultInitialized event')
        emit('vaultInitialized')
        isInitialized.value = true
      }
      
      // Clear form
      password.value = ''
      confirmPassword.value = ''
      
    } else {
      console.log('❌ Operation failed:', result.error)
      errorMessage.value = result.error || 'Operation failed'
    }
    
  } catch (error) {
    console.error('💥 Vault operation error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
    console.log('🔐 Vault unlock attempt finished')
  }
}

onMounted(() => {
  checkVaultStatus()
})
</script>

<style scoped>
.vault-unlock-container {
  min-height: 400px;
}
</style>
