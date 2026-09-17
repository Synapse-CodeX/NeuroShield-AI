import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

MAX_LLM_WORKERS = int(
    os.getenv("MAX_LLM_WORKERS", "3")
)

MAX_SEARCH_WORKERS = int(
    os.getenv("MAX_SEARCH_WORKERS", "3")
)

TAVILY_MAX_RESULTS = int(
    os.getenv("TAVILY_MAX_RESULTS", "5")
)

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "15")
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)