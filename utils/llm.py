from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class LanguageModel:
    def __init__(self, model_name="gpt-4o", temperature=0, fake_model=False):
        if (fake_model):
            self.llm = type("FakeLLM", (), {"invoke": lambda self, prompt: type("FakeResponse", (), {"content": f"FAKE RESPONSE: {prompt}"})()})()
        else:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def predict(self, prompt):
        return self.llm.invoke(prompt).content

LLM = LanguageModel()

if __name__ == "__main__":
    llm = LanguageModel(fake_model=False)
    while True:
        prompt = input("Enter prompt (or 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        response = llm.predict(prompt)
        print("Response:", response)
