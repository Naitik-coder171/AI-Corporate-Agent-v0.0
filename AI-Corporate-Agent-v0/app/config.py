import os
from dataclasses import dataclass
from dotenv import load_dotenv  # type: ignore

load_dotenv()


@dataclass
class AppConfig:
    openai_api_key: str | None
    openai_api_base: str | None
    openai_model: str
    ollama_base_url: str
    ollama_model: str
    embedding_model: str
    vector_db_path: str
    reference_dir: str
    output_dir: str


def load_config() -> AppConfig:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # Choose embedding default: OpenAI if available else Ollama embedding model
    default_embedding = (
        os.getenv("EMBEDDING_MODEL")
        or ("text-embedding-3-small" if openai_api_key else "ollama:nomic-embed-text")
    )
    return AppConfig(
        openai_api_key=openai_api_key,
        openai_api_base=os.getenv("OPENAI_API_BASE"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        ollama_base_url=ollama_base_url,
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        embedding_model=default_embedding,
        vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/vector"),
        reference_dir=os.getenv("REFERENCE_DIR", "./data/reference"),
        output_dir=os.getenv("OUTPUT_DIR", "./outputs"),
    ) 