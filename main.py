from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from motor.motor_asyncio import AsyncIOMotorClient
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
from contextlib import asynccontextmanager
import re

# Initialize FastAPI app
app = FastAPI(title="RAG Document Query API")

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# MongoDB setup
MONGODB_URL = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["rag_database"]
documents_collection = db["documents"]

# Initialize Cohere Embeddings
co_embedder = CohereEmbeddings(
    model="embed-v4.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

# Initialize Google Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

# Define Pydantic models
class QueryRequest(BaseModel):
    document_id: str
    query: str

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    cloudinary_url: str
    upload_date: str

# Prompt template for RAG
prompt = ChatPromptTemplate.from_template("""
You are an AI assistant tasked with answering questions based on the provided context.
Carefully read the context and use only the information within it to answer the question.
If the answer cannot be found in the context, state that clearly and do not make up information.
<context>
{context}
</context>

Question: {input}
""")

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure MongoDB indexes
    await documents_collection.create_index("document_id", unique=True)
    print("Connected to MongoDB")
    yield
    # Shutdown: Close MongoDB connection
    client.close()
    print("Disconnected from MongoDB")

# Assign lifespan handler to FastAPI app
app.lifespan = lifespan



@app.post("/upload-document/", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create temp directory in project root
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)

        # Sanitize filename to handle spaces and special characters
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{safe_filename}")

        # Log file creation
        print(f"Creating temporary file at: {temp_file_path}")

        # --- IMPORTANT CHANGE HERE ---
        # Read the file content directly from the UploadFile object and write it
        file_content = await file.read()
        
        # Check if the file_content is empty right after reading
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be read.")

        with open(temp_file_path, "wb") as f:
            f.write(file_content)

        # Verify file exists and has content after writing
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
            raise HTTPException(status_code=500, detail=f"Failed to create temporary file or it's empty after writing: {temp_file_path}")
        
        print(f"Temporary file created successfully, size: {os.path.getsize(temp_file_path)} bytes")

        # Upload to Cloudinary - use the temp file directly or the BytesIO from file_content
        # For Cloudinary, it's often better to pass a file-like object or bytes
        # Since you've read it into file_content, you can use that directly.
        # However, for robustness and avoiding reading into memory for huge files,
        # it's better to reset the file pointer if you read it from the original file handle.
        # But for now, let's use the temp file path directly, which is safer if the temp file is guaranteed to be good.
        upload_result = cloudinary.uploader.upload(
            temp_file_path, # Pass the path to the temporary file
            resource_type="raw",
            folder="rag_documents",
            public_id=f"doc_{uuid.uuid4().hex}"
        )

        # Process document for RAG
        print("Loading document with PyPDFium2Loader...")
        try:
            document = PyPDFium2Loader(temp_file_path).load()
        except Exception as e:
            # Catch specific error from PyPDFium2Loader for better diagnostics
            print(f"Error loading PDF with PyPDFium2Loader: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to load document (PDFium: {e})")

        docs = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0).split_documents(document)
        
        # Create and save vector store
        persistent_path = os.path.join("vector_stores", upload_result['public_id'])
        os.makedirs(os.path.dirname(persistent_path), exist_ok=True)
        print(f"Creating vector store at: {persistent_path}")
        vector_store = FAISS.from_documents(docs, co_embedder)
        vector_store.save_local(persistent_path)

        # Store document metadata in MongoDB
        document_id = str(uuid.uuid4())
        document_data = {
            "document_id": document_id,
            "filename": file.filename,
            "cloudinary_url": upload_result["secure_url"],
            "vector_store_path": persistent_path,
            "upload_date": upload_result["created_at"]
        }
        await documents_collection.insert_one(document_data)

        # Clean up temporary file
        print(f"Cleaning up temporary file: {temp_file_path}")
        os.remove(temp_file_path)

        return DocumentResponse(**document_data)

    except HTTPException as he:
        # Re-raise HTTPExceptions directly
        raise he
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in upload_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/query-document/")
async def query_document(request: QueryRequest):
    try:
        # Fetch document metadata from MongoDB
        document = await documents_collection.find_one({"document_id": request.document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Load vector store
        vector_store = FAISS.load_local(
            document["vector_store_path"],
            co_embedder,
            allow_dangerous_deserialization=True
        )
        
        # Set up RAG chain
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        document_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, document_chain)

        # Process query
        response = await rag_chain.ainvoke({"input": request.query})
        
        return {
            "document_id": request.document_id,
            "query": request.query,
            "answer": response["answer"],
            "context": [doc.page_content for doc in response["context"]]
        }

    except Exception as e:
        print(f"Error in query_document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/documents/", response_model=List[DocumentResponse])
async def list_documents():
    try:
        documents = await documents_collection.find().to_list(length=100)
        return [DocumentResponse(**doc) for doc in documents]
    except Exception as e:
        print(f"Error in list_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
