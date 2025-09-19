# AI Refinement Dashboard

A comprehensive dashboard for training, evaluating, and managing AI models with LoRA fine-tuning and RAG (Retrieval-Augmented Generation) capabilities.

## Features

- 🚀 **LoRA Fine-tuning**: Efficiently fine-tune large language models
- 📚 **RAG Training**: Create knowledge bases with ChromaDB integration
- 📊 **Model Evaluation**: Comprehensive evaluation metrics and comparisons
- 🎯 **Dataset Management**: Import and manage datasets from Hugging Face
- 🤖 **AI Room**: Multi-agent conversation simulation
- 📈 **Real-time Monitoring**: Live training progress and status updates
- 🖼️ **Model Profiles**: Avatar uploads and model customization

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Ollama** (for model inference)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-refinement-dashboard
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

   This will automatically:
   - Check system requirements
   - Create Python virtual environment
   - Install all dependencies
   - Setup database with migrations
   - Create environment configuration

3. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ```

4. **Start the application**
   ```bash
   ./start_services.sh
   ```

5. **Access the dashboard**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/api/health

## Manual Setup

If you prefer manual setup:

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
cd backend
python3 setup_db.py --action setup
cd ..
```

### Frontend Setup

```bash
cd frontend
npm install
cd ..
```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and modify as needed:

```bash
cp env.example .env
```

Key configuration options:
- `DATABASE_PATH`: Database file location
- `BACKEND_PORT`: Backend server port (default: 5000)
- `FRONTEND_PORT`: Frontend server port (default: 5173)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)
- `DEFAULT_MAX_SAMPLES`: Maximum samples for dataset loading (default: 1000)

## Database Management

### Migrations

The database uses a migration system for schema updates:

```bash
# Run all pending migrations
python3 backend/setup_db.py --action migrate

# Check database status
python3 backend/setup_db.py --action status

# Create backup
python3 backend/setup_db.py --action backup

# Reset database (WARNING: Deletes all data!)
python3 backend/setup_db.py --action reset
```

### Schema Version

The database tracks schema versions automatically. Current schema includes:
- `training_jobs`: Training job management
- `datasets`: Dataset storage and metadata
- `evaluations`: Model evaluation results
- `model_profiles`: Model avatars and profiles

## Service Management

### Start Services

```bash
# Start all services
./start_services.sh

# Start with specific options
./start_services.sh --backend-only
./start_services.sh --frontend-only
```

### Stop Services

```bash
# Stop all services
./start_services.sh stop

# Restart services
./start_services.sh restart
```

## Usage

### Training Models

1. **Import Datasets**: Go to `/datasets` page to import from Hugging Face or upload local files
2. **Create Training Job**: Go to `/training` page to configure LoRA or RAG training
3. **Monitor Progress**: Real-time updates on training status and progress
4. **View Results**: Check `/models` page for trained models

### Model Evaluation

1. **Automatic Evaluation**: Evaluations are created automatically after training
2. **Manual Evaluation**: Create custom evaluations on `/evaluation` page
3. **Compare Models**: Use `/model-comparison` page for side-by-side comparisons

### AI Room

1. **Select Models**: Choose AI models for conversation
2. **Configure Settings**: Set conversation parameters (temperature, delay, etc.)
3. **Start Conversation**: Watch AI agents interact automatically
4. **Export Results**: Save conversation logs

## API Endpoints

### Core Endpoints

- `GET /api/health` - Health check
- `GET /api/models` - List Ollama models
- `GET /api/datasets` - List datasets
- `GET /api/training-jobs` - List training jobs
- `GET /api/evaluations` - List evaluations

### Training Endpoints

- `POST /api/training-jobs` - Create training job
- `POST /api/start-training` - Start training
- `PUT /api/training-jobs/<id>` - Update training job
- `DELETE /api/training-jobs/<id>` - Delete training job

### Dataset Endpoints

- `POST /api/load-dataset` - Load dataset from Hugging Face
- `DELETE /api/datasets/<id>` - Delete dataset
- `POST /api/datasets/<id>/favorite` - Toggle favorite

### Model Endpoints

- `PUT /api/models/<name>` - Update model (system prompt, etc.)
- `POST /api/models/<name>/avatar` - Upload model avatar
- `GET /api/avatars/<filename>` - Serve avatar images

## Development

### Project Structure

```
ai-refinement-dashboard/
├── backend/                 # Python backend
│   ├── api_server.py       # Main Flask application
│   ├── database.py         # Database operations
│   ├── setup_db.py         # Database migrations
│   ├── training_executor.py # LoRA training
│   ├── rag_training_executor.py # RAG training
│   ├── evaluation_executor.py # Model evaluation
│   ├── dataset_loader.py   # Dataset processing
│   ├── chromadb_service.py # ChromaDB integration
│   └── migrations/         # Database migrations
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── views/         # Page components
│   │   ├── components/    # Reusable components
│   │   └── router/        # Vue Router
│   └── package.json
├── setup.sh               # Setup script
├── start_services.sh      # Service management
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
└── README.md
```

### Adding New Features

1. **Backend**: Add new endpoints in `api_server.py`
2. **Frontend**: Create new components in `frontend/src/`
3. **Database**: Create migrations in `backend/setup_db.py`
4. **Testing**: Add tests in `tests/` directory

### Database Migrations

When adding new database features:

1. Add migration to `setup_db.py`
2. Increment version number
3. Test migration with `python3 backend/setup_db.py --action migrate`

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :5000
   lsof -i :5173
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Database Issues**
   ```bash
   # Check database status
   python3 backend/setup_db.py --action status
   
   # Reset database
   python3 backend/setup_db.py --action reset
   ```

3. **Ollama Connection Issues**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama
   ollama serve
   ```

4. **Python Dependencies**
   ```bash
   # Reinstall dependencies
   source venv/bin/activate
   pip install -r requirements.txt --force-reinstall
   ```

5. **Node.js Dependencies**
   ```bash
   # Clear and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Logs

- Backend logs: `backend/api_server.log`
- Frontend logs: `frontend/frontend.log`
- Service logs: Check terminal output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Happy Training! 🚀**