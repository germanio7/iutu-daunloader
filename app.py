from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import uuid
import glob
import subprocess
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='public', static_url_path='/static')

def find_ffmpeg():
    """Encuentra la ubicación de FFmpeg en el sistema"""
    # Verificar ubicación conocida primero
    if os.path.isfile('/usr/bin/ffmpeg'):
        return '/usr/bin/ffmpeg'
    
    # Intentar con which
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def convert_to_mp3(input_file, output_file):
    try:
        cmd = [
            '/usr/bin/ffmpeg', '-i', input_file,
            '-vn', '-acodec', 'libmp3lame', '-ab', '192k',
            output_file
        ]
        subprocess.run(cmd, check=True)
        os.remove(input_file)
    except Exception as e:
        raise Exception(f'Error al convertir a MP3: {str(e)}')

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
            'outtmpl': f'{output_path}/{download_id}_%(title)s.%(ext)s',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
        
        # Buscar archivo descargado
        downloaded_files = glob.glob(f'{output_path}/{download_id}_*')
        if downloaded_files:
            input_file = downloaded_files[0]
            output_file = input_file.rsplit('.', 1)[0] + '.mp3'
            
            # Convertir a MP3
            convert_to_mp3(input_file, output_file)
            
            return jsonify({
                'success': True,
                'filename': os.path.basename(output_file),
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
            response = send_file(file_path, as_attachment=True)
            # Programar eliminación del archivo después de enviarlo
            import threading
            def delete_file():
                import time
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