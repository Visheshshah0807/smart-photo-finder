from PIL import Image
import torch
import clip

# Load CLIP model once
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Sample label set
CANDIDATE_LABELS = [
    "nature", "family", "friends", "selfie", "mountains", "sky",
    "group photo", "beach", "city", "food", "animals", "baby"
]

def tag_image_with_clip(image_path):
    try:
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        text = clip.tokenize(CANDIDATE_LABELS).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text)

            logits_per_image, _ = model(image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

        tags = [label for label, prob in zip(CANDIDATE_LABELS, probs) if prob > 0.15]
        return tags
    except Exception as e:
        print("Tagging error:", e)
        return []
