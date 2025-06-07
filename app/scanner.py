import os
from datetime import datetime

from app.face_recognizer import load_known_faces, recognize_faces_in_image
from app.tagger import tag_image_with_clip

# Load known face data once
known_encodings, known_names = load_known_faces()

def scan_folder(folder_path):
    photo_data = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(root, file)

                try:
                    # Get created date
                    created_ts = os.path.getctime(file_path)
                    created_date = datetime.fromtimestamp(created_ts).strftime('%Y-%m-%d %H:%M:%S')

                    # Recognize faces
                    faces = recognize_faces_in_image(file_path, known_encodings, known_names)
                    faces_str = ', '.join(faces)

                    # Auto tag using AI
                    tags = tag_image_with_clip(file_path)
                    tags_str = ', '.join(tags)

                    # Add photo metadata
                    photo_data.append({
                        'file_path': file_path,
                        'file_name': file,
                        'created_date': created_date,
                        'faces': faces_str,
                        'tags': tags_str
                    })

                except Exception as e:
                    print(f"Error processing {file}: {e}")

    return photo_data
