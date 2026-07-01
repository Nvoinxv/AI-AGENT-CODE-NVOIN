from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class BaseTool(ABC):
    """Kelas dasar abstrak untuk semua tools yang dapat dipanggil agen."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Menjalankan fungsionalitas tool dengan argumen yang diberikan."""
        pass

    def to_function_definition(self) -> Dict[str, Any]:
        """Mengembalikan skema tool dalam format OpenAI/LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
