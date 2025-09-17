# 🤖 AI Refinement Dashboard

A comprehensive platform for training, managing, and evaluating AI models with a beautiful neumorphic UI.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🏠 **Dashboard**
- Real-time training statistics
- Model performance overview
- Interactive charts and metrics

### 🤖 **Model Management**
- View all local Ollama models
- Model capabilities and tags
- Real-time model information
- Model deployment tracking

### 📚 **Dataset Management**
- Load datasets from Hugging Face
- Upload custom JSONL files
- Dataset preview and validation
- Multi-format support

### 🏋️ **Training System**
- **RAG Training**: Fast knowledge base setup (minutes)
- **LoRA Training**: Real fine-tuning (20-30+ minutes)
- Multi-dataset training support
- Real-time progress tracking
- ChromaDB integration for vector storage

### 📈 **Evaluation & Analytics**
- Training job results
- Before/after performance comparisons
- Detailed metrics (accuracy, precision, recall, F1)
- Model evaluation history
- Interactive charts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama
- 8GB+ RAM (16GB recommended)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ai-refinement-dashboard
```

2. **Setup backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Setup frontend**
```bash
cd ../frontend
npm install
```

4. **Install Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

5. **Start the application**
```bash
./start_services.sh start
```

6. **Access the dashboard**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 📖 Documentation

- **[Setup Instructions](SETUP.md)** - Detailed installation and configuration guide
- **[API Documentation](docs/API.md)** - Backend API reference
- **[User Guide](docs/USER_GUIDE.md)** - How to use the dashboard

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   Flask API     │    │   Ollama        │
│   Frontend      │◄──►│   Backend       │◄──►│   Models        │
│   (Port 5173)   │    │   (Port 5000)   │    │   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Neumorphic    │    │   SQLite        │    │   ChromaDB      │
│   UI Components │    │   Database      │    │   Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Use Cases

### **AI Researchers**
- Experiment with different training strategies
- Compare model performance across datasets
- Track training experiments and results

### **ML Engineers**
- Deploy and manage AI models
- Monitor model performance
- A/B test different model versions

### **Data Scientists**
- Load and explore datasets
- Train custom models for specific tasks
- Evaluate model performance

### **Developers**
- Integrate AI models into applications
- Create custom AI assistants
- Build RAG systems for knowledge retrieval

## 🔧 Configuration

### Environment Variables
```env
# Database
DATABASE_PATH=./ai_dashboard.db

# ChromaDB
CHROMADB_PATH=./chromadb_data

# Ollama
OLLAMA_HOST=http://localhost:11434

# Training
MAX_TRAINING_TIME=3600
DEFAULT_BATCH_SIZE=4
DEFAULT_LEARNING_RATE=0.0002
```

## 📊 Supported Models

### **Base Models**
- Llama 3.1 (8B, 70B)
- CodeLlama (7B, 13B, 34B)
- Qwen2.5-Coder (7B, 14B, 32B)
- Claude 3.7 Sonnet
- LLaVA (13B)

### **Training Types**
- **RAG Training**: Knowledge base setup with ChromaDB
- **LoRA Fine-tuning**: Parameter-efficient fine-tuning
- **Full Fine-tuning**: Complete model training

## 🛠️ Development

### Project Structure
```
ai-refinement-dashboard/
├── backend/                 # Python Flask API
│   ├── api_server.py       # Main API server
│   ├── database.py         # SQLite database
│   ├── training_executor.py # Training logic
│   ├── chromadb_service.py # ChromaDB integration
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vue.js frontend
│   ├── src/views/          # Page components
│   ├── src/components/     # Reusable components
│   └── package.json        # Node.js dependencies
├── models/                 # Generated models
├── chromadb_data/         # ChromaDB storage
└── start_services.sh      # Service management
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues
- **Backend won't start**: Check if port 5000 is available
- **Frontend won't start**: Clear node_modules and reinstall
- **Training fails**: Check disk space and Ollama status
- **Models not showing**: Verify Ollama is running

### Logs
- Backend: `backend/api_server.log`
- Frontend: `frontend/frontend.log`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 📧 Email: support@ai-refinement-dashboard.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local model serving
- [Hugging Face](https://huggingface.co/) for datasets and models
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Vue.js](https://vuejs.org/) for the frontend framework
- [Flask](https://flask.palletsprojects.com/) for the backend API

---

**Made with ❤️ for the AI community**
