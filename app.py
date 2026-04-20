from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import yt_dlp
import os

app = Flask(__name__)

# Certifique-se de que o diretório de downloads existe
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    download_type = data.get('type', 'video') # Padrão para vídeo se não for especificado

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Opções base para yt-dlp
        ydl_opts_base = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',
            'remote_components': 'ejs:github',
            'compat_opts': {'remote-components': 'ejs:github'}
        }

        if download_type == 'audio':
            ydl_opts = ydl_opts_base.copy()
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts = ydl_opts_base.copy()
            ydl_opts.update({
                'format': 'bestvideo*+bestaudio/best',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            
            # Para downloads de áudio, o nome do arquivo pode mudar de .webm/.m4a para .mp3
            if download_type == 'audio':
                base, _ = os.path.splitext(file_name)
                file_name = base + '.mp3'

        return jsonify({'message': f'Download de "{os.path.basename(file_name)}" concluído!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
