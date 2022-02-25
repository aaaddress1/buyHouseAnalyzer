from flask import Flask, render_template
from flask import request
import analyzer, json
app = Flask(__name__)


@app.route('/')
def hello_world():

    houseAddr = request.args.get('houseAddr')
    district = request.args.get('district')
    which_floor = int(request.args.get('which_floor')) if request.args.get('which_floor') else None
    if request.args.get('landsize_Ibuy'):
        landsize_Ibuy = float(request.args.get('landsize_Ibuy'))
    else:
        landsize_Ibuy = None
    search_similar_year = "true" == (request.args.get('only_same_year'))

    if request.args.get('house_year'):
        house_year = int(request.args.get('house_year'))
        house_year = house_year if search_similar_year else None
    else:
        house_year = None

    city = request.args.get('city')
    if not city or len(city) < 1: city = '臺北市'
    user_input_record = {
        'houseAddr':houseAddr, 'district':district, 'city':city, 'which_floor': which_floor,
        'house_year': house_year, 'only_same_year': search_similar_year, 'landsize_Ibuy':landsize_Ibuy
    }

    city_symbol = analyzer.country_map[city.replace('台', '臺')]
    if houseAddr or district:
        _, __, analyzeResult = analyzer.fetchHouseInfo(city_symbol, houseAddr, district, which_floor, house_year)
        return render_template('index.html', labels=_, content=(__), dbInitVal = user_input_record, analyzeResult = analyzeResult)
    else:
        return render_template('index.html', labels=[], content={}, dbInitVal = user_input_record, analyzeResult = {})

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.run('127.0.0.1', 21247, debug=True)