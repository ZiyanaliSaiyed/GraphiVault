use std::env;

fn main() {
    // This will ensure OUT_DIR is set and can be used by build dependencies
    println!("cargo:rerun-if-changed=build.rs");
    
    // Explicitly ensure OUT_DIR is available during build
    if let Ok(out_dir) = env::var("OUT_DIR") {
        println!("cargo:rustc-env=OUT_DIR={}", out_dir);
    }
    
    // Run the standard Tauri build process
    tauri_build::build()
}
