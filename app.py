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

# Sidebar Developer Card
with st.sidebar:
  st.markdown("### 👨‍💻 Project Developer")
  st.markdown(
      """
    <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px; border-radius: 6px;">
        <p style="margin: 0; color: #15803d; font-weight: bold; font-size: 15px;">Developed by Ganesh</p>
        <p style="margin: 4px 0 0 0; color: #4b5563; font-size: 13px;">Agronomy & Smart Crop Protection</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
  st.markdown("---")
  st.markdown(
      "**About this App:**\nPlant pathology diagnostic system to identify"
      " crops, detect diseases from leaf photos, and recommend targeted"
      " treatments."
  )

st.title("🌱 Crop Factor: Plant Disease Doctor")
st.write(
    "Upload or snap a photo of any crop leaf to identify diseases and get"
    " actionable remedies."
)

# Fetch Secret Safely
api_key = ""
try:
  if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
except Exception:
  pass

if not api_key:
  api_key = os.environ.get("GEMINI_API_KEY", "").strip()

# Input Options
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
  img = Image.open(image_file).convert("RGB")
  st.image(img, caption="Target Crop Leaf", use_container_width=True)

  if st.button(
      "🔍 Diagnose Crop Health", type="primary", use_container_width=True
  ):
    if not api_key:
      st.error(
          "API Key missing. Please ensure GEMINI_API_KEY is configured in"
          " Streamlit Secrets."
      )
    else:
      with st.spinner("Analyzing plant pathology and generating treatment..."):
        prompt = (
            "You are a senior agricultural specialist and crop pathologist.\n"
            "Examine this plant leaf carefully and output your report in the"
            " exact format below:\n\n"
            "### 1. 🌾 Crop Identification\n"
            "- **Crop / Plant Name:** [Common name and botanical name]\n\n"
            "### 2. 🩺 Health Status\n"
            "- **Condition:** [State clearly: 'HEALTHY' or 'DISEASED']\n"
            "- **Confidence Assessment:** [High / Moderate / Low]\n\n"
            "### 3. 🔬 Disease Diagnosis (If Diseased)\n"
            "- **Disease / Pest Name:** [Exact pathology name, or 'None - plant"
            " is healthy']\n"
            "- **Severity Level:** [Mild / Moderate / Severe / Not"
            " Applicable]\n"
            "- **Observed Symptoms:** [Detail chlorosis, fungal lesions,"
            " wilting, or pest damage]\n\n"
            "### 4. 💊 Chemical & Pesticide Recommendations\n"
            "- **Recommended Pesticide / Fungicide:** [Exact chemical names,"
            " e.g., Mancozeb, Chlorpyrifos, Carbendazim, Copper Oxychloride]\n"
            "- **Dosage & Application:** [Standard dilution in ml/g per liter"
            " of water and spraying interval]\n\n"
            "### 5. 🌿 Organic / Natural Recovery Methods\n"
            "- **Organic Treatment:** [Neem oil, bio-control agents like"
            " Trichoderma, wood ash dusting]\n"
            "- **Cultural Practices:** [Pruning diseased leaves, drip"
            " management, soil aeration]\n\n"
            "### 6. 🛡️ Preventive Action for Farmers\n"
            "- [Crop rotation, seed treatment, and resistant variety"
            " recommendations]\n\n"
            "If the image is not a plant or leaf, state clearly that a valid"
            " plant leaf image is required."
        )

        result_text = None
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]

        # Multi-engine fallback: Vertex AI mode (for Google Cloud bound keys) & Standard mode
        client_configs = [
            {
                "vertexai": True,
                "api_key": api_key,
                "project": "crop-doctor-512410",
                "location": "us-central1",
            },
            {"vertexai": True, "api_key": api_key},
            {"api_key": api_key},
        ]

        for config in client_configs:
          try:
            client = genai.Client(**config)
            for model_name in models_to_try:
              try:
                response = client.models.generate_content(
                    model=model_name, contents=[img, prompt]
                )
                if response and response.text:
                  result_text = response.text
                  break
              except Exception:
                time.sleep(0.5)
            if result_text:
              break
          except Exception:
            continue

        if result_text:
          st.success("✅ Diagnosis Complete!")
          st.markdown(result_text)
        else:
          st.warning(
              "System is busy processing requests. Please tap 'Diagnose Crop"
              " Health' once more."
          )

# Bottom corner branding
st.markdown("---")
st.markdown(
    """
    <div style="text-align: right; color: #6b7280; font-size: 13px; padding-top: 10px;">
        Designed & Developed with ❤️ by <b>Ganesh</b>
    </div>
    """,
    unsafe_allow_html=True,
)