from flask import Flask, render_template
from flask import request
import analyzer
app = Flask(__name__)


@app.route('/')
def hello_world():
    _, __ = analyzer.fetchHouseInfo('a', request.args.get('houseAddr'), request.args.get('country'))
    __ = sorted(__, key = lambda input_data: input_data[2])
    return render_template('index.html', labels=_, content=__)

if __name__ == '__main__':
    app.run('127.0.0.1', 21247)