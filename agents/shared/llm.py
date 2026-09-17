import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.shared.config import GEMINI_MODEL


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)