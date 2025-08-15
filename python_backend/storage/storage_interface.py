#!/usr/bin/env python3
"""
GraphiVault Storage Interface
SQLite-backed storage abstraction with prepared queries and schema control
Provides secure, ACID-compliant data persistence for the vault system
"""

import sqlite3
import json
import threading
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# GraphiVault Database Models
@dataclass
class ImageRecord:
    """Secure image record with encrypted metadata"""
    id: str
    name: str
    encrypted_path: str
    original_size: int
    encrypted_size: int
    mime_type: str
    file_hash: str
    date_added: datetime
    date_modified: datetime
    encrypted_tags: bytes
    encrypted_metadata: bytes
    thumbnail_path: Optional[str] = None
    is_encrypted: bool = True

@dataclass
class TagRecord:
    """Encrypted tag record"""
    id: int
    image_id: int
    tag_name: str  # Encrypted tag content
    tag_type: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class AnnotationRecord:
    """Encrypted annotation record"""
    id: int
    image_id: int
    note: str  # Encrypted content
    created_at: Optional[datetime] = None

# Import crypto controller
try:
    from ..crypto.crypto_controller import CryptoController
except ImportError:
    from crypto.crypto_controller import CryptoController


class StorageInterface:
    """
    Storage Interface - The persistent memory of the vault
    
    Features:
    - SQLite-backed storage with ACID compliance
    - Prepared statements for security and performance
    - Encrypted metadata storage
    - Transaction support with rollback
    - Schema versioning and migration
    - Connection pooling and thread safety
    """
    
    def __init__(self, db_path: str, crypto_controller: CryptoController):
        """Initialize storage interface"""
        logging.info(f"Initializing StorageInterface with db_path: {db_path}")
        self.db_path = Path(db_path)
        self.crypto = crypto_controller
        self.connection_lock = threading.Lock()
        self._local_storage = threading.local()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local_storage, 'connection'):
            self._local_storage.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
              # Configure connection
            conn = self._local_storage.connection
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = MEMORY")
            
        return self._local_storage.connection
    
    def _initialize_database(self) -> None:
        """Initialize GraphiVault database schema according to design specifications"""
        logging.info("Starting database initialization...")
        try:
            with self.connection_lock:
                conn = self._get_connection()
                
                # Configure SQLite for optimal security and performance
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA secure_delete = ON")
                conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
                conn.execute("PRAGMA page_size = 4096")
                conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
                conn.execute("PRAGMA temp_store = MEMORY")
                
                # Create images table - core metadata for each image file
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        encrypted_path TEXT NOT NULL,
                        original_size INTEGER NOT NULL,
                        encrypted_size INTEGER NOT NULL,
                        mime_type TEXT NOT NULL,
                        file_hash TEXT NOT NULL UNIQUE,
                        date_added TEXT NOT NULL,
                        date_modified TEXT NOT NULL,
                        encrypted_tags BLOB NOT NULL,
                        encrypted_metadata BLOB NOT NULL,
                        thumbnail_path TEXT,
                        is_encrypted BOOLEAN NOT NULL DEFAULT 1
                    )
                """)
                
                # Create tags table - encrypted user-defined tags
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER NOT NULL,
                        tag_name TEXT NOT NULL,
                        tag_type TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
                    )
                """)
                
                # Create annotations table - encrypted notes/descriptions
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS annotations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER NOT NULL,
                        note TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
                    )
                """)
                
                # Create vault_meta table - vault-level config and settings
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vault_meta (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        last_updated TEXT NOT NULL
                    )
                """)
                
                # Create auth_logs table - access attempts and critical operations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS auth_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        details TEXT
                    )
                """)
                
                # Create performance indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_images_file_hash ON images(file_hash)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_images_updated_at ON images(updated_at)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_images_storage_path ON images(storage_path)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_image_id ON tags(image_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_created_at ON tags(created_at)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_annotations_image_id ON annotations(image_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_auth_logs_timestamp ON auth_logs(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_auth_logs_event_type ON auth_logs(event_type)")
                
                # Set initial vault metadata
                self._initialize_vault_metadata(conn)
                
                conn.commit()
            logging.info("Database initialization completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during database initialization: {e}", exc_info=True)
            raise

    def _initialize_vault_metadata(self, conn: sqlite3.Connection) -> None:
        """Initialize vault metadata with default values"""
        from datetime import datetime, timezone
        import secrets
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if vault is already initialized
        cursor = conn.execute("SELECT COUNT(*) FROM vault_meta WHERE key = 'schema_version'")
        if cursor.fetchone()[0] > 0:
            return
        
        # Generate vault ID and salt
        vault_id = secrets.token_hex(16)
        vault_salt = secrets.token_hex(32)
        
        # Insert initial metadata
        metadata_items = [
            ('schema_version', '1', now),
            ('vault_id', vault_id, now),
            ('vault_salt', vault_salt, now),
            ('created_at', now, now),
            ('encryption_enabled', 'true', now),
            ('auto_vacuum_enabled', 'true', now)
        ]
        
        conn.executemany("""
            INSERT OR IGNORE INTO vault_meta (key, value, last_updated)
            VALUES (?, ?, ?)
        """, metadata_items)
      
    # GraphiVault Database Operations
    
    def store_image(self, image_record: ImageRecord) -> bool:
        """Store an image record in the database"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT INTO images (
                        id, name, encrypted_path, original_size, encrypted_size,
                        mime_type, file_hash, date_added, date_modified,
                        encrypted_tags, encrypted_metadata, thumbnail_path, is_encrypted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    image_record.id,
                    image_record.name,
                    image_record.encrypted_path,
                    image_record.original_size,
                    image_record.encrypted_size,
                    image_record.mime_type,
                    image_record.file_hash,
                    image_record.date_added.isoformat(),
                    image_record.date_modified.isoformat(),
                    image_record.encrypted_tags,
                    image_record.encrypted_metadata,
                    image_record.thumbnail_path,
                    image_record.is_encrypted
                ))
            
            return True
            
        except Exception as e:
            self.log_auth_event("store_image_error", "failure", str(e))
            return False
    
    def get_image(self, image_id: int) -> Optional[ImageRecord]:
        """Get an image record by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT id, file_hash, file_name, storage_path, created_at, 
                       updated_at, file_size, is_deleted
                FROM images 
                WHERE id = ? AND is_deleted = 0
            """, (image_id,))
            
            row = cursor.fetchone()
            if row:
                return ImageRecord(
                    id=row['id'],
                    file_hash=row['file_hash'],
                    file_name=row['file_name'],
                    storage_path=row['storage_path'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    file_size=row['file_size'],
                    is_deleted=bool(row['is_deleted'])
                )
            
            return None
            
        except Exception:
            return None
    
    def get_image_by_hash(self, file_hash: str) -> Optional[ImageRecord]:
        """Get an image record by file hash (deduplication)"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT id, file_hash, file_name, storage_path, created_at, 
                       updated_at, file_size, is_deleted
                FROM images 
                WHERE file_hash = ? AND is_deleted = 0
            """, (file_hash,))
            
            row = cursor.fetchone()
            if row:
                return ImageRecord(
                    id=row['id'],
                    file_hash=row['file_hash'],
                    file_name=row['file_name'],
                    storage_path=row['storage_path'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    file_size=row['file_size'],
                    is_deleted=bool(row['is_deleted'])
                )
            
            return None
            
        except Exception:
            return None
    
    def store_tag(self, tag_record: TagRecord) -> bool:
        """Store an encrypted tag"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT INTO tags (image_id, tag_name, tag_type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    tag_record.image_id,
                    tag_record.tag_name,  # Should be encrypted
                    tag_record.tag_type,
                    tag_record.created_at.isoformat() if tag_record.created_at else datetime.now(timezone.utc).isoformat()
                ))
            
            return True
            
        except Exception:
            return False
    
    def get_image_tags(self, image_id: int) -> List[TagRecord]:
        """Get all tags for an image"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT id, image_id, tag_name, tag_type, created_at
                FROM tags 
                WHERE image_id = ?
                ORDER BY created_at
            """, (image_id,))
            
            tags = []
            for row in cursor.fetchall():
                tags.append(TagRecord(
                    id=row['id'],
                    image_id=row['image_id'],
                    tag_name=row['tag_name'],
                    tag_type=row['tag_type'],
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            
            return tags
            
        except Exception:
            return []
    
    def store_annotation(self, annotation_record: AnnotationRecord) -> bool:
        """Store an encrypted annotation/note"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT INTO annotations (image_id, note, created_at)
                    VALUES (?, ?, ?)
                """, (
                    annotation_record.image_id,
                    annotation_record.note,  # Should be encrypted
                    annotation_record.created_at.isoformat() if annotation_record.created_at else datetime.now(timezone.utc).isoformat()
                ))
            
            return True
            
        except Exception:
            return False
    
    def get_image_annotations(self, image_id: int) -> List[AnnotationRecord]:
        """Get all annotations for an image"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT id, image_id, note, created_at
                FROM annotations 
                WHERE image_id = ?
                ORDER BY created_at
            """, (image_id,))
            
            annotations = []
            for row in cursor.fetchall():
                annotations.append(AnnotationRecord(
                    id=row['id'],
                    image_id=row['image_id'],
                    note=row['note'],
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            
            return annotations
            
        except Exception:
            return []
    
    def set_vault_meta(self, key: str, value: str) -> bool:
        """Set vault metadata value"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO vault_meta (key, value, last_updated)
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now(timezone.utc).isoformat()))
            
            return True
            
        except Exception:
            return False
    
    def get_vault_meta(self, key: str) -> Optional[str]:
        """Get vault metadata value"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT value FROM vault_meta WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
            
        except Exception:
            return None
    
    def log_auth_event(self, event_type: str, status: str, details: Optional[str] = None) -> bool:
        """Log authentication/security event"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT INTO auth_logs (event_type, timestamp, status, details)
                    VALUES (?, ?, ?, ?)
                """, (
                    event_type,
                    datetime.now(timezone.utc).isoformat(),
                    status,
                    details
                ))
            
            return True
            
        except Exception:
            return False
    
    def get_image(self, image_id: str) -> Optional[ImageRecord]:
        """Get image record by ID"""
        try:
                SELECT * FROM images WHERE id = ?
            """, (image_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_image_record(row)
            
        except Exception:
            return None
    
    def get_all_images(self, limit: int = None, offset: int = 0) -> List[ImageRecord]:
        """Get all images with pagination"""
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM images WHERE is_encrypted = 1 ORDER BY date_added DESC"
            params = []
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_image_record(row) for row in rows]
            
        except Exception:
            return []
    
    def update_image(self, image_id: str, updates: Dict[str, Any]) -> bool:
        """Update an image record"""
        try:
            if not updates:
                return True
            
            conn = self._get_connection()
            
            # Build dynamic update query
            set_clauses = []
            params = []
            
            allowed_fields = {
                'name', 'encrypted_tags', 'encrypted_metadata', 
                'thumbnail_path', 'date_modified'
            }
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    if field == 'date_modified' and isinstance(value, datetime):
                        params.append(value.isoformat())
                    else:
                        params.append(value)
            
            if not set_clauses:
                return True
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(image_id)
            
            query = f"UPDATE images SET {', '.join(set_clauses)} WHERE id = ?"
            
            with conn:
                cursor = conn.execute(query, params)
                return cursor.rowcount > 0
                
        except Exception:
            return False
    
    def delete_image(self, image_id: str) -> bool:
        """Delete an image record"""
        try:
            conn = self._get_connection()
            
            with conn:
                cursor = conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
                return cursor.rowcount > 0
                
        except Exception:
            return False
    
    def search_images(self, filters: Dict[str, Any] = None) -> List[ImageRecord]:
        """Search images with filters"""
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM images WHERE 1=1"
            params = []
            
            if filters:
                if 'mime_type' in filters:
                    query += " AND mime_type LIKE ?"
                    params.append(f"%{filters['mime_type']}%")
                
                if 'date_from' in filters:
                    query += " AND date_added >= ?"
                    params.append(filters['date_from'])
                
                if 'date_to' in filters:
                    query += " AND date_added <= ?"
                    params.append(filters['date_to'])
                
                if 'min_size' in filters:
                    query += " AND original_size >= ?"
                    params.append(filters['min_size'])
                
                if 'max_size' in filters:
                    query += " AND original_size <= ?"
                    params.append(filters['max_size'])
            
            query += " ORDER BY date_added DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_image_record(row) for row in rows]
            
        except Exception:
            return []
    
    def get_image_by_hash(self, file_hash: str) -> Optional[ImageRecord]:
        """Get image by file hash (for duplicate detection)"""
        try:
            conn = self._get_connection()
            
            cursor = conn.execute("""
                SELECT * FROM images WHERE file_hash = ?
            """, (file_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_image_record(row)
            
        except Exception:
            return None
    
    def get_vault_setting(self, key: str) -> Optional[str]:
        """Get a vault setting"""
        try:
            conn = self._get_connection()
            
            cursor = conn.execute("""
                SELECT value, encrypted FROM vault_settings WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            value = row['value']
            
            # Decrypt if encrypted
            if row['encrypted']:
                try:
                    decrypted_value = self.crypto.decrypt_data(value.encode()).decode()
                    return decrypted_value
                except Exception:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def set_vault_setting(self, key: str, value: str, encrypted: bool = False) -> bool:
        """Set a vault setting"""
        try:
            conn = self._get_connection()
            
            # Encrypt value if requested
            if encrypted:
                try:
                    encrypted_value = self.crypto.encrypt_data(value.encode()).decode()
                    value = encrypted_value
                except Exception:
                    return False
            
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO vault_settings 
                    (key, value, encrypted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    key, value, encrypted,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
            
            return True
            
        except Exception:
            return False
    
    def log_audit_event(self, event_type: str, event_data: Dict[str, Any], 
                       session_hash: str = None) -> bool:
        """Log an audit event"""
        try:
            conn = self._get_connection()
            
            with conn:
                conn.execute("""
                    INSERT INTO audit_log (timestamp, event_type, event_data, session_hash)
                    VALUES (?, ?, ?, ?)                """, (
                    datetime.now(timezone.utc).isoformat(),
                    event_type,
                    json.dumps(event_data, ensure_ascii=False) if event_data else None,
                    session_hash
                ))
            
            return True
            
        except Exception:
            return False
    
    def get_audit_events(self, hours: int = 24, event_type: str = None) -> List[Dict[str, Any]]:
        """Get audit events"""
        try:
            conn = self._get_connection()
            
            cutoff_time = datetime.now(timezone.utc) - datetime.timedelta(hours=hours)
            
            query = "SELECT * FROM audit_log WHERE timestamp >= ?"
            params = [cutoff_time.isoformat()]
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            query += " ORDER BY timestamp DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'event_type': row['event_type'],
                    'session_hash': row['session_hash'],
                    'created_at': row['created_at']
                }
                
                if row['event_data']:
                    try:
                        event['event_data'] = json.loads(row['event_data'])
                    except json.JSONDecodeError:
                        event['event_data'] = {}
                
                events.append(event)
            
            return events
            
        except Exception:
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            conn = self._get_connection()
            
            stats = {}
            
            # Image statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_images,
                    SUM(original_size) as total_original_size,
                    SUM(encrypted_size) as total_encrypted_size,
                    AVG(original_size) as avg_file_size,
                    MIN(date_added) as oldest_image,
                    MAX(date_added) as newest_image
                FROM images
            """)
            
            row = cursor.fetchone()
            if row:
                return self._row_to_image_record(row)
            cursor = conn.execute("""
                SELECT mime_type, COUNT(*) as count
                FROM images
                GROUP BY mime_type
                ORDER BY count DESC
            """)
            
            file_types = {}
            for row in cursor.fetchall():
                file_types[row['mime_type']] = row['count']
            
            stats['file_type_distribution'] = file_types
            
            # Database file size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            stats['database_size'] = db_size
            
            return stats
            
        except Exception:
            return {}
    
    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""
        try:
            conn = self._get_connection()
            conn.execute("VACUUM")
            return True
            
        except Exception:
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            source_conn = self._get_connection()
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            backup_conn.close()
            
            return True
            
        except Exception:
            return False
    
    def _row_to_image_record(self, row: sqlite3.Row) -> ImageRecord:
        """Convert database row to ImageRecord"""
        return ImageRecord(
            id=str(row['id']),
            name=row['name'],
            encrypted_path=row['encrypted_path'],
            original_size=row['original_size'],
            encrypted_size=row['encrypted_size'],
            mime_type=row['mime_type'],
            file_hash=row['file_hash'],
            date_added=datetime.fromisoformat(row['date_added']),
            date_modified=datetime.fromisoformat(row['date_modified']),
            encrypted_tags=row['encrypted_tags'],
            encrypted_metadata=row['encrypted_metadata'],
            thumbnail_path=row['thumbnail_path'],
            is_encrypted=bool(row['is_encrypted'])
        )
    
    def _get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0
            
        except Exception:
            return 0
    
    def _set_schema_version(self, version: int, description: str) -> None:
        """Set schema version"""
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO schema_version (version, applied_at, description)
            VALUES (?, ?, ?)
        """, (version, datetime.now(timezone.utc).isoformat(), description))
        conn.commit()
    
    def close(self) -> None:
        """Close database connections"""
        if hasattr(self._local_storage, 'connection'):
            self._local_storage.connection.close()
            delattr(self._local_storage, 'connection')
