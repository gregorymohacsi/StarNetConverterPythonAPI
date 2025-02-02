from flask import Flask, request, send_file
from flask_cors import CORS
import os
from starnet_converter import converter
from starnet_cleanup import clean_output
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/api/process-file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='_input.rpt') as input_file:
            file.save(input_file.name)
            
        # Create temporary filenames for the intermediate and final output
        converter_output = input_file.name + '_converted'
        final_output = converter_output + '_cleaned'
        
        # Process the file through both scripts
        converter(input_file.name, converter_output)  # First conversion
        clean_output(converter_output, final_output)  # Cleanup
        
        # Send the processed file back to the client
        return send_file(
            final_output,
            as_attachment=True,
            download_name=os.path.basename(file.filename).replace('.rpt', '_processed.txt')
        )
        
    except Exception as e:
        return f'Error processing file: {str(e)}', 500
        
    finally:
        # Clean up temporary files
        try:
            os.unlink(input_file.name)
            os.unlink(converter_output)
            os.unlink(final_output)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)