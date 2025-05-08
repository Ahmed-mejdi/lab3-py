from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os

# Option 1: Set the API key as an environment variable
# os.environ["GROQ_API_KEY"] = "your-api-key-here"

# Option 2: Pass the API key directly to the client initialization
chat_model = ChatGroq(
    api_key="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",  # Replace with your actual Groq API key
    model="llama3-70b-8192",
    temperature=0.3,  # Contrôle la créativité (0=déterministe, 1=créatif)
    max_tokens=500,
)

# Méthode 1: Simple invocation avec une chaîne de texte
response = chat_model.invoke("Quelles sont les 7 merveilles du monde?")
print(f"Réponse simple: {response.content}\n")

# Méthode 2: Utilisation de messages système et humain (plus flexible)
system_message = SystemMessage(
    content="Vous êtes un assistant éducatif qui explique les concepts de manière claire et concise."
)

question = "Expliquez-moi les bases de l'intelligence artificielle en 3 paragraphes."

messages = [
    system_message,
    HumanMessage(content=question)
]

response = chat_model.invoke(messages)

print("\nQuestion:", question)
print("\nRéponse détaillée:")
print(response.content)