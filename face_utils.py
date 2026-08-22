"""
face_utils.py
Thin wrapper around the `face_recognition` library (built on dlib) for:
  - extracting a single encoding from a registration photo
  - detecting + encoding every face in a group photo
  - matching detected faces against a batch's known students
"""

import numpy as np
from PIL import Image

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    FACE_RECOGNITION_ERROR = None
except Exception as _e:
    FACE_RECOGNITION_AVAILABLE = False
    FACE_RECOGNITION_ERROR = str(_e)
    try:
        import cv2
    except ImportError:
        cv2 = None



def resize_image_if_large(image_np, max_dim=800):
    """
    Resizes image_np so its maximum dimension is at most max_dim.
    Drastically speeds up face detection and encoding on high-res camera photos.
    """
    h, w = image_np.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = Image.fromarray(image_np)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return np.array(img)
    return image_np


def get_single_face_encoding(image_np):
    """
    For student registration. Expects one clear face in the image.
    Returns (encoding, error_message). encoding is None if it fails.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return None, f"face_recognition module is unavailable: {FACE_RECOGNITION_ERROR}"

    image_np = resize_image_if_large(image_np, max_dim=800)
    face_locations = face_recognition.face_locations(image_np)

    if len(face_locations) == 0:
        return None, "No face detected. Please retake the photo with better lighting."
    if len(face_locations) > 1:
        return None, "Multiple faces detected. Please make sure only one person is in frame."

    encodings = face_recognition.face_encodings(image_np, known_face_locations=face_locations)
    return encodings[0], None


def get_all_faces(image_np):
    """
    For attendance photos. Returns a list of (location, encoding) for every
    face found in the image.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return []

    image_np = resize_image_if_large(image_np, max_dim=1024)
    face_locations = face_recognition.face_locations(image_np)
    encodings = face_recognition.face_encodings(image_np, known_face_locations=face_locations)
    return list(zip(face_locations, encodings))


def match_face(unknown_encoding, known_students, tolerance=0.5):
    """
    known_students: list of dicts with 'id', 'name', 'roll_no', 'encoding'
    Returns the best-matching student dict, or None if no match within tolerance.
    """
    if not known_students:
        return None

    known_encodings = [s["encoding"] for s in known_students]
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_idx = int(np.argmin(distances))

    if distances[best_idx] <= tolerance:
        return known_students[best_idx]
    return None

