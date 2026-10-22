import base64
import io
import os
from PIL import Image
import requests
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
          "API Key missing. Please make sure GEMINI_API_KEY is configured in"
          " Streamlit Secrets."
      )
    else:
      with st.spinner("Analyzing plant pathology and generating treatment..."):
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = (
            "You are an expert crop pathologist and agronomy specialist.\n"
            "Examine this crop leaf image carefully and provide an actionable"
            " diagnosis report for farmers in the exact structure below:\n\n"
            "### 1. 🌾 Crop Identification\n"
            "- **Crop Name:** [Common name, e.g., Wheat, Maize, Tomato, Cotton,"
            " Rice, etc., and botanical name]\n"
            "- **Plant Part Analyzed:** [Leaf blade, veins, petiole, stem]\n\n"
            "### 2. 🩺 Health Status\n"
            "- **Status:** [State strictly in bold: **HEALTHY** or"
            " **DISEASED**]\n"
            "- **Confidence Score:** [High / Moderate / Low]\n\n"
            "### 3. 🔬 Disease Diagnosis (If Diseased)\n"
            "- **Pathology / Pest Name:** [Exact pathogen name, e.g., Early"
            " Blight, Rust, Downy Mildew, Leaf Spot, or 'None - Crop is"
            " Healthy']\n"
            "- **Severity Level:** [Mild / Moderate / Severe / Not"
            " Applicable]\n"
            "- **Observed Symptoms:** [Detail chlorosis, necrotic lesions,"
            " fungal spores, curling, or insect damage]\n\n"
            "### 4. 💊 Chemical Pesticide & Fungicide Recommendations (To Cure"
            " Disease)\n"
            "- **Recommended Chemical:** [Standard commercial formulations"
            " like Mancozeb 75% WP, Carbendazim 50% WP, Chlorpyrifos 20% EC,"
            " Copper Oxychloride, or 'None required']\n"
            "- **Standard Dosage:** [Exact dosage per 1 liter of water and per"
            " acre spray tank]\n"
            "- **Spraying Schedule:** [Time of spray (early morning/dusk) and"
            " repeat interval in days]\n\n"
            "### 5. 🌿 Organic & Natural Treatment\n"
            "- **Bio-Pesticide / Natural Remedy:** [Neem oil spray (5ml/L),"
            " Trichoderma viride, fermented buttermilk spray, or bio-fungicide"
            " application]\n"
            "- **Agronomic Management:** [Infected foliage removal, drip"
            " adjustment, aeration between rows]\n\n"
            "### 6. 🛡️ Long-Term Preventive Practices\n"
            "- [Seed treatment protocols, crop rotation, soil health"
            " improvement, and disease-resistant cultivars]\n\n"
            "If the provided image is not a plant leaf, state clearly that a"
            " valid agricultural leaf photo must be provided."
        )

        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64,
                        }
                    },
                ],
            }]
        }

        project_num = "434503069010"
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
        result_text = None
        error_logs = []

        for model_name in models_to_try:
          url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_num}/locations/us-central1/publishers/google/models/{model_name}:generateContent"
          headers = {
              "Content-Type": "application/json",
              "x-goog-api-key": api_key,
          }
          try:
            resp = requests.post(url, json=payload, headers=headers, timeout=35)
            if resp.status_code == 200:
              data = resp.json()
              result_text = data["candidates"][0]["content"]["parts"][0]["text"]
              break
            else:
              error_logs.append(f"{resp.status_code}: {resp.text}")
          except Exception as e:
            error_logs.append(str(e))

        if result_text:
          st.success("✅ Diagnosis Complete!")
          st.markdown(result_text)
        else:
          st.error("Diagnosis service response details:")
          for err in error_logs:
            st.code(err)

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