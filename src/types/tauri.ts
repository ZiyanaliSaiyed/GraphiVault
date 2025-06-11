export interface TauriAPI {
  getAppDataDir(): Promise<string>
  initDatabase(): Promise<void>
  addImage(
    name: string,
    path: string,
    size: number,
    mimeType: string,
    tags: string[],
    metadata: Record<string, any>
  ): Promise<ImageRecord>
  getImages(): Promise<ImageRecord[]>
  deleteImage(id: string): Promise<void>
  encryptFile(filePath: string, password: string): Promise<string>
  decryptFile(encryptedFilePath: string, password: string, outputPath: string): Promise<void>
}

export interface ImageRecord {
  id: string
  name: string
  path: string
  size: number
  mimeType: string
  dateAdded: string
  dateModified: string
  tags: string[]
  metadata: Record<string, any>
  isEncrypted: boolean
  thumbnailPath?: string
}
