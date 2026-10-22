import os
import time
from google import genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Crop Factor - Plant Disease Doctor",
    layout="centered",
    page_icon="🌱",
)

st.title("🌱 Crop Factor: Plant Doctor")
st.write(
    "Upload or snap a photo of any crop leaf to detect diseases and get"
    " actionable remedies."
)

# Robust Multi-source Key Retrieval
API_KEY = "AQ.Ab8RN6KLCajoNbliDmCrwqDlt8ZdXdpqU5-5936shd4ZL471aQ"
try:
  if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
  pass

if not API_KEY:
  API_KEY = os.environ.get(
      "GEMINI_API_KEY", "AQ.Ab8RN6KLCajoNbliDmCrwqDlt8ZdXdpqU5-5936shd4ZL471aQ"
  )

client = genai.Client(api_key=API_KEY)

# Flexible image capture for Mobile & Laptop
option = st.radio(
    "Choose Input Method:",
    ("📁 Upload Leaf Image", "📷 Live Camera Capture"),
    horizontal=True,
)
image_file = None

if option == "📁 Upload Leaf Image":
  image_file = st.file_uploader(
      "Choose a leaf photo...", type=["jpg", "jpeg", "png", "webp"]
  )
else:
  image_file = st.camera_input("Capture leaf via camera")

if image_file is not None:
  img = Image.open(image_file)
  st.image(img, caption="Target Crop Leaf", use_container_width=True)

  if st.button(
      "🔍 Diagnose Crop Health", type="primary", use_container_width=True
  ):
    with st.spinner("Analyzing plant pathology and generating treatment..."):
      # Structured botanical & agronomic prompt
      prompt = (
          "You are a senior agricultural extension specialist and crop"
          " pathologist.\n"
          "Examine the provided plant image carefully and output the"
          " evaluation using the following structure:\n\n"
          "### 1. 🌾 Crop Identification\n"
          "- **Crop / Plant Name:** [Common name and botanical name]\n\n"
          "### 2. 🩺 Health Status\n"
          "- **Condition:** [State clearly: 'HEALTHY' or 'DISEASED']\n"
          "- **Confidence Assessment:** [High / Moderate / Low]\n\n"
          "### 3. 🔬 Disease Diagnosis (If Diseased)\n"
          "- **Disease / Pest Name:** [Exact pathology name, or 'None - plant is"
          " healthy']\n"
          "- **Severity Level:** [Mild / Moderate / Severe]\n"
          "- **Observed Symptoms:** [Detail discoloration, chlorosis, fungal"
          " pustules, necrosis, or pest bites]\n\n"
          "### 4. 💊 Chemical & Pesticide Recommendations\n"
          "- **Recommended Pesticide / Fungicide:** [Specific chemical active"
          " ingredients, e.g., Mancozeb, Chlorpyrifos, Carbendazim, Copper"
          " Oxychloride, Azoxystrobin]\n"
          "- **Dosage & Application:** [Standard dilution in ml/g per liter of"
          " water and spraying interval]\n\n"
          "### 5. 🌿 Organic / Natural Recovery Methods\n"
          "- **Organic Spray:** [Neem kernel extract / neem oil, bio-control"
          " agents like Trichoderma viride or Pseudomonas fluorescens]\n"
          "- **Cultural Practices:** [Soil drainage, pruning diseased leaves,"
          " balanced NPK fertilization]\n\n"
          "### 6. 🛡️ Preventive Action for Farmers\n"
          "- [Crop rotation, seed treatment, and resistant variety"
          " recommendations]\n\n"
          "If the image is not a plant or leaf, state clearly that a plant leaf"
          " photo is required."
      )

      # Resilient multi-model sequence: starts with official dynamic alias
      models_to_try = [
          "gemini-flash-latest",
          "gemini-3.8-flash",
          "gemini-3.5-flash",
          "gemini-3-flash",
      ]
      result_text = None
      error_log = []

      for model in models_to_try:
        try:
          response = client.models.generate_content(
              model=model, contents=[img, prompt]
          )
          if response and response.text:
            result_text = response.text
            break
        except Exception as err:
          error_log.append(f"{model}: {str(err)}")
          time.sleep(1.0)  # Brief pause before fallback attempt

      if result_text:
        st.success("✅ Diagnosis Complete!")
        st.markdown(result_text)
      else:
        st.error("Diagnostic service temporarily unavailable. Please retry.")
        with st.expander("Diagnostic details"):
          st.write(error_log)