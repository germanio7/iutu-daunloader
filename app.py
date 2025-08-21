from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import uuid
import glob
import subprocess
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def find_ffmpeg():
    """Encuentra la ubicación de FFmpeg en el sistema"""
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Ubicaciones comunes
    common_paths = ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', 'ffmpeg']
    for path in common_paths:
        try:
            subprocess.run([path, '-version'], capture_output=True, check=True)
            return path
        except:
            continue
    return None

def convert_to_mp3(input_file, output_file):
    try:
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-acodec', 'libmp3lame', '-ab', '192k',
            output_file
        ]
        subprocess.run(cmd, check=True)
        os.remove(input_file)
    except FileNotFoundError:
        # Si FFmpeg no está disponible, usar yt-dlp para conversión
        raise Exception('FFmpeg no disponible')

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
        
        ffmpeg_path = find_ffmpeg()
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{output_path}/{download_id}_%(title)s',
            'noplaylist': True,
        }
        
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
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
            return send_file(file_path, as_attachment=True)
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