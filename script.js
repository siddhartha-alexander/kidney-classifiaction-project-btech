const cards = document.querySelectorAll(".overview-grid article, .step, .metric-list article, .team-grid article");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
      }
    });
  },
  { threshold: 0.14 }
);

cards.forEach((card) => observer.observe(card));

const scanUpload = document.querySelector("#scanUpload");
const scanPreview = document.querySelector("#scanPreview");
const previewBox = document.querySelector(".preview-box");
const evaluateButton = document.querySelector("#evaluateButton");
const predictionClass = document.querySelector("#predictionClass");
const predictionText = document.querySelector("#predictionText");
const confidenceFill = document.querySelector("#confidenceFill");

const labels = ["Cyst", "Normal", "Stone", "Tumor"];

const getPredictUrl = () => {
  if (window.location.port === "5173") {
    return "http://127.0.0.1:8000/api/predict";
  }

  return "/api/predict";
};

scanUpload?.addEventListener("change", () => {
  const file = scanUpload.files?.[0];

  if (!file) {
    return;
  }

  scanPreview.src = URL.createObjectURL(file);
  previewBox.classList.add("has-image");
  predictionClass.textContent = "Ready to evaluate";
  predictionText.textContent = "Click evaluate to classify the uploaded scan image.";
  confidenceFill.style.width = "0";
});

evaluateButton?.addEventListener("click", async () => {
  const file = scanUpload.files?.[0];

  if (!file) {
    predictionClass.textContent = "No image selected";
    predictionText.textContent = "Please upload a CT or X-ray image first.";
    confidenceFill.style.width = "0";
    return;
  }

  predictionClass.textContent = "Evaluating...";
  predictionText.textContent = "Running the trained ResNet18 model on the uploaded image.";
  confidenceFill.style.width = "20%";

  try {
    const formData = new FormData();
    formData.append("image", file);

    const response = await fetch(getPredictUrl(), {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Prediction request failed.");
    }

    predictionClass.textContent = result.prediction;
    predictionText.textContent = `Predicted class: ${result.prediction}. Confidence: ${result.confidence}%.`;
    confidenceFill.style.width = `${result.confidence}%`;
  } catch (error) {
    predictionClass.textContent = "Backend not connected";
    predictionText.textContent =
      "Start the Python server to run real model prediction, then evaluate again.";
    confidenceFill.style.width = "0";
  }
});
