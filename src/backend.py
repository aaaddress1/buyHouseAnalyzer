from flask import Flask, render_template
from flask import request
import analyzer, json
app = Flask(__name__)


@app.route('/')
def hello_world():

    houseAddr = request.args.get('houseAddr')
    district = request.args.get('district')
    which_floor = request.args.get('which_floor')
    city = request.args.get('city')
    if not city or len(city) < 1: city = '臺北市'
    user_input_record = {'houseAddr':houseAddr, 'district':district, 'city':city, 'which_floor': which_floor}

    city_symbol = analyzer.country_map[city.replace('台', '臺')]
    if houseAddr or district:
        _, __ = analyzer.fetchHouseInfo(city_symbol, houseAddr, district, which_floor)
        return render_template('index.html', labels=_, content=(__), dbInitVal = user_input_record)
    else:
        return render_template('index.html', labels=[], content={}, dbInitVal = user_input_record)

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.run('127.0.0.1', 21247, debug=True)