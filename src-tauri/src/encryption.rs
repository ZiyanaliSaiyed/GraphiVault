use anyhow::Result;
use std::process::Command;
use std::path::Path;

pub async fn encrypt_file(file_path: &str, password: &str) -> Result<String> {
    // For now, we'll use a simple Python script for encryption
    // In production, you might want to use a Rust crypto library
    let output = Command::new("python")
        .arg("python_backend/encrypt.py")
        .arg(file_path)
        .arg(password)
        .output()?;
    
    if output.status.success() {
        let encrypted_path = String::from_utf8(output.stdout)?;
        Ok(encrypted_path.trim().to_string())
    } else {
        let error = String::from_utf8(output.stderr)?;
        Err(anyhow::anyhow!("Encryption failed: {}", error))
    }
}

pub async fn decrypt_file(encrypted_file_path: &str, password: &str, output_path: &str) -> Result<()> {
    let output = Command::new("python")
        .arg("python_backend/decrypt.py")
        .arg(encrypted_file_path)
        .arg(password)
        .arg(output_path)
        .output()?;
    
    if output.status.success() {
        Ok(())
    } else {
        let error = String::from_utf8(output.stderr)?;
        Err(anyhow::anyhow!("Decryption failed: {}", error))
    }
}
