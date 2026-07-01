import streamlit as st
import PyPDF2
import json
import os

from dotenv import load_dotenv
from groq import Groq


# Load .env variables
load_dotenv()


# Groq AI Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



# AI function
def ask_ai(prompt):

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content



# Page settings
st.set_page_config(
    page_title="AI Resume Scanner",
    page_icon="📄",
    layout="wide"
)


st.title("📄 AI Resume ATS Scanner")
st.caption("Upload your resume and get AI-powered ATS feedback")



# Extract text from PDF
def extract_pdf(file):

    reader = PyPDF2.PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text


    return text




# Layout

left, right = st.columns([1, 1])



# Left side inputs

with left:

    st.subheader("Upload Resume")


    resume_file = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"]
    )


    job_role = st.text_input(
        "Target Job Role",
        placeholder="Example: Data Scientist"
    )


    job_desc = st.text_area(
        "Job Description (Optional)",
        height=150
    )


    scan_btn = st.button(
        "Scan Resume",
        use_container_width=True
    )




# Right side output

with right:


    if scan_btn:


        if not resume_file:

            st.error(
                "Please upload a PDF resume"
            )


        elif not job_role:

            st.error(
                "Please enter a target job role"
            )


        else:


            with st.spinner("Analyzing resume..."):


                # Extract PDF text

                resume_text = extract_pdf(
                    resume_file
                )


                # AI prompt

                prompt = (

                    "You are an ATS and HR expert. "
                    "Analyze this resume for the role: "
                    + job_role

                    +

                    "\n\nResume text:\n"

                    + resume_text[:3000]

                    +

                    "\n\nReturn ONLY valid JSON."

                    +

                    "\nJSON format should contain:"

                    "\nats_score (0-100)"

                    "\noverall_rating"

                    "\nstrengths (3 items)"

                    "\nweaknesses (3 items)"

                    "\nmissing_keywords (5 items)"

                    "\nimprovement_tips (3 items)"

                    "\nsummary (2 sentences)"

                )



                # Get AI response

                raw = ask_ai(prompt).strip()



                # Clean JSON response

                if "```" in raw:

                    raw = raw.split("```")[1]


                if raw.startswith("json"):

                    raw = raw.replace(
                        "json",
                        "",
                        1
                    )



                try:

                    result = json.loads(raw)


                except:

                    st.error(
                        "AI response was not valid JSON. Try again."
                    )

                    st.stop()



                # Score display

                score = result["ats_score"]



                if score >= 75:

                    status = "🟢 Strong Resume"


                elif score >= 50:

                    status = "🟠 Average Resume"


                else:

                    status = "🔴 Needs Improvement"



                st.metric(
                    "ATS Score",
                    f"{score}/100"
                )


                st.subheader(status)



                st.info(
                    result["summary"]
                )



                # Results columns

                c1, c2 = st.columns(2)



                with c1:


                    st.success(
                        "Strengths"
                    )


                    for item in result["strengths"]:

                        st.write(
                            "• " + item
                        )



                    st.error(
                        "Weaknesses"
                    )


                    for item in result["weaknesses"]:

                        st.write(
                            "• " + item
                        )




                with c2:


                    st.warning(
                        "Missing Keywords"
                    )


                    for item in result["missing_keywords"]:

                        st.write(
                            "• " + item
                        )



                    st.info(
                        "Improvement Tips"
                    )


                    for item in result["improvement_tips"]:

                        st.write(
                            "• " + item
                        )