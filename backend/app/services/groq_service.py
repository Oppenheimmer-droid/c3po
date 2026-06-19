from groq import Groq
from app.core.settings import settings


class GroqService:
    def __init__(self):
        if settings.GROQ_MOCK or settings.GROQ_API_KEY in ("", "mock", "test", "dummy"):
            self.client = None
            print("⚠️ Groq en modo MOCK")
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def chat(self, messages: list, model: str = None) -> dict:
        """Send chat request to Groq API."""
        if self.client is None:
            return self._mock_response(messages)
        
        model = model or settings.GROQ_MODEL
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }
    
    def chat_stream(self, messages: list, on_chunk: callable, model: str = None):
        """Send streaming chat request to Groq API."""
        if self.client is None:
            content = f"[MOCK] Respuesta a: {messages[-1]['content'] if messages else '?'}"
            for word in content.split():
                on_chunk(word + " ")
            return
        
        model = model or settings.GROQ_MODEL
        
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                on_chunk(chunk.choices[0].delta.content)
    
    def _mock_response(self, messages: list) -> dict:
        """Generate mock response for testing."""
        last_message = messages[-1]["content"] if messages else "?"
        return {
            "content": f"[MOCK RESPONSE] Recibido: {last_message}. Esta es una respuesta simulada de Groq.",
            "model": "mock-groq",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            }
        }


def get_groq_service() -> GroqService:
    """Factory function to get Groq service instance."""
    return GroqService()