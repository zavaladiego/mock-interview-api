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

class InterviewSession:
    def __init__(self, max_questions: int = 5, max_history_length: int = 5):
        self.conversation_history = []
        self.question_counter = 0
        self.max_questions = max_questions
        self.max_history_length = max_history_length

    def handle_direct_openai_query(self, query: str) -> str:
        """Directly query OpenAI API for non-contextual responses."""
        client = OpenAI()
        try:
            # Append the new user message to the conversation history
            self.conversation_history.append({"role": "user", "content": query})
            
            # Limit the conversation history to the most recent messages
            limited_history = self.conversation_history[-self.max_history_length:]
            
            # Determine the system message based on the question counter
            if self.question_counter == self.max_questions - 1:
                system_message = (
                    "This is the last question of the interview. "
                    "Thank you for your time. "
                    "If you have any additional questions, please ask them now."
                )
            else:
                system_message = (
                    "You are an AI simulation acting as a professional interviewer conducting a structured interview in Spanish. "
                    "Your goal is to ask clear and concise questions related to job qualifications, experience, skills, and behavioral competencies. "
                    "Ensure that the conversation covers a broad range of topics relevant to the role and does not overly focus on a single aspect. "
                    "When the user responds to a question, follow up only once for clarification if needed, and then move on to a different question. "
                    "If the user's response is inappropriate, contains offensive language, or is unrelated to the interview, respond with "
                    "'Su respuesta no es apropiada para esta entrevista. Por favor, mantenga un tono profesional.' "
                    "If the response is unclear or confusing, respond with 'No entendí su respuesta. ¿Podría aclararlo?' and then proceed with the next topic. "
                    "Avoid offering opinions, non-interview-related discussions, or personal comments. Keep the interaction strictly professional and polite. "
                    "After each user response, ask a new question related to job qualifications, experience, skills, or behavioral competencies."
                )
            
            # Check if the interview should end
            if self.question_counter > self.max_questions:
                return "La entrevista ha concluido. Gracias por su tiempo."
            
            # Include the limited conversation history in the request
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    *limited_history,
                ]
            )

            # Increment the question counter
            self.question_counter += 1
            
            # Append the assistant's response to the conversation history
            response = completion.choices[0].message.content.strip()
            self.conversation_history.append({"role": "assistant", "content": response})
                    
            return response if response else "Respuesta no válida del modelo"
        except Exception as e:
            raise RuntimeError(f"Error in OpenAI direct query: {str(e)}")
