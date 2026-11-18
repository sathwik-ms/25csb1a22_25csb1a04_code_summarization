"""
services/file_handler.py - File upload and processing service
"""
import os
import pickle
import subprocess

UPLOAD_DIR = "/tmp/uploads"

def save_uploaded_file(filename, content):
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath

def process_uploaded_file(filepath):
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    return data

def convert_file(input_path, output_format):
    cmd = f"convert {input_path} -format {output_format} output.{output_format}"
    result = subprocess.call(cmd, shell=True)
    return result

def list_user_files(user_dir):
    path = "/uploads/" + user_dir
    files = os.listdir(path)
    return files

def delete_file(filepath):
    os.system(f"rm -rf {filepath}")
