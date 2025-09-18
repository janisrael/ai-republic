# AI Refinement Dashboard - Setup Instructions

## 🚀 Quick Start

This AI Refinement Dashboard is a complete platform for training, managing, and evaluating AI models with a beautiful neumorphic UI.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Ollama** (for local AI models)
- **Git** (for version control)

### System Requirements
- **RAM**: 8GB+ (16GB recommended for training)
- **Storage**: 20GB+ free space
- **GPU**: Optional but recommended for faster training

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-refinement-dashboard
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional AI dependencies
pip install chromadb sentence-transformers transformers torch peft datasets accelerate bitsandbytes
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

### 4. ChromaDB Setup
```bash
# ChromaDB is automatically installed with pip install chromadb
# It will create a local database in backend/chromadb_data/

# Test ChromaDB installation
cd backend
python3 -c "import chromadb; print('✅ ChromaDB installed successfully')"
```

### 5. Ollama Setup
```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull base models (in another terminal)
ollama pull llama3.1:8b
ollama pull codellama:13b
ollama pull qwen2.5-coder:7b
```

## 🚀 Running the Application

### Option 1: Using the Service Script (Recommended)
```bash
# Start all services
./start_services.sh start

# Stop all services
./start_services.sh stop

# Check status
./start_services.sh status
```

### Option 2: Manual Start
```bash
# Terminal 1: Backend
cd backend
python3 api_server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 📊 Features Overview

### 🏠 Dashboard
- Real-time statistics
- Training progress monitoring
- Model performance overview

### 🤖 Models
- View all local Ollama models
- Model capabilities and tags
- Real-time model information

### 📚 Datasets
- Load datasets from Hugging Face
- Upload custom JSONL files
- Dataset preview and management

### 🏋️ Training
- **RAG Training**: Fast knowledge base setup with ChromaDB (2-5 minutes)
  - Creates vector embeddings from your datasets
  - Enables semantic search and retrieval
  - Perfect for Q&A and knowledge-based tasks
- **LoRA Training**: Real fine-tuning with Hugging Face integration (20-30+ minutes)
  - Efficient parameter fine-tuning
  - Supports multiple base models
  - Real-time progress tracking with step counters
- Multi-dataset training support
- Real-time progress tracking via Socket.IO

### 📈 Evaluation
- Training job results
- Before/after comparisons
- Performance metrics
- Model evaluation history

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
# Database
DATABASE_PATH=./ai_dashboard.db

# ChromaDB
CHROMADB_PATH=./chromadb_data
CHROMADB_BATCH_SIZE=512
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Ollama
OLLAMA_HOST=http://localhost:11434

# Training
MAX_TRAINING_TIME=3600
DEFAULT_BATCH_SIZE=4
DEFAULT_LEARNING_RATE=0.0002
LORA_RANK=8
LORA_ALPHA=32
LORA_DROPOUT=0.05
```

### Model Configuration
Models are stored in the `models/` directory with Modelfile configurations.

## 🎯 Usage Examples

### 1. Load a Dataset
1. Go to **Datasets** page
2. Click **"🤗 Load from Hugging Face"**
3. Enter dataset ID (e.g., `sahil2801/CodeAlpaca-20k`)
4. Click **Load Dataset**

### 2. Start Training

#### RAG Training (Fast - 2-5 minutes)
1. Go to **Training** page
2. Click **"Start Training"**
3. Fill in the training modal:
   - **Name**: "My RAG Assistant"
   - **Base Model**: "llama3.1:8b"
   - **Training Type**: "RAG"
   - **Select Datasets**: Choose your datasets
   - **Description**: "AI assistant with knowledge base"
4. Click **"Start Training"**
   - Creates ChromaDB knowledge base
   - Generates vector embeddings
   - Creates Ollama model with RAG capabilities

#### LoRA Training (Real Fine-tuning - 20-30+ minutes)
1. Go to **Training** page
2. Click **"Start Training"**
3. Fill in the training modal:
   - **Name**: "My Fine-tuned Model"
   - **Base Model**: "llama3.1:8b"
   - **Training Type**: "LoRA"
   - **Select Datasets**: Choose your datasets
   - **LoRA Config**: Adjust rank, alpha, dropout
   - **Training Params**: Set epochs, batch size, learning rate
4. Click **"Start Training"**
   - Downloads Hugging Face model
   - Performs real fine-tuning
   - Creates Ollama model with LoRA weights

### 3. View Results
1. Go to **Models** page to see created models
2. Go to **Evaluation** page to see training results
3. Use `ollama run <model-name>` to test your model

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if port 5000 is available
lsof -i :5000

# Kill existing processes
pkill -f "python3 api_server.py"
```

#### Frontend Won't Start
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Ollama Connection Issues
```bash
# Check Ollama status
ollama list

# Restart Ollama
pkill ollama
ollama serve
```

#### Training Fails
- Check available disk space (need 5GB+ for training)
- Ensure Ollama is running
- Check ChromaDB installation: `python3 -c "import chromadb"`
- Check backend logs: `tail -f backend/api_server.log`
- For LoRA training: Ensure Hugging Face models are accessible
- For RAG training: Check ChromaDB data directory permissions

### Logs Location
- **Backend**: `backend/api_server.log`
- **Frontend**: `frontend/frontend.log`

## 📁 Project Structure

```
ai-refinement-dashboard/
├── backend/
│   ├── api_server.py          # Main API server with Socket.IO
│   ├── database.py            # SQLite database
│   ├── training_executor.py   # Training logic (RAG + LoRA)
│   ├── chromadb_service.py    # ChromaDB integration
│   ├── dataset_loader.py      # Dataset loading
│   ├── chromadb_data/         # ChromaDB vector database
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── views/             # Vue.js pages
│   │   ├── components/        # Reusable components
│   │   └── assets/           # CSS and assets
│   └── package.json          # Node.js dependencies
├── models/                   # Generated Ollama models
├── training_data/           # LoRA training datasets
├── start_services.sh        # Service management script
└── SETUP.md                # This file
```

## 🧠 ChromaDB Features

### What is ChromaDB?
ChromaDB is a vector database that enables semantic search and retrieval-augmented generation (RAG). It stores your training data as vector embeddings, allowing AI models to find relevant information quickly.

### RAG Training Process
1. **Data Ingestion**: Your datasets are converted into vector embeddings
2. **Storage**: Embeddings are stored in ChromaDB collections
3. **Retrieval**: When you ask questions, relevant data is retrieved
4. **Generation**: The AI model uses retrieved data to provide accurate answers

### ChromaDB Collections
- Each training job creates a unique collection: `knowledge_base_job_{id}`
- Collections contain vector embeddings of your dataset samples
- Supports semantic search across all your training data
- Automatic batching for efficient processing

### Benefits of RAG
- **Fast Setup**: 2-5 minutes vs 20-30+ minutes for LoRA
- **Knowledge Retention**: Models can access your specific data
- **Flexible**: Easy to update knowledge base with new data
- **Efficient**: Only relevant information is retrieved per query

## 🔒 Security Notes

- The application runs locally by default
- No external API keys required for basic functionality
- ChromaDB data is stored locally in `backend/chromadb_data/`
- Training data remains on your machine
- Vector embeddings are generated locally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository

---

**Happy Training! 🚀**
