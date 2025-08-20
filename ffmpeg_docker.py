#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    # Obtener directorio actual
    current_dir = os.getcwd()
    
    # Construir comando Docker
    docker_cmd = [
        'docker', 'run', '--rm',
        '-v', f'{current_dir}:/data',
        'jrottenberg/ffmpeg',
        'ffmpeg'
    ]
    
    # Agregar argumentos de FFmpeg, reemplazando rutas locales con /data
    for arg in sys.argv[1:]:
        if os.path.isabs(arg) and arg.startswith(current_dir):
            # Convertir ruta absoluta a ruta relativa en el contenedor
            rel_path = os.path.relpath(arg, current_dir)
            docker_cmd.append(f'/data/{rel_path}')
        else:
            docker_cmd.append(arg)
    
    # Ejecutar comando Docker
    result = subprocess.run(docker_cmd)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()