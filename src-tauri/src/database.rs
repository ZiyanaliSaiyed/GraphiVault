use sqlx::{Row, SqlitePool};
use tauri::AppHandle;
use anyhow::Result;
use std::fs;

use crate::commands::ImageRecord;

pub async fn init_db(app_handle: &AppHandle) -> Result<()> {
    let app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or_else(|| anyhow::anyhow!("Failed to get app data directory"))?;
    
    // Create app data directory if it doesn't exist
    fs::create_dir_all(&app_data_dir)?;
    
    let db_path = app_data_dir.join("graphivault.db");
    let database_url = format!("sqlite:{}", db_path.to_string_lossy());
    
    let pool = SqlitePool::connect(&database_url).await?;
    
    // Create tables
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            date_added TEXT NOT NULL,
            date_modified TEXT NOT NULL,
            tags TEXT NOT NULL, -- JSON array
            metadata TEXT NOT NULL, -- JSON object
            is_encrypted BOOLEAN NOT NULL DEFAULT 0,
            thumbnail_path TEXT
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Store the pool in app state
    app_handle.manage(pool);
    
    Ok(())
}

pub async fn insert_image(app_handle: &AppHandle, image: &ImageRecord) -> Result<()> {
    let pool = app_handle.state::<SqlitePool>();
    
    let tags_json = serde_json::to_string(&image.tags)?;
    let metadata_json = serde_json::to_string(&image.metadata)?;
    
    sqlx::query(
        r#"
        INSERT INTO images (
            id, name, path, size, mime_type, date_added, date_modified,
            tags, metadata, is_encrypted, thumbnail_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&image.id)
    .bind(&image.name)
    .bind(&image.path)
    .bind(image.size)
    .bind(&image.mime_type)
    .bind(image.date_added.to_rfc3339())
    .bind(image.date_modified.to_rfc3339())
    .bind(tags_json)
    .bind(metadata_json)
    .bind(image.is_encrypted)
    .bind(&image.thumbnail_path)
    .execute(&**pool)
    .await?;
    
    Ok(())
}

pub async fn get_all_images(app_handle: &AppHandle) -> Result<Vec<ImageRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let rows = sqlx::query("SELECT * FROM images ORDER BY date_added DESC")
        .fetch_all(&**pool)
        .await?;
    
    let mut images = Vec::new();
    
    for row in rows {
        let tags_json: String = row.get("tags");
        let metadata_json: String = row.get("metadata");
        let date_added_str: String = row.get("date_added");
        let date_modified_str: String = row.get("date_modified");
        
        let tags: Vec<String> = serde_json::from_str(&tags_json)?;
        let metadata: serde_json::Value = serde_json::from_str(&metadata_json)?;
        let date_added = chrono::DateTime::parse_from_rfc3339(&date_added_str)?
            .with_timezone(&chrono::Utc);
        let date_modified = chrono::DateTime::parse_from_rfc3339(&date_modified_str)?
            .with_timezone(&chrono::Utc);
        
        images.push(ImageRecord {
            id: row.get("id"),
            name: row.get("name"),
            path: row.get("path"),
            size: row.get("size"),
            mime_type: row.get("mime_type"),
            date_added,
            date_modified,
            tags,
            metadata,
            is_encrypted: row.get("is_encrypted"),
            thumbnail_path: row.get("thumbnail_path"),
        });
    }
    
    Ok(images)
}

pub async fn delete_image(app_handle: &AppHandle, id: &str) -> Result<()> {
    let pool = app_handle.state::<SqlitePool>();
    
    sqlx::query("DELETE FROM images WHERE id = ?")
        .bind(id)
        .execute(&**pool)
        .await?;
    
    Ok(())
}
