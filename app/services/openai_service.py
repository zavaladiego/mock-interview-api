from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_objectbox.vectorstores import ObjectBox
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from openai import OpenAI
import os

# Load environment variables
OpenAI_key = os.getenv("OPENAI_API_KEY")
if not OpenAI_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")

# Initialize and configure the retrieval chain
def initialize_qa_chain():
    # Valida that ./data/context.txt exists\
    context_file = "./data/context.txt"
    if not os.path.exists(context_file):
        raise FileNotFoundError("File ./data/context.txt not found")
    
    loader = TextLoader(context_file)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(data)
    vector = ObjectBox.from_documents(documents, OpenAIEmbeddings(openai_api_key=OpenAI_key), embedding_dimensions=768)
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OpenAI_key)
    prompt = hub.pull("rlm/rag-prompt")

    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vector.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

# Initialize chain once to avoid reloading on every request
qa_chain = initialize_qa_chain()

def handle_retrieval_query(query: str) -> str:
    """Handle the query using RetrievalQA chain."""
    try:
        result = qa_chain({"query": query})
        return result["result"]
    except Exception as e:
        raise RuntimeError(f"Error in retrieval query: {str(e)}")

def handle_direct_openai_query(query: str) -> str:
    """Directly query OpenAI API for non-contextual responses."""
    client = OpenAI()
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are an AI simulation acting as an interviewer. Conduct the interview entirely in Spanish, asking professional questions "
                    "related to job qualifications, experience, skills, and behavioral competencies. Interpret the user's responses "
                    "accurately and adapt your follow-up questions to simulate a realistic interview flow. Respond in clear, concise, and polite Spanish. "
                    "Avoid responding to non-interview related topics or offering personal opinions, and remain strictly professional. "
                    "For simple greetings or unclear responses from the user, respond briefly and neutrally to guide the conversation back to interview questions. "
                    "If the user's input is unrelated or confusing, respond only with 'invalidQuery'."
                )},
                {"role": "user", "content": query},
            ]
        )
        response = completion.choices[0].message.content.strip()
        return response if response else "Respuesta no válida del modelo"
    except Exception as e:
        raise RuntimeError(f"Error in OpenAI direct query: {str(e)}")


