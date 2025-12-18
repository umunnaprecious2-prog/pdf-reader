# pdf-reader.py - ✅ COMPLETE WORKING VERSION
import streamlit as st
import PyPDF2
from litellm import completion  # ✅ Direct LiteLLM import
import os

# Page config
st.set_page_config(page_title="PDF Chat App", page_icon="📄")
st.title("🤖 Chat with Your PDF")
st.markdown("---")

# API Key input
api_key = st.text_input(
    "OpenAI API Key", 
    type="password", 
    placeholder="sk-proj-...",
    help="Get from https://platform.openai.com/api-keys"
)

if not api_key:
    st.info("👈 Enter your OpenAI API key to start")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key

# LLM Test (before PDF upload)
@st.cache_data
def test_llm():
    """Test if API key works"""
    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API READY'"}],
            api_key=api_key,
            temperature=0
        )
        return True, response.choices[0].message.content
    except Exception as e:
        return False, str(e)

llm_test_ok, llm_test_msg = test_llm()
if llm_test_ok:
    st.success(f"✅ LLM Ready! Test: `{llm_test_msg}`")
else:
    st.error(f"❌ LLM Error: {llm_test_msg}")
    st.info("💡 Fix: Check API key + add credits at https://platform.openai.com/account/usage")
    st.stop()

# PDF Upload
uploaded_file = st.file_uploader("📁 Upload PDF", type="pdf")
if not uploaded_file:
    st.info("👈 Upload a PDF to chat with it")
    st.stop()

# Extract text
with st.spinner("🔄 Extracting text from PDF..."):
    reader = PyPDF2.PdfReader(uploaded_file)
    text_content = ""
    for page_num, page in enumerate(reader.pages, 1):
        text_content += f"\n--- Page {page_num} ---\n"
        text_content += page.extract_text() + "\n"

if not text_content.strip():
    st.error("❌ No text found in PDF!")
    st.stop()

st.success(f"✅ PDF loaded! {len(reader.pages)} pages, {len(text_content):,} characters")

# PDF Preview
with st.expander("📄 Preview PDF Content (first 2000 chars)", expanded=False):
    st.text_area("", text_content[:2000], height=200, disabled=True)

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💭 Ask a question about the PDF:"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # LiteLLM call
                response = completion(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are a helpful PDF assistant. Answer questions using ONLY the PDF content below.

PDF Content:
{text_content[:8000]}

IMPORTANT RULES:
1. Use ONLY information from the PDF above
2. If the answer is not in the PDF, say: "I couldn't find that information in the PDF"
3. Quote relevant sections when possible
4. Be concise and accurate"""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    api_key=api_key,
                    temperature=0.1,
                    max_tokens=1000
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.metric("📄 Pages", len(reader.pages) if 'reader' in locals() else 0)
    st.metric("📝 Characters", len(text_content) if 'text_content' in locals() else 0)
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.header("ℹ️ About")
    st.markdown("""
    **Tech Stack:**
    - 🎯 LiteLLM (OpenAI compatible)
    - 📄 PyPDF2 (PDF parsing)  
    - 🚀 Streamlit (UI)
    
    **Status:** ✅ All systems operational!
    """)
    
    st.markdown("---")
    st.info("""
    🔑 **API Key Tips:**
    1. Get from: https://platform.openai.com/api-keys
    2. Add credits: https://platform.openai.com/account/usage
    3. Copy the FULL `sk-proj-...` key
    """)

# Auto-scroll to bottom
st.markdown(
    """
    <script>
    parent = window.parent.document ?? document;
    const messages = parent.querySelectorAll('.stChatMessage');
    if (messages.length > 0) {
        messages[messages.length - 1].scrollIntoView({ behavior: 'smooth' });
    }
    </script>
    """,
    unsafe_allow_html=True
)