# File Processing Web Application

This web application processes .rpt files using StarNet conversion and cleanup scripts.

## Project Structure
```
your_project_directory/
├── backend/
│   ├── app.py
│   ├── starnet_converter.py
│   └── starnet_cleanup.py
├── frontend/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── index.html
└── README.md
```

## Setup Instructions

1. Install required Python packages:
```bash
pip install flask flask-cors
```

2. Start the backend server:
```bash
cd backend
python app.py
```

3. Open the frontend/index.html file in a web browser

## Features
- File upload interface
- .rpt file validation
- Processing status indicators
- Automatic file download after processing
- Error handling and user feedback

## Technical Details
- Backend: Flask (Python)
- Frontend: HTML5, CSS3, JavaScript
- Cross-Origin Resource Sharing (CORS) enabled
- Temporary file handling for processing