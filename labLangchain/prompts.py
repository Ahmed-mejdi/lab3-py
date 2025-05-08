from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os

# Option 1: Set the API key as an environment variable
# os.environ["GROQ_API_KEY"] = "your-api-key-here"

# Option 2: Pass the API key directly to the client
llm = ChatGroq(
    api_key="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",  # Replace with your actual Groq API key
    model="llama3-70b-8192",
    temperature=0.3,
    max_tokens=500,
)

# Création d'un modèle de prompt avec des variables
prompt_template = PromptTemplate.from_template(
    "Listez {n} idées de plats pour la cuisine {cuisine} (nom uniquement)."
)

# Méthode 1: Utilisation séparée du template et du modèle
prompt = prompt_template.format(n=3, cuisine="italienne")
response = llm.invoke(prompt)
print("Méthode 1 - Réponse:")
print(response.content)
print("\n" + "-"*50 + "\n")

# Méthode 2: Utilisation de l'opérateur pipe pour créer une chaîne (chain)
chain = prompt_template | llm

# Exécution de la chaîne avec des paramètres spécifiques
response = chain.invoke({
    "n": 5,
    "cuisine": "française"
})

print("Méthode 2 - Prompt: Listez 5 idées de plats pour la cuisine française")
print("Réponse:")
print(response.content)