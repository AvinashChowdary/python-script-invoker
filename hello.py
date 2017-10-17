from flask import Flask, request, Response, make_response, send_file, send_from_directory, redirect
from flask_uploads import (UploadSet, SCRIPTS, configure_uploads)
import rocksdb
import time
import struct
import datetime
import subprocess
import sys
import os

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads/scripts')
app.config['UPLOADED_SCRIPTS_DEST'] = UPLOAD_FOLDER
scripts = UploadSet('scripts', SCRIPTS)
configure_uploads(app, scripts)

@app.route('/api/v1/scripts/<script_id>',methods=['GET'])
def run_script(script_id):
    rdb = rocksdb.DB("sample.db", rocksdb.Options(create_if_missing=True))
    key = script_id.encode(encoding='UTF-8',errors='strict')
    file_name = rdb.get(key)
    app.logger.error(file_name)
    cmd = 'python ./%s' %file_name
    app.logger.error(cmd)
    res = subprocess.check_output(cmd, shell = True, stderr=subprocess.STDOUT)
    return res

@app.route('/api/v1/scripts',methods=['POST'])
def upload():

    rdb = rocksdb.DB("sample.db", rocksdb.Options(create_if_missing=True))

    now = datetime.datetime.now()
    stamp = time.mktime(now.timetuple())
    binarydatetime = struct.pack('<L', stamp)
    bts = struct.unpack('<L', binarydatetime)[0]
    
    file = request.files['data']
    if os.path.isfile(UPLOAD_FOLDER+"/"+file.filename):
        app.logger.error('true')
        return Response('{"error":"Already file with name exits, please upload file with different name"}', status=409, mimetype='application/json')
    else:
        filename = scripts.save(request.files['data'])
        rdb.put(str(bts), str(filename))
        return Response('{"script-id":"%s"}' % str(bts), status=201, mimetype='application/json')

@app.route('/')
def hello():
    return 'Welcome'

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)
