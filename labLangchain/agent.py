from langchain_groq import ChatGroq
from langchain.tools import DuckDuckGoSearchRun
from langchain.chains import LLMMathChain
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, Tool
from langchain.agents.structured_chat.base import StructuredChatAgent
import os

# Set your API key
# os.environ["GROQ_API_KEY"] = "your-valid-api-key-here"
# OR pass it directly to the model
llm = ChatGroq(
    api_key="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",  # Replace with your valid API key
    model="llama3-70b-8192",
    temperature=0.3,
    max_tokens=1024,
)

# IMPORTANT FIX: Use the default LLMMathChain prompt instead of custom one
# The default prompt ensures the output format is compatible with the parser
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

# Alternative solution: If you want to use a custom prompt, make sure it produces 
# an output format that LLMMathChain can parse - ensure it returns just a number
# math_prompt = PromptTemplate.from_template(
#     "Calculez l'expression mathématique suivante: {question}\n\nExprimez votre réponse seulement comme un nombre sans texte."
# )
# llm_math_chain = LLMMathChain.from_llm(llm=llm, prompt=math_prompt, verbose=True)

# Initialisation des outils
# 1. Outil de recherche web
search = DuckDuckGoSearchRun()

# 2. Outil de calcul avec description en français
calculator = Tool(
    name="calculatrice",
    description="Utilisez cet outil pour les calculs arithmétiques. L'entrée doit être une expression mathématique.",
    func=llm_math_chain.run,  # Important: use .run directly instead of lambda
)

# Liste des outils pour l'agent
tools = [
    Tool(
        name="recherche",
        description="Recherchez sur internet des informations sur les événements actuels, des données ou des faits. Utilisez ceci pour rechercher des chiffres de population, des statistiques ou d'autres informations factuelles.",
        func=search.run
    ),
    calculator
]

# Création de l'agent avec StructuredChatAgent
agent = StructuredChatAgent.from_llm_and_tools(
    llm=llm,
    tools=tools
)

# Initialisation de l'exécuteur d'agent
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True
)

# Exécution de l'agent avec une requête complexe
result = agent_executor.invoke({
    "input": "Quelle est la différence de population entre la France et l'Allemagne? Ensuite, calculez ce nombre divisé par 1000."
})

print("\nRésultat final:")
print(result["output"])