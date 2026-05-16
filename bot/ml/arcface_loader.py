import torch
from insightface.app import FaceAnalysis
from insightface.model_zoo import model_zoo
from bot.ml.model.model import FatigueRegressor

# === Устройство ===
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# === Модель регрессии усталости ===
regression_model = FatigueRegressor().to(device)
regression_model.load_state_dict(
    torch.load(r".\bot\ml\model\fatigue_model.pth", map_location=device)
)
regression_model.eval()

# === Детектор лиц InsightFace ===
face_detector = FaceAnalysis(
    name="buffalo_l",
    providers=['CUDAExecutionProvider'] if torch.cuda.is_available() else ['CPUExecutionProvider']
)
face_detector.prepare(ctx_id=0, det_size=(224, 224))

# === ArcFace (эмбеддер) ===
recognizer = model_zoo.get_model(
    r".\!models\buffalo_l\recognition"
)
recognizer.prepare(ctx_id=0)
