from flask import Flask, render_template, request, send_file, jsonify
import json
import io
import os
from util import inject_templates

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        # 1. Parse Form Data
        job_name = request.form.get('job_name', 'af3_job')
        raw_seeds = request.form.get('seeds', '1')
        seeds = [int(s.strip()) for s in raw_seeds.split(',') if s.strip().isdigit()]
        
        if not seeds:
            return jsonify({"error": "At least one valid seed is required."}), 400

        # Sequences are passed as a JSON string from the frontend
        sequences_json = request.form.get('sequences')
        if not sequences_json:
             return jsonify({"error": "No sequences provided."}), 400
        
        sequences = json.loads(sequences_json)

        # 2. Build Base JSON
        input_json = {
            "name": job_name,
            "modelSeeds": seeds,
            "sequences": sequences,
            "dialect": "alphafold3",
            "version": 1
        }

        # 3. Handle Template Injection (if CIF provided)
        cif_files = request.files.getlist('cif_file')
        logs = []
        
        if cif_files:
            for cif_file in cif_files:
                if cif_file and cif_file.filename != '':
                    # Read content as string
                    cif_content = cif_file.read().decode('utf-8')
                    file_logs = inject_templates(input_json, cif_content)
                    logs.extend(file_logs)
        
        # 4. Prepare Response
        # If user wants download
        output_buffer = io.BytesIO()
        output_buffer.write(json.dumps(input_json, indent=2).encode('utf-8'))
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=f"{job_name}.json",
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=19999)
