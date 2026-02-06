from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/ejecutar-etl', methods=['GET'])
def run_etl():
    try:
        # RUTA ACTUALIZADA A SRC
        script_path = '/data/src/run_pipeline.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                "status": "error", 
                "message": f"Archivo no encontrado en: {script_path}"
            }), 404

        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                "status": "success", 
                "message": "ETL de Logística completada",
                "output": result.stdout
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "error_python": result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Servidor de ETL Logística activo en el puerto 5000...")
    app.run(host='0.0.0.0', port=5000)