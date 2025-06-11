<template>
  <div class="min-h-screen bg-gradient-to-br from-base-100 to-base-200">
    <!-- Navigation Bar -->
    <nav class="navbar bg-base-100 shadow-lg border-b border-base-300">
      <div class="navbar-start">
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><RouterLink to="/vault">My Vault</RouterLink></li>
            <li><RouterLink to="/settings">Settings</RouterLink></li>
          </ul>
        </div>
        <RouterLink to="/" class="btn btn-ghost text-xl font-bold">
          🛡️ GraphiVault
        </RouterLink>
      </div>
      
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><RouterLink to="/vault" class="btn btn-ghost">My Vault</RouterLink></li>
          <li><RouterLink to="/settings" class="btn btn-ghost">Settings</RouterLink></li>
        </ul>
      </div>
      
      <div class="navbar-end">
        <ThemeToggle />
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero min-h-[80vh]">
      <div class="hero-content text-center">
        <div class="max-w-4xl">
          <div class="mb-8">
            <div class="text-6xl mb-4">🛡️</div>
            <h1 class="text-5xl font-bold text-gradient mb-6">
              Welcome to GraphiVault
            </h1>
            <p class="text-xl text-base-content/80 mb-8 max-w-2xl mx-auto">
              Your privacy-first, offline-first image vault. Store, encrypt, and manage your sensitive images with military-grade security.
            </p>
          </div>

          <!-- Feature Cards -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="card bg-base-100 shadow-xl card-hover">
              <div class="card-body">
                <div class="text-3xl mb-4">🔒</div>
                <h3 class="card-title text-lg justify-center">Military-Grade Encryption</h3>
                <p class="text-sm text-base-content/70">
                  AES-256 encryption ensures your images are secure from prying eyes.
                </p>
              </div>
            </div>

            <div class="card bg-base-100 shadow-xl card-hover">
              <div class="card-body">
                <div class="text-3xl mb-4">📱</div>
                <h3 class="card-title text-lg justify-center">100% Offline</h3>
                <p class="text-sm text-base-content/70">
                  No internet required. Your data never leaves your device.
                </p>
              </div>
            </div>

            <div class="card bg-base-100 shadow-xl card-hover">
              <div class="card-body">
                <div class="text-3xl mb-4">⚡</div>
                <h3 class="card-title text-lg justify-center">Lightning Fast</h3>
                <p class="text-sm text-base-content/70">
                  Built with Rust and Tauri for optimal performance.
                </p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <RouterLink to="/vault" class="btn btn-primary btn-lg">
              Open My Vault
              <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </RouterLink>
            <button class="btn btn-outline btn-lg" @click="showFeatures = !showFeatures">
              Learn More
            </button>
          </div>

          <!-- Additional Features (Collapsible) -->
          <div v-if="showFeatures" class="mt-12 fade-in">
            <div class="divider">Features</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div class="space-y-4">
                <div class="flex items-start space-x-3">
                  <div class="text-green-500 mt-1">✓</div>
                  <div>
                    <h4 class="font-semibold">Custom Metadata</h4>
                    <p class="text-sm text-base-content/70">Add tags, descriptions, and custom fields to organize your images.</p>
                  </div>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="text-green-500 mt-1">✓</div>
                  <div>
                    <h4 class="font-semibold">Advanced Search</h4>
                    <p class="text-sm text-base-content/70">Find images quickly with powerful search and filtering.</p>
                  </div>
                </div>
              </div>
              <div class="space-y-4">
                <div class="flex items-start space-x-3">
                  <div class="text-green-500 mt-1">✓</div>
                  <div>
                    <h4 class="font-semibold">Cross-Platform</h4>
                    <p class="text-sm text-base-content/70">Works on Windows, macOS, and Linux.</p>
                  </div>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="text-green-500 mt-1">✓</div>
                  <div>
                    <h4 class="font-semibold">Open Source</h4>
                    <p class="text-sm text-base-content/70">MIT licensed and community-driven development.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'

const showFeatures = ref(false)
</script>
