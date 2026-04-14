import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_ID = "llama-3.3-70b-versatile"
MAX_TOKENS = 4096
MAX_DOC_CHARS = 60_000
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt", ".md"]