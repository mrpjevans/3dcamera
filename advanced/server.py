from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def create_image():
    return 'Hello, World!'
