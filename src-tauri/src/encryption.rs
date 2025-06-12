use anyhow::Result;
use serde_json;
use std::process::Command;

pub async fn encrypt_file(file_path: &str, password: &str) -> Result<String> {
    // Use the new IPC Gateway for encryption
    let output = Command::new("python")
        .arg("python_backend/ipc/ipc_gateway.py")
        .arg("encrypt_file")
        .arg("--vault-path")
        .arg("./vault") // This should be configurable
        .arg("--file-path")
        .arg(file_path)
        .arg("--password")
        .arg(password)
        .output()?;

    if output.status.success() {
        let response_text = String::from_utf8(output.stdout)?;
        let response: serde_json::Value = serde_json::from_str(&response_text)?;

        if response["success"].as_bool().unwrap_or(false) {
            let encrypted_path = response["encrypted_path"]
                .as_str()
                .ok_or_else(|| anyhow::anyhow!("No encrypted_path in response"))?;
            Ok(encrypted_path.to_string())
        } else {
            let error = response["error"].as_str().unwrap_or("Unknown error");
            Err(anyhow::anyhow!("Encryption failed: {}", error))
        }
    } else {
        let error = String::from_utf8(output.stderr)?;
        Err(anyhow::anyhow!("Encryption process failed: {}", error))
    }
}

pub async fn decrypt_file(
    encrypted_file_path: &str,
    password: &str,
    output_path: &str,
) -> Result<()> {
    // Use the new IPC Gateway for decryption
    let output = Command::new("python")
        .arg("python_backend/ipc/ipc_gateway.py")
        .arg("decrypt_file")
        .arg("--vault-path")
        .arg("./vault") // This should be configurable
        .arg("--file-path")
        .arg(encrypted_file_path)
        .arg("--password")
        .arg(password)
        .arg("--output-path")
        .arg(output_path)
        .output()?;

    if output.status.success() {
        let response_text = String::from_utf8(output.stdout)?;
        let response: serde_json::Value = serde_json::from_str(&response_text)?;

        if response["success"].as_bool().unwrap_or(false) {
            Ok(())
        } else {
            let error = response["error"].as_str().unwrap_or("Unknown error");
            Err(anyhow::anyhow!("Decryption failed: {}", error))
        }
    } else {
        let error = String::from_utf8(output.stderr)?;
        Err(anyhow::anyhow!("Decryption process failed: {}", error))
    }
}
