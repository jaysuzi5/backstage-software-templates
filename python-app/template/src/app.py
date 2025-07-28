from flask import Flask, jsonify
import datetime
import logging
import socket

app = Flask(__name__)

@app.route('/api/${{values.app_name}}/v1/info')
def info():
    logging.info('info called')
    return jsonify({
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d"),
        'hostname': socket.gethostname(),
        'message': 'Changed to info endpoint',
        'status': 'UP',
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}'
    })

@app.route('/api/${{values.app_name}}/v1/health')
def health():
    logging.info('health called')
    return jsonify({'status': 'UP'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

