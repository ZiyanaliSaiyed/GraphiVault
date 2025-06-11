<template>
  <div class="min-h-screen gv-vault-bg">
    <!-- Navigation Bar - Minimalist & Dark -->
    <nav class="gv-navbar fixed w-full top-0 z-50">
      <div class="container mx-auto px-6">
        <div class="flex items-center justify-between h-16">
          <!-- Logo/Brand -->
          <RouterLink to="/" class="flex items-center space-x-3 group">
            <div class="text-2xl gv-transition-smooth group-hover:animate-glow">🛡️</div>
            <span class="gv-heading-md gv-text-gradient font-mono">GraphiVault</span>
          </RouterLink>
          
          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-1">
            <RouterLink to="/vault" class="gv-text-meta hover:text-blue-400 px-4 py-2 rounded-lg gv-transition-smooth hover:bg-gray-800/50">
              VAULT
            </RouterLink>
            <RouterLink to="/settings" class="gv-text-meta hover:text-blue-400 px-4 py-2 rounded-lg gv-transition-smooth hover:bg-gray-800/50">
              SETTINGS
            </RouterLink>
            <ThemeToggle />
          </div>
          
          <!-- Mobile Menu Button -->
          <button @click="showMobileMenu = !showMobileMenu" class="md:hidden p-2 rounded-lg hover:bg-gray-800/50 gv-transition-smooth">
            <svg class="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Menu -->
        <div v-if="showMobileMenu" class="md:hidden py-4 border-t border-gray-800 animate-slide-up">
          <div class="flex flex-col space-y-2">
            <RouterLink to="/vault" class="gv-text-meta hover:text-blue-400 px-4 py-3 rounded-lg gv-transition-smooth hover:bg-gray-800/50">
              VAULT
            </RouterLink>
            <RouterLink to="/settings" class="gv-text-meta hover:text-blue-400 px-4 py-3 rounded-lg gv-transition-smooth hover:bg-gray-800/50">
              SETTINGS
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>    <!-- Hero Section - Stoic Digital Vault Assistant -->
    <div class="pt-20 pb-16 px-6">
      <div class="container mx-auto max-w-6xl">
        <div class="text-center mb-16">
          <!-- Vault Icon with Animation -->
          <div class="mb-8 animate-vault-lock">
            <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-500/20 to-emerald-500/20 border border-blue-500/30 shadow-glow-blue">
              <span class="text-5xl">🛡️</span>
            </div>
          </div>
          
          <!-- Main Heading -->
          <h1 class="gv-heading-xl mb-6 animate-fade-in">
            <span class="gv-text-gradient">Privacy-First</span><br>
            <span class="text-gray-200">Digital Vault</span>
          </h1>
          
          <!-- Subtitle -->
          <p class="gv-text-body max-w-3xl mx-auto mb-8 text-lg leading-relaxed animate-slide-in">
            Military-grade encryption meets elegant design. Store, organize, and protect your sensitive images with <strong class="text-blue-400">zero compromise</strong> on privacy or performance.
          </p>
          
          <!-- Core Values -->
          <div class="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up">
            <div class="flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-900/50 border border-gray-700/50">
              <div class="w-2 h-2 bg-emerald-400 rounded-full"></div>
              <span class="gv-text-meta text-emerald-400">OFFLINE-FIRST</span>
            </div>
            <div class="flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-900/50 border border-gray-700/50">
              <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
              <span class="gv-text-meta text-blue-400">AES-256 ENCRYPTED</span>
            </div>
            <div class="flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-900/50 border border-gray-700/50">
              <div class="w-2 h-2 bg-purple-400 rounded-full"></div>
              <span class="gv-text-meta text-purple-400">OPEN SOURCE</span>
            </div>
          </div>
        </div>        <!-- Feature Grid - Precision Tool Showcase -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <!-- Military-Grade Encryption -->
          <div class="gv-card gv-card-hover p-8 text-center group animate-slide-up" style="animation-delay: 0.1s">
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-blue-500/10 border border-blue-500/20 group-hover:border-blue-500/40 gv-transition-smooth">
                <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
            </div>
            <h3 class="gv-heading-md mb-4 text-blue-300">Quantum-Safe Encryption</h3>
            <p class="gv-text-body text-sm">
              AES-256 with future-proof cryptographic standards. Your images remain secure against current and emerging threats.
            </p>
          </div>

          <!-- 100% Offline -->
          <div class="gv-card gv-card-hover p-8 text-center group animate-slide-up" style="animation-delay: 0.2s">
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-emerald-500/10 border border-emerald-500/20 group-hover:border-emerald-500/40 gv-transition-smooth">
                <svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"/>
                </svg>
              </div>
            </div>
            <h3 class="gv-heading-md mb-4 text-emerald-300">Air-Gapped Security</h3>
            <p class="gv-text-body text-sm">
              Complete offline operation. No telemetry, no cloud dependencies. Your data never touches external servers.
            </p>
          </div>

          <!-- Lightning Performance -->
          <div class="gv-card gv-card-hover p-8 text-center group animate-slide-up" style="animation-delay: 0.3s">
            <div class="mb-6">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-purple-500/10 border border-purple-500/20 group-hover:border-purple-500/40 gv-transition-smooth">
                <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
            </div>
            <h3 class="gv-heading-md mb-4 text-purple-300">Rust-Powered Engine</h3>
            <p class="gv-text-body text-sm">
              Native performance with Tauri's Rust backend. Memory-safe, lightning-fast, and resource-efficient.
            </p>
          </div>
        </div>        <!-- Action Buttons - Mission Control -->
        <div class="flex flex-col sm:flex-row gap-6 justify-center items-center mb-20">
          <RouterLink to="/vault" class="gv-button-primary group">
            <span class="mr-3">Enter Vault</span>
            <svg class="w-5 h-5 gv-transition-smooth group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </RouterLink>
          
          <button @click="showFeatures = !showFeatures" class="gv-button-outline group">
            <span class="mr-3">Technical Details</span>
            <svg class="w-5 h-5 gv-transition-smooth" :class="{'rotate-180': showFeatures}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>
    </div>    <!-- Technical Details Section - Expandable -->
    <div v-if="showFeatures" class="px-6 pb-16 animate-slide-up">
      <div class="container mx-auto max-w-6xl">
        <!-- Section Divider -->
        <div class="flex items-center mb-12">
          <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent"></div>
          <div class="px-6">
            <span class="gv-text-meta text-blue-400">TECHNICAL SPECIFICATIONS</span>
          </div>
          <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-600 to-transparent"></div>
        </div>
        
        <!-- Features Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Left Column -->
          <div class="space-y-6">
            <!-- Advanced Metadata -->
            <div class="gv-card p-6 hover:border-blue-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Smart Metadata System</h4>
                  <p class="gv-text-body text-sm">Custom tags, EXIF preservation, and semantic search across encrypted collections.</p>
                </div>
              </div>
            </div>

            <!-- Advanced Search -->
            <div class="gv-card p-6 hover:border-emerald-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Neural Search Engine</h4>
                  <p class="gv-text-body text-sm">Find images by content, color palette, or semantic meaning using local AI processing.</p>
                </div>
              </div>
            </div>

            <!-- Zero-Knowledge Architecture -->
            <div class="gv-card p-6 hover:border-purple-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Zero-Knowledge Design</h4>
                  <p class="gv-text-body text-sm">Even we can't see your data. Client-side encryption with user-controlled keys.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-6">
            <!-- Cross-Platform -->
            <div class="gv-card p-6 hover:border-cyan-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Universal Compatibility</h4>
                  <p class="gv-text-body text-sm">Windows, macOS, Linux. One vault format, synchronized security across all platforms.</p>
                </div>
              </div>
            </div>

            <!-- Open Source -->
            <div class="gv-card p-6 hover:border-orange-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Transparent & Auditable</h4>
                  <p class="gv-text-body text-sm">MIT licensed. Every line of code is open for security audits and community contributions.</p>
                </div>
              </div>
            </div>

            <!-- Performance Metrics -->
            <div class="gv-card p-6 hover:border-yellow-500/30 gv-transition-smooth">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-200 mb-2">Sub-100ms Operations</h4>
                  <p class="gv-text-body text-sm">Instant image preview, real-time search, and <5MB memory footprint for encrypted vault operations.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Philosophy Quote -->
        <div class="mt-16 text-center">
          <div class="max-w-4xl mx-auto gv-card p-8 border-l-4 border-blue-500">
            <blockquote class="text-xl italic text-gray-300 mb-4">
              "GraphiVault doesn't ask you to trust it. It earns your trust — through transparency, clarity, and control."
            </blockquote>
            <cite class="gv-text-meta text-blue-400">— The GraphiVault Philosophy</cite>
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
const showMobileMenu = ref(false)
</script>
