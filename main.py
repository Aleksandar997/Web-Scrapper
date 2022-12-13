from flask import Flask, jsonify, request, send_from_directory, render_template, Response
from util import logger
import os
import codecs
from util.scrapper import writePage, scrape
import PyInstaller.__main__

app = Flask(__name__, static_url_path='/static')

exception_log_name = "exception.log"
info_log_name = "info.log"

logger.setup_logger("exception", exception_log_name, logger.ERROR)
logger.setup_logger("info", info_log_name, logger.INFO)

exception_logger = logger.getLogger('exception')
info_logger = logger.getLogger('info')

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response

@app.route('/exception_log', methods = ['GET'])
def get_exception_log():
    return __get_log_file(exception_log_name)

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_from_url():
    url = request.form['url']
    title, content = scrape(url)
    return Response(
        content.encode('utf-8'),
        mimetype="text/html",
        headers={'Content-disposition': f'attachment; filename={title}.html'}
    )

@app.route('/get_files', methods=['GET'])
def get_files():
    files = ''
    print(os.path.exists('sites'))
    if os.path.exists('sites'):
        files = ',<br>'.join(os.listdir('sites/'))
    return files

@app.route('/get_scrapper', methods=['GET'])
def get_scrapper():
    if not os.path.exists('dist/scrapper.exe'):
        PyInstaller.__main__.run([
            './util/scrapper.py',
            '--onefile',
            '--console'
        ])
    return send_from_directory(directory='dist', path='scrapper.exe')

@app.route('/save_scraped_content', methods=['POST'])
def save_scraped_content():
    content = request.json["content"]
    file_name = request.json["fileName"]
    is_success = writePage(file_name, content, exception_logger)
    status = ('success' if is_success else 'error')
    print(status)
    return jsonify({"status": status})

def __get_log_file(file_name: str):
    file_contents = ''
    if os.path.exists(file_name):
        with codecs.open(file_name, "r", encoding="utf-8") as f:
            file_contents = f.read()

    if (file_contents == None or file_contents.strip() == ''):
        file_contents = '{} file is empty'.format(file_name)
    file_contents = file_contents.replace('\n', '<br>')
    return file_contents

app.run(host='0.0.0.0', port=80, debug=False)
info_logger.info('App is running')
