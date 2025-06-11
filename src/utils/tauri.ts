import { invoke } from '@tauri-apps/api/tauri'
import type { TauriAPI, ImageRecord } from '../types/tauri'

export const tauriAPI: TauriAPI = {
  async getAppDataDir(): Promise<string> {
    return await invoke('get_app_data_dir')
  },

  async initDatabase(): Promise<void> {
    return await invoke('init_database')
  },

  async addImage(
    name: string,
    path: string,
    size: number,
    mimeType: string,
    tags: string[],
    metadata: Record<string, any>
  ): Promise<ImageRecord> {
    return await invoke('add_image', {
      name,
      path,
      size,
      mimeType,
      tags,
      metadata
    })
  },

  async getImages(): Promise<ImageRecord[]> {
    return await invoke('get_images')
  },

  async deleteImage(id: string): Promise<void> {
    return await invoke('delete_image', { id })
  },

  async encryptFile(filePath: string, password: string): Promise<string> {
    return await invoke('encrypt_file', { filePath, password })
  },

  async decryptFile(encryptedFilePath: string, password: string, outputPath: string): Promise<void> {
    return await invoke('decrypt_file', { encryptedFilePath, password, outputPath })
  }
}
