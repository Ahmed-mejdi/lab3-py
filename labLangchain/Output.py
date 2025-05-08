from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
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

# Définition d'un modèle de données pour la sortie
class Film(BaseModel):
    titre: str = Field(description="Le titre du film.")
    genre: list[str] = Field(description="Le(s) genre(s) du film.")
    annee: int = Field(description="L'année de sortie du film.")

# Création d'un parseur de sortie basé sur le modèle Film
parser = PydanticOutputParser(pydantic_object=Film)

# Définition du template de prompt avec des instructions de formatage
prompt_template_text = """
Répondez avec une recommandation de film basée sur la requête:

{format_instructions}

{query}
"""

format_instructions = parser.get_format_instructions()
prompt_template = PromptTemplate(
    template=prompt_template_text,
    input_variables=["query"],
    partial_variables={"format_instructions": format_instructions},
)

# Méthode 1: Exécution manuelle des étapes
prompt = prompt_template.format(query="Un film des années 90 avec Nicolas Cage.")
text_output = llm.invoke(prompt)
print("Sortie brute de l'IA:")
print(text_output.content)  # Format JSON
print("\nSortie structurée après parsing:")
parsed_output = parser.parse(text_output.content)
print(f"Titre: {parsed_output.titre}")
print(f"Genre: {', '.join(parsed_output.genre)}")
print(f"Année: {parsed_output.annee}")
print("\n" + "-"*50 + "\n")

# Méthode 2: Utilisation du langage d'expression LangChain (LCEL)
chain = prompt_template | llm | parser
response = chain.invoke({"query": "Un film d'action récent"})
print("Résultat avec LCEL:")
print(f"Titre: {response.titre}")
print(f"Genre: {', '.join(response.genre)}")
print(f"Année: {response.annee}")