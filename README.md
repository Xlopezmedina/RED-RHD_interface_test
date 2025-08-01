# RED-RHD Clinical Interface

A modern web application for managing heart sound recordings, AI predictions, and clinical data analysis.

## Project Structure

```
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── App.js          # Main application component
│   │   ├── App.css         # Application styles
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
│
├── backend/                 # Flask backend API
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── __init__.py
│
└── README.md               # This file
```

## Features

- **Modern UI/UX**: Clean, responsive design with professional medical interface
- **Audio Waveform Visualization**: Interactive waveforms for heart sound recordings
- **File Management**: Organized sections for recordings, predictions, embeddings, and metadata
- **Clinical Notes**: Add and save clinical observations for each file
- **Real-time Audio Playback**: Play/pause controls with time tracking
- **Azure Blob Storage Integration**: Secure cloud storage for medical data
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- Azure Storage Account with SAS token

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Azure credentials:
   ```
   AZURE_CONTAINER_URL=your_container_url
   AZURE_SAS_TOKEN=your_sas_token
   ```

4. Start the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

## API Endpoints

- `GET /api/blobs` - List all files in Azure storage
- `GET /api/audio/<filename>` - Stream audio files
- `POST /api/comments` - Save clinical comments

## Technologies Used

### Frontend
- React 18
- WaveSurfer.js for audio visualization
- Lucide React for icons
- Axios for API calls
- CSS3 with modern features

### Backend
- Flask
- Azure Storage SDK
- Flask-CORS for cross-origin requests
- Python-dotenv for environment management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.