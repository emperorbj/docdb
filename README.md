# BotyDoc 🤖📄

An intelligent RAG (Retrieval-Augmented Generation) chatbot that enables users to upload documents and have natural conversations with their content. Built with modern technologies for seamless document interaction.

## 🚀 Features

- **Document Upload**: Support for multiple document formats (PDF, TXT, DOCX, etc.)
- **Intelligent Chat**: Natural language conversations with your documents
- **RAG Architecture**: Combines retrieval and generation for accurate responses
- **Cross-Platform**: Built with React Native for iOS and Android
- **Real-time Processing**: Fast document analysis and response generation
- **User-friendly Interface**: Intuitive chat interface with document management
- **Context-Aware**: Maintains conversation context for better understanding

## 🛠️ Tech Stack

- **Frontend**: React Native
- **Backend**: FastAPI
- **AI Framework**: LangChain
- **LLM**: Google Gemini API
- **Database**: MongoDB
- **Architecture**: RAG (Retrieval-Augmented Generation)



## 🔧 Installation

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- MongoDB (v4.4 or higher)
- React Native development environment
- Google Gemini API key

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/emperorbj/botydoc.git
cd botydoc
```

2. Set up Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/botydoc
UPLOAD_FOLDER=./uploads
```

5. Start the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create `.env` file in the frontend directory:
```env
API_BASE_URL=http://localhost:8000
```

4. Start the React Native app:
```bash
# For iOS
npx react-native run-ios

# For Android
npx react-native run-android
```

## 🚀 Usage

1. **Launch the App**: Open BotyDoc on your mobile device
2. **Upload Document**: Tap the upload button and select your document
3. **Wait for Processing**: The app will analyze and index your document
4. **Start Chatting**: Ask questions about your document content
5. **Get Intelligent Responses**: Receive contextual answers based on your document

### Example Interactions

```
User: "What is the main topic of this document?"
BotyDoc: "Based on the document you uploaded, the main topic is..."

User: "Can you summarize the key points?"
BotyDoc: "Here are the key points from your document: 1. ... 2. ... 3. ..."

User: "Find information about [specific topic]"
BotyDoc: "I found the following information about [topic] in your document..."
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Native  │    │     FastAPI     │    │   Gemini API    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (LLM Model)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   LangChain     │
                       │   (RAG Logic)   │
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │    MongoDB      │
                       │  (Documents &   │
                       │   Embeddings)   │
                       └─────────────────┘
```

## 📡 API Endpoints

### Document Management
- `POST /upload` - Upload a document
- `GET /documents` - List all uploaded documents
- `DELETE /documents/{id}` - Delete a document

### Chat Interface
- `POST /chat` - Send a message and get AI response
- `GET /chat/history/{document_id}` - Get chat history for a document

### Health Check
- `GET /health` - Check API status

## 🔒 Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=mongodb://localhost:27017/botydoc
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=pdf,txt,docx,doc
```

### Frontend (.env)
```env
API_BASE_URL=http://localhost:8000
MAX_UPLOAD_SIZE=50000000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

## 📦 Build for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
# For Android
npx react-native run-android --variant=release

# For iOS
npx react-native run-ios --configuration Release
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- Large documents (>50MB) may take longer to process
- PDF parsing may vary depending on document structure
- Chat history is currently stored locally

## 🗺️ Roadmap

- [ ] Support for more document formats
- [ ] Cloud storage integration
- [ ] Multi-language support
- [ ] Voice chat functionality
- [ ] Document collaboration features
- [ ] Advanced search and filtering

## 👥 Authors

- **Opatola Bolaji** -  - [YourGitHub](https://github.com/emperorbj)

## 🙏 Acknowledgments

- Google Gemini API for powerful language processing
- LangChain for RAG implementation
- FastAPI for robust backend development
- React Native community for mobile development tools

---

⭐ If you found this project helpful, please give it a star on GitHub!
