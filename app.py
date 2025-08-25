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

def sanitize_filename(filename):
    """Elimina caracteres especiales del nombre del archivo"""
    import re
    # Mantener solo letras, números, espacios, guiones y puntos
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    # Reemplazar múltiples espacios con uno solo
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()

def cleanup_old_files():
    """Elimina archivos más antiguos de 1 hora"""
    try:
        downloads_path = os.getenv('DOWNLOAD_PATH', 'downloads')
        if not os.path.exists(downloads_path):
            return
        
        current_time = time.time()
        for filename in os.listdir(downloads_path):
            file_path = os.path.join(downloads_path, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 7200:  # 2 horas en segundos
                    os.remove(file_path)
                    print(f'Archivo eliminado: {filename}')
    except Exception as e:
        print(f'Error en limpieza: {e}')

def start_cleanup_scheduler():
    """Inicia el programador de limpieza automática"""
    def cleanup_loop():
        while True:
            cleanup_old_files()
            time.sleep(1800)  # Ejecutar cada 30 minutos
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()

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
                'postprocessor_args': ['-af', 'silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB']
            }],
            'outtmpl': f'{output_path}/{download_id}_%(title)s',
            'noplaylist': True,
            'ffmpeg_location': '/usr/bin/ffmpeg',
            'restrictfilenames': True,
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
        
        # Si no hay MP3, buscar cualquier archivo generado
        all_files = glob.glob(f'{output_path}/{download_id}_*')
        if all_files:
            return jsonify({
                'success': True,
                'filename': os.path.basename(all_files[0]),
                'title': title
            })
        
        return jsonify({'error': 'No se pudo generar el archivo'}), 500
            
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
    # Iniciar limpieza automática
    start_cleanup_scheduler()
    
    port = int(os.getenv('PORT', 5000))
    app_url = f'http://localhost:{port}'
    
    print(f'Aplicación ejecutándose en: {app_url}')
    print('Modo desarrollo')
    print('Limpieza automática iniciada')
    
    app.run(debug=True, port=port, host='0.0.0.0')