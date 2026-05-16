import torch
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from insightface.model_zoo import model_zoo
from bot.ml.model.model import FatigueRegressor

# Инициализация FaceRecognition
face_model = FaceAnalysis(name="buffalo_l")
face_model.prepare(ctx_id=0)
recognizer = model_zoo.get_model("buffalo_l")
recognizer.prepare(ctx_id=0)

# Предобработка фото
def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return torch.zeros(1, 512)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_model.get(img_rgb)
    if len(faces) == 0:
        return torch.zeros(1, 512)
    bbox = faces[0].bbox.astype(int)
    x1, y1, x2, y2 = bbox
    face_img = img_rgb[y1:y2, x1:x2]
    face_input = cv2.resize(face_img, (112,112)).transpose(2,0,1)[np.newaxis,...]
    embedding = torch.tensor(recognizer.forward(face_input), dtype=torch.float32)
    return embedding

# Постобработка
def predict_fatigue(embedding: torch.Tensor, model: FatigueRegressor) -> float:
    model.eval()
    with torch.no_grad():
        return model(embedding).item()
