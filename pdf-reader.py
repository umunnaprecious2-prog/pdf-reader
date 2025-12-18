# pdf-reader.py - ✅ STREAMLIT CLOUD READY VERSION

import streamlit as st
import PyPDF2
from litellm import completion
import os

# --------------------------------------------------
# Load API key from Streamlit Secrets
# --------------------------------------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY not found in Streamlit secrets")
    st.stop()

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="PDF Chat App", page_icon="📄")
st.title("🤖 Chat with Your PDF")
st.markdown("---")

# --------------------------------------------------
# Test LLM connection
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def test_llm():
    try:
        response = completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say API READY"}],
            temperature=0
        )
        return True, response.choices[0].message.content
    except Exception as e:
        return False, str(e)

llm_ok, llm_msg = test_llm()
if llm_ok:
    st.success(f"✅ LLM Ready: `{llm_msg}`")
else:
    st.error(f"❌ LLM Error: {llm_msg}")
    st.stop()

# --------------------------------------------------
# PDF Upload
# --------------------------------------------------
uploaded_file = st.file_uploader("📁 Upload PDF", type="pdf")
if not uploaded_file:
    st.info("👈 Upload a PDF to start chatting")
    st.stop()

# --------------------------------------------------
# Extract PDF text
# --------------------------------------------------
with st.spinner("🔄 Extracting text from PDF..."):
    reader = PyPDF2.PdfReader(uploaded_file)
    text_content = ""

    for page_num, page in enumerate(reader.pages, 1):
        extracted = page.extract_text()
        if extracted:
            text_content += f"\n--- Page {page_num} ---\n{extracted}\n"

if not text_content.strip():
    st.error("❌ No readable text found in this PDF")
    st.stop()

st.success(f"✅ PDF loaded: {len(reader.pages)} pages")

# --------------------------------------------------
# Preview
# --------------------------------------------------
with st.expander("📄 Preview PDF Content (first 2000 chars)"):
    st.text_area("", text_content[:2000], height=200, disabled=True)

# --------------------------------------------------
# Chat state
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------
# Chat input
# --------------------------------------------------
if prompt := st.chat_input("💭 Ask a question about the PDF"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = completion(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
You are a PDF assistant.
Answer ONLY from the content below.

PDF CONTENT:
{text_content[:8000]}

Rules:
- If not found, say: "I couldn't find that information in the PDF"
- Quote sections when possible
- Be concise
"""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=800
                )

                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ App Info")
    st.metric("📄 Pages", len(reader.pages))
    st.metric("📝 Characters", len(text_content))

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("""
**Tech Stack**
- LiteLLM
- PyPDF2
- Streamlit
""")

