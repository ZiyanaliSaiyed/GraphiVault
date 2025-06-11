// GraphiVault Database Types
// Auto-generated from Rust database models

export interface ImageRecord {
  id: number;
  file_hash: string;
  file_name: string; // Encrypted filename
  storage_path: string; // Vault-relative path
  created_at: string;
  updated_at: string;
  file_size: number;
  is_deleted: boolean;
}

export interface TagRecord {
  id: number;
  image_id: number;
  tag_name: string; // Encrypted tag
  tag_type?: string;
  created_at: string;
}

export interface AnnotationRecord {
  id: number;
  image_id: number;
  note: string; // Encrypted note
  created_at: string;
}

export interface VaultInfo {
  vault_id?: string;
  created_at?: string;
  schema_version?: string;
  total_images: number;
  status: string;
}

// Python Backend Response Types
export interface PythonBackendResponse {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

// Enhanced Image Record from Python Backend
export interface EnhancedImageRecord {
  id: string;
  name: string;
  size: number;
  mime_type: string;
  date_added: string;
  date_modified: string;
  tags: string[];
  metadata: Record<string, any>;
  thumbnail_path?: string;
  is_encrypted: boolean;
}

// Search Result
export interface SearchResult extends EnhancedImageRecord {
  relevance_score: number;
}

// Vault Statistics
export interface VaultStatistics {
  vault_path: string;
  is_locked: boolean;
  total_count: number;
  tag_statistics?: Record<string, any>;
  session_info?: Record<string, any>;
}

// GraphiVault API Commands
export interface GraphiVaultAPI {
  // Database initialization
  initDatabase(): Promise<void>;
  
  // Image operations
  addImage(file_hash: string, file_name: string, storage_path: string, file_size: number): Promise<number>;
  getImages(): Promise<ImageRecord[]>;
  getImageById(id: number): Promise<ImageRecord | null>;
  getImageByHash(file_hash: string): Promise<ImageRecord | null>;
  deleteImage(id: number): Promise<void>;
  
  // Tag operations
  addTag(image_id: number, tag_name: string, tag_type?: string): Promise<number>;
  getImageTags(image_id: number): Promise<TagRecord[]>;
  
  // Annotation operations
  addAnnotation(image_id: number, note: string): Promise<number>;
  getImageAnnotations(image_id: number): Promise<AnnotationRecord[]>;
  
  // Vault settings
  setVaultSetting(key: string, value: string): Promise<void>;
  getVaultSetting(key: string): Promise<string | null>;
  getVaultInfo(): Promise<VaultInfo>;
  
  // Utility
  getAppDataDir(): Promise<string>;
  
  // Encryption
  encryptFile(file_path: string, password: string): Promise<string>;
  decryptFile(encrypted_file_path: string, password: string): Promise<string>;

  // Python Backend Integration
  initializeVault(master_password: string): Promise<PythonBackendResponse>;
  unlockVault(master_password: string): Promise<PythonBackendResponse>;
  lockVault(): Promise<PythonBackendResponse>;
  processImageFile(file_path: string, tags: string[]): Promise<PythonBackendResponse>;
  searchImages(query: string, tags: string[]): Promise<PythonBackendResponse>;
  getDecryptedImage(image_id: number): Promise<PythonBackendResponse>;
  getImageThumbnail(image_id: number): Promise<PythonBackendResponse>;
}
