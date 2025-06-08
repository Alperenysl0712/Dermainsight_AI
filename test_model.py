import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from torchvision import transforms
from PIL import Image, ImageFilter, ImageEnhance


class EfficientNetB0FineTune(nn.Module):
    def __init__(self, num_classes):
        super(EfficientNetB0FineTune, self).__init__()
        self.model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
        in_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.model(x)

def enhance_image(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(1.5)  # kontrast artırılır
    image = ImageEnhance.Sharpness(image).enhance(2.0) # netlik artırılır
    image = image.filter(ImageFilter.MedianFilter(size=3)) # gürültü azaltılır
    return image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_names = [
    "nevus",
    "melanoma",
    "seborrheic keratosis",
    "dermatofibroma",
    "basal cell carcinoma",
    "squamous cell carcinoma",
    "pigmented benign keratosis"
]

model = EfficientNetB0FineTune(num_classes=len(class_names))
model.load_state_dict(torch.load("best_model_EfficientNetB0 88-91.pth", map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def predict_image(file_path):
    image = Image.open(file_path).convert("RGB")

    image = enhance_image(image)

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        top_probs, top_indices = torch.topk(probs, k=3)

    predictions = []
    for i in range(3):
        idx = top_indices[0][i].item()
        predictions.append({
            "class": class_names[idx],
            "probability": round(top_probs[0][i].item(), 4)
        })

    return predictions