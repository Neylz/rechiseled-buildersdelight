#!/usr/bin/env python3
"""
Script to automatically download chisel files from BuildersDelight GitHub repository
and generate corresponding chiseling recipes for the rechiseld datapack.
"""

import os
import json
import requests
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Configuration
GITHUB_API_BASE = "https://api.github.com/repos/Tynoxs/BuildersDelight/contents/src/main/resources/data/buildersdelight/chisel"
GITHUB_BRANCH = "1.20.1"
OUTPUT_DIR = Path("../data/rechiseld/chiseling_recipes")
SCRIPT_DIR = Path(__file__).parent


def clean_output_directory() -> None:
    """Clean the output directory before generating new files."""
    output_path = SCRIPT_DIR / OUTPUT_DIR
    if output_path.exists():
        print(f"Cleaning directory: {output_path}")
        shutil.rmtree(output_path)
    
    # Create the directory structure
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {output_path}")


def get_github_files() -> List[Dict[str, Any]]:
    """Fetch the list of files from GitHub API."""
    url = f"{GITHUB_API_BASE}?ref={GITHUB_BRANCH}"
    
    print(f"Fetching file list from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        files = response.json()
        json_files = [f for f in files if f['name'].endswith('.json') and f['type'] == 'file']
        
        print(f"Found {len(json_files)} JSON files")
        return json_files
        
    except requests.RequestException as e:
        print(f"Error fetching file list: {e}")
        return []


def download_file_content(download_url: str) -> Dict[str, Any] | None:
    """Download and parse a JSON file from GitHub."""
    try:
        response = requests.get(download_url)
        response.raise_for_status()
        
        return response.json()
        
    except requests.RequestException as e:
        print(f"Error downloading file from {download_url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {download_url}: {e}")
        return None


def extract_base_name(filename: str) -> str:
    """
    Extract the base name for the output file.
    For example: 'acacia_frame.json' -> 'acacia_planks'
    
    This function attempts to convert frame names to plank names.
    """
    base_name = filename.replace('.json', '')
    
    # Convert common frame patterns to plank patterns
    if '_frame' in base_name:
        base_name = base_name.replace('_frame', '_planks')
    elif base_name.endswith('_log'):
        # Keep log files as is, or convert if needed
        pass
    else:
        # For other cases, try to infer the base material
        # and add _planks suffix if it seems appropriate
        if not base_name.endswith('_planks'):
            base_name += '_planks'
    
    return base_name


def create_chiseling_recipe(variants: List[str]) -> Dict[str, Any]:
    """Create a chiseling recipe from a list of variants."""
    entries = [{"item": variant} for variant in variants]
    
    return {
        "type": "rechiseled:chiseling",
        "overwrite": False,
        "entries": entries
    }


def process_chisel_file(file_info: Dict[str, Any]) -> None:
    """Process a single chisel file and generate the corresponding recipe."""
    filename = file_info['name']
    download_url = file_info['download_url']
    
    print(f"Processing: {filename}")
    
    # Download and parse the file content
    content = download_file_content(download_url)
    if not content:
        print(f"Skipping {filename} due to download/parse error")
        return
    
    # Extract variants
    variants = content.get('variants', [])
    if not variants:
        print(f"No variants found in {filename}")
        return
    
    print(f"Found {len(variants)} variants in {filename}")
    
    # Generate output filename
    base_name = extract_base_name(filename)
    output_filename = f"{base_name}.json"
    output_path = SCRIPT_DIR / OUTPUT_DIR / output_filename
    
    # Create the chiseling recipe
    recipe = create_chiseling_recipe(variants)
    
    # Write the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
        
        print(f"Generated: {output_path}")
        
    except IOError as e:
        print(f"Error writing {output_path}: {e}")


def main():
    """Main function to orchestrate the generation process."""
    print("Starting chisel recipe generation...")
    print("=" * 50)
    
    # Clean the output directory
    clean_output_directory()
    
    # Get the list of files from GitHub
    files = get_github_files()
    if not files:
        print("No files found or error occurred. Exiting.")
        return
    
    print("=" * 50)
    
    # Process each file
    for file_info in files:
        try:
            process_chisel_file(file_info)
        except Exception as e:
            print(f"Error processing {file_info['name']}: {e}")
        print("-" * 30)
    
    print("=" * 50)
    print("Generation complete!")
    print(f"Output directory: {SCRIPT_DIR / OUTPUT_DIR}")


if __name__ == "__main__":
    main()