// Platform detection and API abstraction
import { invoke } from '@tauri-apps/api/tauri'
import type { 
  GraphiVaultAPI,
  ImageRecord, 
  TagRecord, 
  AnnotationRecord, 
  VaultInfo,
  PythonBackendResponse
} from '../types/database'

// Check if we're running in Tauri (desktop) or browser
export const isTauri = () => {
  return typeof window !== 'undefined' && '__TAURI__' in window
}

export const isWeb = () => !isTauri()

// Mock data for web environment
const mockImages: ImageRecord[] = [
  {
    id: 1,
    file_hash: 'demo_hash_123456789',
    file_name: 'demo-image.jpg', // Would be encrypted in real implementation
    storage_path: 'encrypted/demo_image_encrypted',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    file_size: 1024000,
    is_deleted: false
  }
]

// Web API implementation (fallback for browser)
const webAPI: GraphiVaultAPI = {
  async getAppDataDir(): Promise<string> {
    return '/tmp/graphivault'
  },

  async initDatabase(): Promise<void> {
    console.log('Web mode: Database initialized (using localStorage)')
    return Promise.resolve()
  },

  async addImage(
    file_hash: string,
    file_name: string,
    storage_path: string,
    file_size: number
  ): Promise<number> {
    const newImage: ImageRecord = {
      id: Math.floor(Math.random() * 10000),
      file_hash,
      file_name,
      storage_path,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      file_size,
      is_deleted: false
    }
    
    // Store in localStorage for demo
    const stored = localStorage.getItem('graphivault-images')
    const images = stored ? JSON.parse(stored) : []
    images.push(newImage)
    localStorage.setItem('graphivault-images', JSON.stringify(images))
    
    return newImage.id
  },

  async getImages(): Promise<ImageRecord[]> {
    // Return mock data + localStorage data for demo
    const stored = localStorage.getItem('graphivault-images')
    const localImages = stored ? JSON.parse(stored) : []
    return [...mockImages, ...localImages]
  },

  async getImageById(id: number): Promise<ImageRecord | null> {
    const images = await this.getImages()
    return images.find(img => img.id === id) || null
  },

  async getImageByHash(file_hash: string): Promise<ImageRecord | null> {
    const images = await this.getImages()
    return images.find(img => img.file_hash === file_hash) || null
  },

  async deleteImage(id: number): Promise<void> {
    const stored = localStorage.getItem('graphivault-images')
    const images = stored ? JSON.parse(stored) : []
    const filtered = images.filter((img: ImageRecord) => img.id !== id)
    localStorage.setItem('graphivault-images', JSON.stringify(filtered))
    return Promise.resolve()
  },

  async addTag(image_id: number, tag_name: string, tag_type?: string): Promise<number> {
    console.log('Web mode: Tag added (simulated)')
    return Math.floor(Math.random() * 10000)
  },

  async getImageTags(image_id: number): Promise<TagRecord[]> {
    console.log('Web mode: Getting tags (simulated)')
    return []
  },

  async addAnnotation(image_id: number, note: string): Promise<number> {
    console.log('Web mode: Annotation added (simulated)')
    return Math.floor(Math.random() * 10000)
  },

  async getImageAnnotations(image_id: number): Promise<AnnotationRecord[]> {
    console.log('Web mode: Getting annotations (simulated)')
    return []
  },

  async setVaultSetting(key: string, value: string): Promise<void> {
    localStorage.setItem(`vault_setting_${key}`, value)
    return Promise.resolve()
  },

  async getVaultSetting(key: string): Promise<string | null> {
    return localStorage.getItem(`vault_setting_${key}`)
  },

  async getVaultInfo(): Promise<VaultInfo> {
    const images = await this.getImages()
    return {
      vault_id: 'demo_vault_123',
      created_at: new Date().toISOString(),
      schema_version: '1',
      total_images: images.length,
      status: 'active'
    }
  },

  async encryptFile(file_path: string, password: string): Promise<string> {
    console.log('Web mode: File encryption simulated')
    return Promise.resolve(file_path + '.encrypted')
  },

  async decryptFile(encrypted_file_path: string, password: string): Promise<string> {
    console.log('Web mode: File decryption simulated')
    return Promise.resolve(encrypted_file_path.replace('.encrypted', ''))
  },

  // Python Backend Integration (mock implementations for web)
  async initializeVault(master_password: string): Promise<PythonBackendResponse> {
    console.log('Web mode: Vault initialization simulated')
    return Promise.resolve({
      success: true,
      message: 'Vault initialized (simulated)',
      data: { vault_id: 'demo_vault_123' }
    })
  },

  async unlockVault(master_password: string): Promise<PythonBackendResponse> {
    console.log('Web mode: Vault unlock simulated')
    return Promise.resolve({
      success: true,
      message: 'Vault unlocked (simulated)',
      data: { session_id: 'demo_session_456' }
    })
  },

  async lockVault(): Promise<PythonBackendResponse> {
    console.log('Web mode: Vault lock simulated')
    return Promise.resolve({
      success: true,
      message: 'Vault locked (simulated)'
    })
  },

  async processImageFile(file_path: string, tags: string[]): Promise<PythonBackendResponse> {
    console.log('Web mode: Image processing simulated')
    return Promise.resolve({
      success: true,
      data: {
        image_id: Math.floor(Math.random() * 10000).toString(),
        message: 'Image processed (simulated)'
      }
    })
  },

  async searchImages(query: string, tags: string[]): Promise<PythonBackendResponse> {
    console.log('Web mode: Image search simulated')
    const images = await this.getImages()
    return Promise.resolve({
      success: true,
      data: {
        results: images.map(img => ({
          id: img.id.toString(),
          name: img.file_name,
          size: img.file_size,
          mime_type: 'image/jpeg',
          date_added: img.created_at,
          date_modified: img.updated_at,
          tags: [],
          metadata: {},
          is_encrypted: false,
          relevance_score: 0.8
        })),
        total_results: images.length
      }
    })
  },

  async getDecryptedImage(image_id: number): Promise<PythonBackendResponse> {
    console.log('Web mode: Image decryption simulated')
    return Promise.resolve({
      success: true,
      data: {
        image_data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        format: 'base64'
      }
    })
  },

  async getImageThumbnail(image_id: number): Promise<PythonBackendResponse> {
    console.log('Web mode: Thumbnail retrieval simulated')
    return Promise.resolve({
      success: true,
      data: {
        thumbnail_data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        format: 'base64'
      }
    })
  }
}

// Tauri API implementation (desktop)
const tauriAPI: GraphiVaultAPI = {
  async getAppDataDir(): Promise<string> {
    return await invoke('get_app_data_dir')
  },

  async initDatabase(): Promise<void> {
    return await invoke('init_database')
  },

  async addImage(file_hash: string, file_name: string, storage_path: string, file_size: number): Promise<number> {
    return await invoke('add_image', { 
      fileHash: file_hash,
      fileName: file_name,
      storagePath: storage_path,
      fileSize: file_size
    })
  },

  async getImages(): Promise<ImageRecord[]> {
    return await invoke('get_images')
  },

  async getImageById(id: number): Promise<ImageRecord | null> {
    return await invoke('get_image_by_id', { id })
  },

  async getImageByHash(file_hash: string): Promise<ImageRecord | null> {
    return await invoke('get_image_by_hash', { fileHash: file_hash })
  },

  async deleteImage(id: number): Promise<void> {
    return await invoke('delete_image', { id })
  },

  async addTag(image_id: number, tag_name: string, tag_type?: string): Promise<number> {
    return await invoke('add_tag', { 
      imageId: image_id,
      tagName: tag_name,
      tagType: tag_type
    })
  },

  async getImageTags(image_id: number): Promise<TagRecord[]> {
    return await invoke('get_image_tags', { imageId: image_id })
  },

  async addAnnotation(image_id: number, note: string): Promise<number> {
    return await invoke('add_annotation', { 
      imageId: image_id,
      note: note
    })
  },

  async getImageAnnotations(image_id: number): Promise<AnnotationRecord[]> {
    return await invoke('get_image_annotations', { imageId: image_id })
  },

  async setVaultSetting(key: string, value: string): Promise<void> {
    return await invoke('set_vault_setting', { key, value })
  },

  async getVaultSetting(key: string): Promise<string | null> {
    return await invoke('get_vault_setting', { key })
  },

  async getVaultInfo(): Promise<VaultInfo> {
    return await invoke('get_vault_info')
  },

  async encryptFile(file_path: string, password: string): Promise<string> {
    return await invoke('encrypt_file', { filePath: file_path, password })
  },
  async decryptFile(encrypted_file_path: string, password: string): Promise<string> {
    return await invoke('decrypt_file', { encryptedFilePath: encrypted_file_path, password })
  },
  // Python Backend Integration
  async initializeVault(master_password: string): Promise<PythonBackendResponse> {
    return await invoke('initialize_vault', { masterPassword: master_password })
  },

  async unlockVault(master_password: string): Promise<PythonBackendResponse> {
    return await invoke('unlock_vault', { masterPassword: master_password })
  },

  async lockVault(): Promise<PythonBackendResponse> {
    return await invoke('lock_vault')
  },
  async processImageFile(file_path: string, tags: string[]): Promise<PythonBackendResponse> {
    return await invoke('process_image_file', { filePath: file_path, tags })
  },

  async searchImages(query: string, tags: string[]): Promise<PythonBackendResponse> {
    return await invoke('search_images', { query, tags })
  },
  async getDecryptedImage(image_id: number): Promise<PythonBackendResponse> {
    return await invoke('get_decrypted_image', { imageId: image_id })
  },

  async getImageThumbnail(image_id: number): Promise<PythonBackendResponse> {
    return await invoke('get_image_thumbnail', { imageId: image_id })
  }
}

// Export the appropriate API based on the environment
export const api: GraphiVaultAPI = isTauri() ? tauriAPI : webAPI

// Environment info for debugging
export const getEnvironmentInfo = () => ({
  isTauri: isTauri(),
  isWeb: isWeb(),
  userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
  platform: typeof navigator !== 'undefined' ? navigator.platform : 'unknown'
})
