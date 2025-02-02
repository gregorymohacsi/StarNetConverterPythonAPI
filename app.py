# Update app.py to add root route
from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
import os
import traceback
import logging
from starnet_converter import converter
from starnet_cleanup import clean_output
import tempfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "https://starnetconverterpythonapi.onrender.com"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/process-file', methods=['POST'])
def process_file():
    logger.info('Received file processing request')
    
    if 'file' not in request.files:
        logger.error('No file part in request')
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error('No selected file')
        return 'No selected file', 400
    
    logger.info(f'Processing file: {file.filename}')
    
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='_input.rpt') as input_file:
            input_path = input_file.name
            file.save(input_path)
            logger.info(f'Saved input file to {input_path}')
            
            # Create temporary filenames for outputs
            converter_output = input_path + '_converted'
            final_output = converter_output + '_cleaned'
            
            # Process the file
            logger.info('Starting conversion')
            converter(input_path, converter_output)
            logger.info('Conversion complete')
            
            logger.info('Starting cleanup')
            clean_output(converter_output, final_output)
            logger.info('Cleanup complete')
            
            # Verify file exists and has content
            if not os.path.exists(final_output):
                raise FileNotFoundError(f'Final output file not found: {final_output}')
                
            file_size = os.path.getsize(final_output)
            logger.info(f'Output file size: {file_size} bytes')
            
            if file_size == 0:
                raise ValueError('Output file is empty')
            
            # Read file content for logging
            with open(final_output, 'r') as f:
                content_preview = f.read(100)
                logger.info(f'Output file preview: {content_preview[:50]}...')
            
            # Send the file
            logger.info('Sending file back to client')
            return send_file(
                final_output,
                as_attachment=True,
                download_name=os.path.basename(file.filename).replace('.rpt', '_processed.txt')
            )
            
    except Exception as e:
        logger.error('Error during processing:')
        logger.error(traceback.format_exc())
        return f'Error processing file: {str(e)}', 500
        
    finally:
        # Clean up temporary files
        for path in [input_path, converter_output, final_output]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    logger.info(f'Cleaned up temporary file: {path}')
                except Exception as e:
                    logger.error(f'Error cleaning up {path}: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True, port=5000)