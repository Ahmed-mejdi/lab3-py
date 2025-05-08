from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Add your Groq API key here
groq_api_key = "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"  

# Initialisation du modèle
llm = ChatGroq(
    api_key=groq_api_key,  # Add this line
    model="llama3-70b-8192",
    temperature=0.7,
    max_tokens=500,
)

# Initialisation du modèle
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.7,  # Plus créatif pour les conversations
    max_tokens=500,
)

# Création d'un template de prompt qui utilise la mémoire de conversation
template = """
Vous êtes un assistant amical et serviable. Vous avez une mémoire et vous vous souvenez de 
ce que l'utilisateur vous a dit précédemment dans la conversation.

Historique de la conversation:
{chat_history}

Humain: {input}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    template=template
)

# Initialisation de la mémoire (stocke l'historique des messages)
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="chat_history"
)

# Création de la chaîne de conversation
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True
)

# Simulation d'une conversation
questions = [
    "Bonjour! Comment vous appelez-vous?",
    "Quels sont vos hobbies?",
    "Vous souvenez-vous de mon premier message?",
    "Pouvez-vous résumer notre conversation?"
]

for question in questions:
    print(f"\nHumain: {question}")
    response = conversation.predict(input=question)
    print(f"Assistant: {response}")