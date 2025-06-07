import face_recognition
import os

KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), '../known_faces')

def load_known_faces():
    known_encodings = []
    known_names = []

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_names.append(name)
            else:
                print(f"No face found in known image: {filename}")

    return known_encodings, known_names

def recognize_faces_in_image(image_path, known_encodings, known_names):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    recognized_names = []

    for encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]
        recognized_names.append(name)

    return recognized_names
