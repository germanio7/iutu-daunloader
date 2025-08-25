from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import uuid
import glob
import threading
import time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='public', static_url_path='/static')

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
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{output_path}/{download_id}_%(title)s',
            'noplaylist': True,
            'ffmpeg_location': '/usr/bin/ffmpeg',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
        
        # Buscar archivo MP3 generado
        mp3_files = glob.glob(f'{output_path}/{download_id}_*.mp3')
        if mp3_files:
            return jsonify({
                'success': True,
                'filename': os.path.basename(mp3_files[0]),
                'title': title
            })
        else:
            return jsonify({'error': 'No se pudo generar el archivo MP3'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        file_path = os.path.join('downloads', filename)
        if os.path.exists(file_path):
            response = send_file(file_path, as_attachment=True)
            # Programar eliminación del archivo después de enviarlo
            def delete_file():
                time.sleep(60)  # Esperar 60 segundos para asegurar que se envió
                try:
                    os.remove(file_path)
                except:
                    pass
            threading.Thread(target=delete_file).start()
            return response
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app_url = f'http://localhost:{port}'
    
    print(f'Aplicación ejecutándose en: {app_url}')
    print('Modo desarrollo')
    
    app.run(debug=True, port=port, host='0.0.0.0')