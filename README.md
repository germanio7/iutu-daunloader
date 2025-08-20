# Descargador de MP3 de YouTube

## Instalación

1. Instala las dependencias:
```bash
py -m pip install -r requirements.txt
```

2. Instala Docker:
   - Descarga desde: https://www.docker.com/get-started
   - Asegúrate de que Docker esté ejecutándose

3. Instala ffmpeg:
```bash 
docker pull linuxserver/ffmpeg
```

## Uso

### Interfaz Web (Recomendado)
```bash
py app.py
```
Abre http://localhost:5000 en tu navegador

### Producción (WSGI)
```bash
py -m pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Línea de comandos
```bash
py downloader.py
```

Los archivos MP3 se guardan en la carpeta `downloads/` en formato .mp3