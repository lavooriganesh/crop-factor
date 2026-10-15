import json
import time
from PIL import Image
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Crop Factor", page_icon="🌾", layout="centered")

# --- CONFIGURE GEMINI API KEY ---
API_KEY = "AQ.Ab8RN6K2D-zzfN9b_HuMfsuBkJ-wDTiPZlDJnkZzVoMXTZm8yw"
genai.configure(api_key=API_KEY)

st.title("🌾 Crop Factor")
st.write("Upload or take a photo of any crop leaf for an automated clinical pathology and prescription report.")

mode = st.radio("Choose photo method:", ["📁 Upload Image", "📷 Take Photo"], horizontal=True)

source = None
if mode == "📁 Upload Image":
    source = st.file_uploader("Upload plant picture", type=["jpg", "jpeg", "png"])
else:
    source = st.camera_input("Take a photo of the plant leaf")

if source is not None:
    img = Image.open(source).convert("RGB")
    st.image(img, caption="Uploaded Foliage", use_container_width=True)

    with st.spinner("Analyzing pathology and structuring clinical report..."):
        prompt = """
        You are an expert plant pathologist and agronomist.
        Inspect this crop foliage and return strictly valid JSON conforming to this exact schema:
        {
          "is_plant": true or false,
          "crop_name": "Common Name (Botanical Name)",
          "is_healthy": true or false,
          "disease_name": "Pathogen and Disease Name (or 'None' if healthy)",
          "confidence_score": "High / Moderate / Low (with concise percentage like 92%)",
          "symptoms": "Clear visual symptoms observed on leaf blade, margins, or veins",
          "treatment": "Direct action steps and immediate measures to arrest active disease spread",
          "prevention": "Cultural practices, pruning, sanitization, and long-term preventive measures",
          "pesticide_advice": "Recommended chemical active ingredients, formulation (WP/EC), and exact dilution dosage per liter of water"
        }
        Output only clean, raw JSON. Do not enclose in markdown code fences.
        """

        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            generation_config={"temperature": 0.1}
        )

        response_text = None
        for _ in range(3):
            try:
                response = model.generate_content([prompt, img])
                response_text = response.text.strip()
                break
            except Exception as e:
                if "429" in str(e):
                    time.sleep(15)
                else:
                    st.error(f"Error: {e}")
                    break

        if response_text:
            try:
                clean_text = response_text
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                elif clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()

                data = json.loads(clean_text)

                st.divider()

                if not data.get("is_plant", False):
                    st.warning("⚠️ The uploaded image does not appear to be plant foliage. Please upload a clear leaf picture.")
                else:
                    # 1. Crop Name
                    st.markdown(f"## 🌾 Crop Name: **{data.get('crop_name', 'Unknown')}**")

                    if data.get("is_healthy", False):
                        st.success("✅ **Status: HEALTHY**")
                        st.info("The foliage exhibits clean tissue with no visible lesions. Maintain standard agronomic nutrition and watering.")
                    else:
                        # 2. Disease Name
                        st.error(f"### 🦠 Disease Name: **{data.get('disease_name', 'Undetermined Pathogen')}**")

                        # 3. Confidence Score
                        confidence = data.get("confidence_score", "Moderate")
                        st.metric(label="🎯 Confidence Score", value=confidence)

                        st.markdown("---")

                        # 4. Symptoms
                        st.subheader("🔍 Observed Symptoms")
                        st.info(data.get("symptoms", "No symptoms described."))

                        # 5. Treatment
                        st.subheader("💊 Treatment (Immediate Remediation)")
                        st.warning(data.get("treatment", "No immediate treatment specified."))

                        # 6. Prevention
                        st.subheader("🛡️ Prevention & Cultural Practices")
                        st.success(data.get("prevention", "No preventive measures specified."))

                        # 7. Pesticide Advice
                        st.subheader("🧪 Pesticide Advice (Dosage & Formulation)")
                        pesticide = data.get("pesticide_advice", "None required.")
                        st.markdown(
                            f"""
                            <div style="background-color: #2b1d0c; padding: 15px; border-left: 5px solid #ff9800; border-radius: 4px;">
                                <strong style="color: #ffb74d;">Chemical Prescription & Dilution:</strong><br>
                                <span style="color: #ffffff;">{pesticide}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            except Exception as parse_err:
                st.error(f"Failed to process diagnosis: {parse_err}")