from flask import Flask, request, send_file
from flask_cors import CORS
import os
import logging
from starnet_converter import converter
from starnet_cleanup import clean_output
import tempfile
import traceback

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = app.logger

    @app.route('/process-file', methods=['POST'])
    def process_file():
        logger.debug('Process file endpoint called')
        if 'file' not in request.files:
            logger.error('No file part in request')
            return 'No file part', 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error('No selected file')
            return 'No selected file', 400
        
        logger.debug(f'Processing file: {file.filename}')
        input_file = None
        converter_output = None
        final_output = None

        try:
            # Create temporary files for processing
            input_file = tempfile.NamedTemporaryFile(delete=False, suffix='_input.rpt')
            input_file_path = input_file.name
            logger.debug(f'Created temporary input file: {input_file_path}')
            
            # Save uploaded file
            file.save(input_file_path)
            logger.debug('File saved successfully')
            
            # Create temporary filenames for the outputs
            converter_output = input_file_path + '_converted'
            final_output = converter_output + '_cleaned'
            logger.debug(f'Output paths: converter={converter_output}, final={final_output}')
            
            # Process the file through conversion
            logger.debug('Starting conversion process')
            converter(input_file_path, converter_output)
            logger.debug('Conversion completed')
            
            # Process through cleanup
            logger.debug('Starting cleanup process')
            clean_output(converter_output, final_output)
            logger.debug('Cleanup completed')
            
            if not os.path.exists(final_output):
                raise FileNotFoundError(f'Final output file not created: {final_output}')
            
            logger.debug('Sending file back to client')
            return send_file(
                final_output,
                as_attachment=True,
                download_name=os.path.basename(file.filename).replace('.rpt', '_processed.txt')
            )
            
        except Exception as e:
            logger.error('Error during processing:')
            logger.error(traceback.format_exc())
            return f'Error processing file: {str(e)}\n{traceback.format_exc()}', 500
            
        finally:
            # Clean up temporary files
            logger.debug('Cleaning up temporary files')
            for temp_file in [input_file_path, converter_output, final_output]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                        logger.debug(f'Deleted temporary file: {temp_file}')
                    except Exception as e:
                        logger.error(f'Error deleting temporary file {temp_file}: {str(e)}')

    return app