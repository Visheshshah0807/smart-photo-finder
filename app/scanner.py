import os
from datetime import datetime

from app.face_recognizer import load_known_faces, recognize_faces_in_image
from app.tagger import tag_image_with_clip

# Load known face data once
known_encodings, known_names = load_known_faces()

def scan_folder(folder_path):
    photo_data = []
    
    # Validate folder path
    if not os.path.exists(folder_path):
        print(f"Error: Folder path does not exist: {folder_path}")
        return photo_data
    
    if not os.path.isdir(folder_path):
        print(f"Error: Path is not a directory: {folder_path}")
        return photo_data

    # Supported image extensions
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    
    print(f"Scanning folder: {folder_path}")
    
    total_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(folder_path):
        print(f"Checking directory: {root}")
        
        # Filter for image files
        image_files = [f for f in files if f.lower().endswith(supported_extensions)]
        total_files += len(image_files)
        
        print(f"Found {len(image_files)} image files in {root}")
        
        for file in image_files:
            file_path = os.path.join(root, file)
            
            # Check if file is accessible
            if not os.path.isfile(file_path):
                print(f"Skipping non-file: {file_path}")
                continue
                
            if not os.access(file_path, os.R_OK):
                print(f"No read permission for: {file_path}")
                continue

            try:
                print(f"Processing: {file_path}")
                
                # Get file statistics
                stat_info = os.stat(file_path)
                
                # Try to get creation time, fall back to modification time
                try:
                    created_ts = stat_info.st_birthtime  # macOS
                except AttributeError:
                    try:
                        created_ts = stat_info.st_ctime  # Windows
                    except AttributeError:
                        created_ts = stat_info.st_mtime  # Linux (modification time)
                
                created_date = datetime.fromtimestamp(created_ts).strftime('%Y-%m-%d %H:%M:%S')

                # Initialize faces and tags
                faces = []
                tags = []

                # Recognize faces (with error handling)
                try:
                    faces = recognize_faces_in_image(file_path, known_encodings, known_names)
                    print(f"  Found faces: {faces}")
                except Exception as face_error:
                    print(f"  Face recognition error for {file}: {face_error}")
                    faces = []

                # Auto tag using AI (with error handling)
                try:
                    tags = tag_image_with_clip(file_path)
                    print(f"  Generated tags: {tags}")
                except Exception as tag_error:
                    print(f"  Tagging error for {file}: {tag_error}")
                    tags = []

                faces_str = ', '.join(faces) if faces else ''
                tags_str = ', '.join(tags) if tags else ''

                # Add photo metadata
                photo_info = {
                    'file_path': file_path,
                    'file_name': file,
                    'created_date': created_date,
                    'faces': faces_str,
                    'tags': tags_str
                }
                
                photo_data.append(photo_info)
                processed_files += 1
                
                print(f"  Successfully processed: {file}")

            except PermissionError:
                print(f"Permission denied accessing {file_path}")
                continue
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue

    print(f"Scan complete. Processed {processed_files} out of {total_files} image files.")
    return photo_data


def get_folder_stats(folder_path):
    """Get statistics about a folder before scanning"""
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None
    
    stats = {
        'total_files': 0,
        'image_files': 0,
        'subdirectories': 0,
        'accessible_images': 0
    }
    
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    
    for root, dirs, files in os.walk(folder_path):
        stats['subdirectories'] += len(dirs)
        stats['total_files'] += len(files)
        
        for file in files:
            if file.lower().endswith(supported_extensions):
                stats['image_files'] += 1
                file_path = os.path.join(root, file)
                if os.access(file_path, os.R_OK):
                    stats['accessible_images'] += 1
    
    return stats