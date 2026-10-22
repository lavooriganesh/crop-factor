
import os
import streamlit as st
from PIL import Image
from google import genai

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
        "Identify crops, examine leaf photos, and get "
        "disease diagnosis and treatment guidance."
    )

st.title("🌱 Crop Factor: Plant Disease Doctor")
st.write(
    "Upload or capture a crop leaf photo to check plant health "
    "and receive possible remedies."
)

# Read API key from Streamlit Secrets or environment
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

If the image is not a plant leaf, explain that the user
must upload a valid crop leaf image.

If it is a leaf, provide the following report:

### 1. Crop Identification
- Common crop name
- Botanical name if identifiable
- Plant part examined

### 2. Health Status
- Status: HEALTHY, DISEASED, or UNCERTAIN
- Confidence: High, Moderate, or Low

### 3. Possible Disease Diagnosis
- Possible disease or pest
- Severity: Mild, Moderate, Severe, or Uncertain
- Visible symptoms
- Explain when the image is not clear enough to confirm.

### 4. Treatment Guidance
- Possible control methods
- Suitable chemical treatment, if appropriate
- Explain that pesticide choice and dosage must follow
  the product label and local agricultural guidance.
- Do not invent exact dosages if they cannot be verified.
- Mention safety precautions and pre-harvest restrictions.

### 5. Organic and Natural Management
- Suitable options, where appropriate
- Removal of infected plant material
- Irrigation and field management suggestions

### 6. Prevention
- Crop rotation
- Resistant varieties
- Field sanitation
- Monitoring and other relevant practices

### 7. Confidence and Next Steps
- State what cannot be confirmed from the image alone.
- Recommend consulting a local agricultural officer
  if the diagnosis is uncertain or the damage is severe.

Use simple language that farmers can understand.
Do not claim a disease is confirmed from an unclear image.
"""

                try:
                    with st.spinner(
                        "Examining the leaf and preparing recommendations..."
                    ):
                        client = genai.Client(api_key=api_key)

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[prompt, img],
                        )

                    if response and response.text:
                        st.success("✅ Diagnosis Complete!")
                        st.markdown(response.text)
                    else:
                        st.warning(
                            "No diagnosis was returned. "
                            "Please try a clearer leaf photo."
                        )

                except Exception as e:
                    st.error(
                        "Diagnosis failed. Check your API key, "
                        "model availability, internet connection, "
                        "or API usage limits."
                    )
                    st.code(str(e))

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
