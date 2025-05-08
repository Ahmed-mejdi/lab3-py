from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 1. Préparation du document (exemple)
documents = ["""
LangChain est un framework pour développer des applications alimentées par des modèles de langage.
Il permet aux développeurs de créer facilement des chaînes de traitement complexes qui combinent
différents modèles et outils pour créer des applications sophistiquées telles que des chatbots,
des générateurs de contenu, et des systèmes de réponse à des questions.

Parmi les fonctionnalités principales de LangChain on trouve:
- Les chaînes (chains) qui permettent d'enchaîner différentes opérations
- Les agents qui peuvent prendre des décisions sur les outils à utiliser
- Les templates de prompts qui facilitent la création de messages structurés
- Les outils qui connectent les modèles à des API et services externes
- La mémoire qui permet de stocker et récupérer l'historique des conversations

LangChain est disponible en Python et JavaScript, ce qui permet une intégration
facile dans différents environnements de développement.
"""]

# 2. Fractionnement du texte en morceaux plus petits
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_text(documents[0])

# 3. Création d'embeddings avec un modèle HuggingFace gratuit
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 4. Création d'une base de vecteurs avec FAISS
vector_store = FAISS.from_texts(chunks, embeddings)

# 5. Initialisation du modèle de chat
chat_model = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.3,
    max_tokens=500,
)

# 6. Configuration de la mémoire pour la conversation
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 7. Création de la chaîne de récupération conversationnelle
retrieval_chain = ConversationalRetrievalChain.from_llm(
    llm=chat_model,
    retriever=vector_store.as_retriever(),
    memory=memory,
    verbose=True
)

# 8. Exemple d'utilisation
questions = [
    "Qu'est-ce que LangChain?",
    "Quelles sont ses fonctionnalités principales?",
    "Est-il disponible en JavaScript?"
]

for question in questions:
    print(f"\nQuestion: {question}")
    result = retrieval_chain.invoke({"question": question})
    print(f"Réponse: {result['answer']}")