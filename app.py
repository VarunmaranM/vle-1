from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Using an environment variable to show updates
    version = os.environ.get('APP_VERSION', "v1.0")
    return f'Hello from Kubernetes! App Version: {version}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)