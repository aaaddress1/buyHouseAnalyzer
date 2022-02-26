from flask import Flask, render_template
from flask import request
import analyzer, json
app = Flask(__name__)


@app.route('/')
def hello_world():

    houseAddr = request.args.get('houseAddr')
    district = request.args.get('district')
    which_floor = int(request.args.get('which_floor')) if request.args.get('which_floor') else None
    landsize_Ibuy = float(request.args.get('landsize_Ibuy'))  if request.args.get('landsize_Ibuy') else None
    house_year = int(request.args.get('house_year')) if request.args.get('house_year') else None
    onlyHaveCarResult = request.args.get('onlyHaveCarResult')
    year_range = range(1, 200) # 民國一年～兩百年

    if request.args.get('year_begin') and request.args.get('year_end'):
        year_range = range(int(request.args.get('year_begin')) -1911, int(request.args.get('year_end'))- 1911)


    city = request.args.get('city')
    if not city or len(city) < 1: city = '臺北市'
    user_input_record = {
        'houseAddr':houseAddr, 'district':district, 'city':city, 'which_floor': which_floor,
        'house_year': house_year, 'landsize_Ibuy':landsize_Ibuy, 'year_begin':request.args.get('year_begin'), 'year_end': request.args.get('year_end'),
        'onlyHaveCarResult': onlyHaveCarResult
    }

    city_symbol = analyzer.country_map[city.replace('台', '臺')]
    if houseAddr or district:
        _, __, analyzeResult = analyzer.fetchHouseInfo(city_symbol, houseAddr, district, which_floor, house_year, year_range, onlyHaveCarResult)
        return render_template('index.html', labels=_, content=(__), dbInitVal = user_input_record, analyzeResult = analyzeResult)
    else:
        return render_template('index.html', labels=[], content={}, dbInitVal = user_input_record, analyzeResult = {})

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.run('127.0.0.1', 21247, debug=True)