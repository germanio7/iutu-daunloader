@echo off
docker run --rm -v "%cd%":/data jrottenberg/ffmpeg ffprobe %*