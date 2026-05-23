import os
from io import BytesIO

import torch
import torch.nn as nn
import torch.nn.functional as F
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image
from torchvision import models, transforms


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(BASE_DIR, "models", "best_phase2.pth"))
CLASS_NAMES = ["Cyst", "Normal", "Stone", "Tumor"]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

infer_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def build_model() -> nn.Module:
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(256, len(CLASS_NAMES)),
    )
    return model


def load_model() -> nn.Module:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")

    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
        state_dict = state_dict["model_state_dict"]

    model = build_model().to(DEVICE)
    model.load_state_dict(state_dict)
    model.eval()
    return model


model = load_model()


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "classes": CLASS_NAMES})


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded."}), 400

    image_file = request.files["image"]
    if not image_file.filename:
        return jsonify({"error": "Uploaded image has no filename."}), 400

    try:
        image = Image.open(BytesIO(image_file.read())).convert("RGB")
        tensor = infer_transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            logits = model(tensor)
            probs = F.softmax(logits, dim=1)[0].cpu().tolist()

        pred_idx = int(torch.tensor(probs).argmax())
        confidence = probs[pred_idx]

        return jsonify(
            {
                "prediction": CLASS_NAMES[pred_idx],
                "confidence": round(confidence * 100, 2),
                "probabilities": [
                    {"label": label, "confidence": round(prob * 100, 2)}
                    for label, prob in zip(CLASS_NAMES, probs)
                ],
            }
        )
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="127.0.0.1", port=port, debug=False)
