

import os
import time
import streamlit as st
from PIL import Image
from google import genai
from google.genai import errors

st.set_page_config(
    page_title="Crop Factor - Plant Disease Doctor",
    layout="centered",
    page_icon="🌱",
)

# Sidebar
with st.sidebar:
    st.markdown("### 👨‍💻 Project Developer")
    st.markdown(
        """
        <div style="background-color:#f0fdf4;
        border-left:4px solid #16a34a;padding:12px;border-radius:6px;">
            <p style="margin:0;color:#15803d;font-weight:bold;">
                Developed by Ganesh
            </p>
            <p style="margin:4px 0 0 0;color:#4b5563;">
                Agronomy & Smart Crop Protection
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "**About this App:**\n\n"
        "Identify crops, examine leaf photos, and get disease "
        "diagnosis and treatment guidance."
    )

st.title("🌱 Crop Factor: Plant Disease Doctor")
st.write(
    "Upload or capture a crop leaf photo to check plant health "
    "and receive possible remedies."
)

# Read API key
api_key = ""

try:
    api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

# Image input
option = st.radio(
    "Choose Input Method:",
    ("📁 Upload Leaf Image", "📷 Live Camera Capture"),
    horizontal=True,
)

if option == "📁 Upload Leaf Image":
    image_file = st.file_uploader(
        "Choose a leaf photo...",
        type=["jpg", "jpeg", "png", "webp"],
    )
else:
    image_file = st.camera_input("Capture leaf via camera")

if image_file is not None:
    try:
        img = Image.open(image_file).convert("RGB")
        st.image(
            img,
            caption="Target Crop Leaf",
            use_container_width=True,
        )

        if st.button(
            "🔍 Diagnose Crop Health",
            type="primary",
            use_container_width=True,
        ):
            if not api_key:
                st.error(
                    "API key missing. Add GEMINI_API_KEY "
                    "in Streamlit Cloud → Settings → Secrets."
                )
            else:
                prompt = """
You are an agricultural crop disease assistant.

Examine the provided image carefully.

If it is not a plant leaf, explain that a valid crop leaf
photo is required.

If it is a leaf, provide this report in simple language:

### 1. Crop Identification
- Common crop name
- Botanical name, if identifiable
- Plant part examined

### 2. Health Status
- Status: HEALTHY, DISEASED, or UNCERTAIN
- Confidence: High, Moderate, or Low

### 3. Possible Disease Diagnosis
- Possible disease or pest
- Severity: Mild, Moderate, Severe, or Uncertain
- Visible symptoms
- Mention uncertainty if the image is unclear.

### 4. Treatment Guidance
- Appropriate disease management options
- Chemical treatment, if suitable
- Follow the product label and local agricultural advice
  for pesticide dosage and application.
- Do not invent unverified dosages.
- Include relevant safety precautions.

### 5. Organic and Natural Management
- Suitable organic options
- Removal of infected plant material
- Irrigation and field management suggestions

### 6. Prevention
- Crop rotation
- Resistant varieties
- Field sanitation
- Regular crop monitoring

### 7. Next Steps
- Explain what cannot be confirmed from the image alone.
- Recommend a local agricultural expert if the diagnosis
  is uncertain or the damage is severe.
"""

                client = genai.Client(api_key=api_key)

                # Retry temporary server errors
                result_text = None
                last_error = None

                with st.spinner(
                    "Analyzing the leaf. Please wait..."
                ):
                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.8-flash",
                                contents=[prompt, img],
                            )

                            if response and response.text:
                                result_text = response.text
                                break

                            last_error = "The model returned no text."
                            break

                        except errors.ServerError as e:
                            last_error = str(e)

                            if "503" not in str(e) or attempt == 2:
                                break

                            time.sleep(2 ** (attempt + 1))

                        except Exception as e:
                            last_error = str(e)
                            break

                if result_text:
                    st.success("✅ Diagnosis Complete!")
                    st.markdown(result_text)
                else:
                    st.error(
                        "Diagnosis could not be completed. "
                        "Please try again later."
                    )
                    if last_error:
                        st.code(last_error)

    except Exception:
        st.error(
            "Unable to open this image. Please upload a valid "
            "JPG, JPEG, PNG, or WEBP file."
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align:right;color:#6b7280;font-size:13px;">
        Designed & Developed with ❤️ by <b>Ganesh</b>
    </div>
    """,
    unsafe_allow_html=True,
)
