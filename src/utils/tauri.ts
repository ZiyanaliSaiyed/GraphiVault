// Re-export the platform-aware API
export { api as tauriAPI, isTauri, isWeb, getEnvironmentInfo } from './platform'

import { invoke } from '@tauri-apps/api/tauri'

/**
 * Adds an image to the vault.
 * @param fileContents - The base64 encoded contents of the file.
 * @param tags - An array of tags to associate with the image.
 * @param password - The vault password (optional, for unlocked vaults).
 * @returns A promise that resolves when the image has been added.
 */
export async function addImage(fileContents: string, tags: string[], password?: string): Promise<any> {
  try {
    console.log(`🔧 Tauri addImage called with ${tags.length} tags, password: ${password ? 'provided' : 'not provided'}`)
    const result = await invoke('add_image_from_frontend', { fileContents, tags, password })
    console.log(`✅ Tauri addImage result:`, result)
    return result
  } catch (error) {
    console.error(`❌ Tauri addImage error:`, error)
    throw error
  }
}
