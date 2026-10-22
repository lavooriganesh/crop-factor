import base64
import io
import os
import requests
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
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = (
            "You are an expert crop doctor, agronomist, and plant"
            " pathologist.\nCarefully analyze this leaf image and generate a"
            " comprehensive report in the exact format below:\n\n### 1. 🌾 Crop"
            " Identification\n- **Crop / Plant Name:** [Identify the exact"
            " crop, e.g., Wheat, Maize, Tomato, Cotton, Rice, etc., with"
            " botanical name]\n- **Part Inspected:** [Leaf, stem, or"
            " fruit]\n\n### 2. 🩺 Health Status\n- **Condition:** [State"
            " clearly in bold: **HEALTHY** or **DISEASED**]\n- **Confidence"
            " Level:** [High / Moderate / Low]\n\n### 3. 🔬 Disease Diagnosis"
            " (If Diseased)\n- **Disease or Pest Name:** [Exact pathology name,"
            " e.g., Early Blight, Powdery Mildew, Leaf Rust, Stem Borer, or"
            " 'None - Plant is Healthy']\n- **Severity Level:** [Mild /"
            " Moderate / Severe / None]\n- **Observed Symptoms:** [Detail"
            " specific leaf damage, spots, chlorosis, fungal patches, or insect"
            " feeding marks]\n\n### 4. 💊 Chemical Pesticide & Fungicide"
            " Treatment (To Restore Crop Health)\n- **Recommended Chemical:**"
            " [Specific chemical name, e.g., Mancozeb, Chlorpyrifos,"
            " Carbendazim, Copper Oxychloride, Azoxystrobin, or 'None"
            " needed']\n- **Exact Dosage:** [Dosage in ml or grams per 1 Liter"
            " of water]\n- **Application Schedule:** [Spray intervals, e.g.,"
            " spray once early morning, repeat after 10-12 days if needed]\n\n###"
            " 5. 🌿 Organic & Natural Remedies\n- **Organic Formulation:**"
            " [Neem oil spray (5ml/L), Trichoderma viride bio-fungicide, or"
            " fermented buttermilk spray]\n- **Cultural Field Practices:**"
            " [Prune and burn infected leaves, improve furrow drainage, reduce"
            " overhead watering]\n\n### 6. 🛡️ Preventive Measures for"
            " Farmers\n- [Seed treatment before sowing, crop rotation with"
            " non-host crops, and use of disease-resistant varieties]\n\nIf the"
            " uploaded image is not a plant or leaf, state clearly that a valid"
            " plant leaf photo is required."
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

        # Targeted endpoint list configured for Project 434503069010 and AQ Auth Keys
        project_num = "434503069010"
        endpoints_to_try = [
            # 1. Google Cloud Vertex AI Express endpoint for Project 434503069010
            (
                f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_num}/locations/us-central1/publishers/google/models/gemini-2.0-flash:generateContent",
                {"Authorization": f"Bearer {api_key}"},
            ),
            (
                f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_num}/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent",
                {"Authorization": f"Bearer {api_key}"},
            ),
            # 2. Direct x-goog-api-key on project endpoint
            (
                f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_num}/locations/us-central1/publishers/google/models/gemini-2.0-flash:generateContent",
                {"x-goog-api-key": api_key},
            ),
            # 3. Direct Gemini Developer API with Bearer token
            (
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                {"Authorization": f"Bearer {api_key}"},
            ),
        ]

        result_text = None
        error_logs = []

        for url, auth_hdr in endpoints_to_try:
          headers = {"Content-Type": "application/json"}
          headers.update(auth_hdr)
          try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
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