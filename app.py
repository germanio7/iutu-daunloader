from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import uuid
import glob
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    try:
        output_path = os.getenv('DOWNLOAD_PATH', 'downloads')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        download_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{output_path}/{download_id}_%(title)s.%(ext)s',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
        
        # Buscar archivo descargado
        downloaded_files = glob.glob(f'{output_path}/{download_id}_*')
        if downloaded_files:
            return jsonify({
                'success': True,
                'filename': os.path.basename(downloaded_files[0]),
                'title': title
            })
        else:
            return jsonify({'error': 'No se pudo descargar el archivo'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        file_path = os.path.join('downloads', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    production = os.getenv('PRODUCTION', 'False').lower() == 'true'
    app_url = os.getenv('APP_URL', f'http://localhost:{port}')
    
    print(f'Aplicación ejecutándose en: {app_url}')
    
    if production:
        print('Modo producción: Usa "gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"')
    else:
        print('Modo desarrollo')
    
    app.run(debug=debug, port=port, host='0.0.0.0' if production else '127.0.0.1')