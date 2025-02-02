from flask import Flask, request, send_file
from flask_cors import CORS
import os
import traceback
from starnet_converter import converter
from starnet_cleanup import clean_output
import tempfile

# Create the Flask application
app = Flask(__name__)
CORS(app)
app.debug = True  # Enable debug mode

@app.route('/process-file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    input_file_path = None
    converter_output = None
    final_output = None
    
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='_input.rpt') as input_file:
            input_file_path = input_file.name
            file.save(input_file_path)
            print(f"File saved to: {input_file_path}")  # Debug print
            
        # Create temporary filenames for the intermediate and final output
        converter_output = input_file_path + '_converted'
        final_output = converter_output + '_cleaned'
        print(f"Output paths: {converter_output}, {final_output}")  # Debug print
        
        # Process the file through both scripts
        print("Starting conversion...")  # Debug print
        converter(input_file_path, converter_output)  # First conversion
        print("Conversion complete")  # Debug print
        
        clean_output(converter_output, final_output)  # Cleanup
        print("Cleanup complete")  # Debug print
        
        if not os.path.exists(final_output):
            raise FileNotFoundError(f"Final output file not created at {final_output}")
        
        # Send the processed file back to the client
        return send_file(
            final_output,
            as_attachment=True,
            download_name=os.path.basename(file.filename).replace('.rpt', '_processed.txt')
        )
        
    except Exception as e:
        print("Error occurred:")  # Debug print
        print(traceback.format_exc())  # This will print the full error traceback
        return f'Error processing file: {str(e)}\n{traceback.format_exc()}', 500
        
    finally:
        # Clean up temporary files
        for filepath in [input_file_path, converter_output, final_output]:
            if filepath and os.path.exists(filepath):
                try:
                    os.unlink(filepath)
                    print(f"Cleaned up: {filepath}")  # Debug print
                except Exception as e:
                    print(f"Error cleaning up {filepath}: {str(e)}")  # Debug print

if __name__ == '__main__':
    app.run(debug=True, port=5000)