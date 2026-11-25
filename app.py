# ==============================================================================
# Project: Universal AI Assistant for Reading & Analyzing Any File in Any Language
# Libraries: streamlit (UI) | google-genai (Multimodal AI) | python-docx (Word files)
# ==============================================================================

# Import io library to handle file data in temporary memory (Bytes)
import io
# Import docx library to read and extract text from Microsoft Word (.docx) files
import docx
# Import official Google library to communicate with Gemini models
from google import genai
# Import types module to wrap raw files (images, PDF, audio) and send them directly to the model
from google.genai import types
# Import library to build the interactive web interface
import streamlit as st


# --- Section 1: User Interface (UI) Design ---

# Display the main application title at the top of the page
st.title("Your First Assistant in Analyzing Any File")

# Create a text input in the sidebar for the API key and mask characters for security
api_key = st.sidebar.text_input("Enter Gemini API key:", type="password")

# Omitting type="pdf" from file_uploader allows the app to accept any file format
uploaded_file = st.file_uploader(
    "Upload any file type (PDF, Image, Word, Text, Audio, CSV...)"
)


# --- Section 2: Processing the Uploaded File Regardless of Type or Language ---

# Check if the user has actually uploaded a file
if uploaded_file is not None:

  # Display an info bar showing the file name and its technical MIME type
  st.info(f"File uploaded: {uploaded_file.name} | Type: {uploaded_file.type}")

  # Input box for the question with a default prompt instructing the model to reply in the file's language
  question = st.text_input(
      "Tell us your question or request about the file:",
      value="Read the file and summarize it in the same language, in clear points",
  )

  # When the "Analyze & Answer" button is clicked
  if st.button("Analyze & Answer"):

    # First, verify that the user did not forget to enter the API key
    if not api_key:
      st.warning("Please enter the Gemini API key in the sidebar first.")
    else:
      # Show an animated loading spinner while processing the file
      with st.spinner("Analyzing the file..."):

        # Initialize the connection client with Google servers using your API key
        client = genai.Client(api_key=api_key)

        # Case 1: If the file is in Word (.docx) format
        # Use python-docx to extract paragraphs so Gemini reads the text with higher accuracy
        if uploaded_file.name.endswith(".docx"):
          # Convert the uploaded file bytes into an in-memory stream for docx to open
          doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
          # Join all paragraphs into a single structured text string
          extracted_text = "\n".join([p.text for p in doc.paragraphs])
          # Prepare the text prompt to send to the model
          contents = [
              f"Based on the following text:\n{extracted_text}\n\nRequest: {question}"
          ]

        # Case 2: Any other file (Arabic/English PDF, images, scanned docs, audio, code, CSV)
        else:
          # Identify the technical MIME type; fallback to plain text if unknown
          mime_type = uploaded_file.type or "text/plain"

          # Convert generic binary types (like .py or .md files) to text/plain
          if mime_type == "application/octet-stream":
            mime_type = "text/plain"

          # Package raw file bytes with its MIME type so Gemini can read it directly
          file_part = types.Part.from_bytes(
              data=uploaded_file.getvalue(), mime_type=mime_type
          )

          # Combine the file package and the user's question to send together
          contents = [file_part, question]

        # Send the file and question to gemini-3.8-flash (supports multilingual & multimodal input)
        response = client.models.generate_content(
            model="gemini-3.8-flash", contents=contents
        )

        # Display the final response on the screen
        st.write(response.text)