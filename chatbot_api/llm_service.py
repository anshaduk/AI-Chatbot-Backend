import ollama
import uuid
from langchain.llms import ollama
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from django.conf import settings
from . models import Conversation,Message,KnowledgeDocument


# PostgreSQL connection string
CONNECTION_STRING = f"postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}"


class ChatbotService:
    def __init__(self):
        ##Initialize LLM##
        self.llm = ollama(model="llama3.2")

        ##Initialize embeddings##
        self.embeddings = OllamaEmbeddings(model="llma3.2")


        ##Initialize vector store##
        try:
            self.vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=self.embeddings,
                collection_name="document_embeddings"
            )
        except Exception as e:
            print(f"vector store initialization error: {e}")
            self.vector_store = None


    def get_conversation(self,conversation_id=None):
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Conversation.objects.create()
        else:
            return Conversation.objects.create()
        

    def save_message(self,conversation,content,is_user=True):
        return Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=is_user
        )
    

    def get_conversation_history(self,conversation):
        messages = conversation.messages.all().order_by('timestamp')
        history = []

        for msg in messages:
            role = "user" if msg.is_user else "assistant"
            history.append({"role":role,"content":msg.content})

        return history
    

    def generate_rag_response(self,user_message,conversation):
        """Generate response using RAG capabilities"""
        if not self.vector_store:
            return self.generate_direct_response(user_message,conversation)
        
        try:
            history = self.get_conversation_history(conversation)
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )


            for msg in history:
                if msg["role"] == "user":
                    memory.chat_memory.add_user_message(msg["content"])
                else:
                    memory.chat_memory.add_ai_message(msg["content"])

            ##Create RAG chain##
            qa_chain = ConversationalRetrievalChain.form_llm(
                llm=self.llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k":3}),
                memory=memory,
                verbose=True
            )

            response = qa_chain({"question":user_message})
            return response["answer"]
        except Exception as e:
            print(f"RAG response error: {e}")
            return self.generate_direct_response(user_message,conversation)
        
    
    def generate_direct_response(self,user_message,conversation):
        """Generate direct response from LLM without RAG"""
        system_prompt = """You are a helpful, friendly AI assistant for a company.
        Answer the user's questions to the best of your ability.
        If you don't know something, admit it rather than making up information."""


        history = self.get_conversation_history(conversation)

        messages = [{"role":"system","content":system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role":"user","content":user_message})


        response = ollama.chat(model="llama3.2",messages=messages)
        return response["message"]["content"]
    
    
    def process_chat(self,user_message,conversation_id=None):
        conversation = self.get_conversation(conversation_id)

        self.save_message(conversation,user_message,is_user=True)

        # Generate response using RAG if available
        bot_response = self.generate_rag_response(user_message,conversation)

        self.save_message(conversation,bot_response,is_user=False)

        return {
            "conversation_id": conversation_id,
            "response": bot_response
        }
    
    def add_document(self,title,content):
         """Add document to knowledge base and generate embeddings"""
         document = KnowledgeDocument.objects.create(
             title=title,
             content=content
         )

         if self.vector_store:
             try:
                 self.vector_store.add_texts(
                     texts=[content],
                     metadatas=[{"title":title,"document_id":str(document.id)}]
                 )

                 document.embedding_stored = True
                 document.save()

                 return True
             except Exception as e:
                 print(f"Error adding document to vector store: {e}")
                 return False
             
         return False
    
    



