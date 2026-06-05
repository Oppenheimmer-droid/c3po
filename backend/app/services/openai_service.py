from app.core.settings import settings

class MockOpenAI:
    def chat(self, message: str):
        return {"mock": True, "response": f"MOCK RESPONSE: {message}"}

def get_openai_client():
    if settings.OPENAI_MOCK or settings.OPENAI_API_KEY in ("", "mock", "test", "dummy"):
        print("⚠️ OpenAI en modo MOCK")
        return MockOpenAI()
    else:
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)
