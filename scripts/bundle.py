#!/usr/bin/env python3

import os
import zipfile
import fnmatch
import argparse
from pathlib import Path

def load_packignore_patterns(packignore_path):
    patterns = []
    if os.path.exists(packignore_path):
        with open(packignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path, patterns, base_path):
    relative_path = os.path.relpath(path, base_path)
    
    for pattern in patterns:
        if pattern.endswith('/'):
            if fnmatch.fnmatch(relative_path + '/', pattern) or fnmatch.fnmatch(relative_path, pattern.rstrip('/')):
                return True
        else:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    
    parts = relative_path.split(os.sep)
    for i in range(len(parts)):
        partial_path = os.sep.join(parts[:i+1])
        for pattern in patterns:
            if pattern.endswith('/'):
                if fnmatch.fnmatch(partial_path + '/', pattern):
                    return True
            elif fnmatch.fnmatch(partial_path, pattern):
                return True
    
    return False

def bundle_files(source_dir, output_zip, packignore_path):
    patterns = load_packignore_patterns(packignore_path)
    output_filename = os.path.basename(output_zip)
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), patterns, source_dir)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path, patterns, source_dir) and os.path.basename(file_path) != output_filename:
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

def main():
    parser = argparse.ArgumentParser(description='Bundle files into a zip archive')
    parser.add_argument('--output', '-o', default='pack.zip', help='Output zip filename')
    parser.add_argument('--packignore', default='.packignore', help='Path to packignore file')
    
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    packignore_path = os.path.join(parent_dir, args.packignore)
    output_path = os.path.join(parent_dir, args.output)
    
    bundle_files(parent_dir, output_path, packignore_path)
    print(f"Bundle created: {args.output}")

if __name__ == "__main__":
    main()