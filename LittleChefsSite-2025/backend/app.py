import os
from flask import Flask

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    return "Hello from Render!"

if __name__ == '__main__':
    app.run()