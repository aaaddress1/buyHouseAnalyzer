import sqlite3, os, datetime, math
import pandas as pd

country_map = {
	'臺北市': 'a',
	'臺中市': 'b',
	'基隆市': 'c',
	'臺南市': 'd',
	'高雄市': 'e',
	'新北市': 'f',
	'宜蘭縣': 'g',
	'桃園市': 'h',
	'嘉義市': 'i',
	'新竹縣': 'j',
	'苗栗縣': 'k',
	'南投縣': 'm',
	'彰化縣': 'n',
	'新竹市': 'o',
	'雲林縣': 'p',
	'嘉義縣': 'q',
	'屏東縣': 't',
	'花蓮縣': 'u',
	'臺東縣': 'v',
	'金門縣': 'w',
	'馬公市': 'x'
 }

zh2digit_table = {'零': 0, '一': 1, '二': 2, '兩': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '〇': 0, '○': 0, '○': 0, '０': 0, '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '壹': 1, '貳': 2, '參': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10, '佰': 100, '仟': 1000, '萬': 10000, '億': 100000000}
def get_floor_byCNstr(in_szChineseFloor):
	try:
		tmp, billion, result, digit_num = 0, 0, 0, 0
		while digit_num < len(in_szChineseFloor):
			tmp_zh = in_szChineseFloor[digit_num]
			tmp_num = zh2digit_table.get(tmp_zh, None)
			if tmp_num == 100000000:
				result = result + tmp
				result = result * tmp_num
				billion = billion * 100000000 + result
				result = 0
				tmp = 0
			elif tmp_num == 10000:
				result = result + tmp
				result = result * tmp_num
				tmp = 0
			elif tmp_num >= 10:
				if tmp == 0:
					tmp = 1
				result = result + tmp_num * tmp
				tmp = 0
			elif tmp_num is not None:
				tmp = tmp * 10 + tmp_num
			digit_num += 1
			result = result + tmp + billion
		return result
	except:
		return None

def transform_CNnum_toNormal_Num(in_str):
	return ''.join([c if (ord(c) not in range(65296, 65296+10)) else chr(ord(c) - 65296 + ord('0')) for c in in_str ])

db = sqlite3.connect('database.db')

db.cursor().execute("drop table houseinfo;")
if list(db.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND name='houseInfo';")) == []:
    print('[!] first time running? building fresh table now!')
    db.execute('''CREATE TABLE houseInfo
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BUY_YEAR              INT      NOT NULL,
    BUY_DATE              TEXT     NOT NULL,
    HOUSE_ADDR            TEXT     NOT NULL,
    HOUSE_TYPE            TEXT     NOT NULL,
    FLOOR                 INT      NOT NULL,
    HOUSE_YEAR            INT      NOT NULL,
    LAND_SIZE             FLOAT    NOT NULL,
    PUBLIC_LAND_RATE      FLOAT    NOT NULL,
    TOTAL_PRISE           FLOAT    NOT NULL,
    PER_LAND_PRISE        FLOAT    NOT NULL,
    COMMENT               TEXT     NOT NULL);''')

db.cursor().execute("delete from houseinfo;")


def parse(dfs):

    df = pd.concat(dfs, sort=True)
    # 建物型態
    df['建物型態2'] = df['建物型態'].str.split('(').str[0]
    df = df[df['備註'].isnull()]

    # 平方公尺換成坪
    df['單價元平方公尺'] = df['單價元平方公尺'].astype(float)
    df['單價元坪'] = df['單價元平方公尺'] * 3.30579
    df['土地位置建物門牌'] = df['土地位置建物門牌'].apply(lambda a: transform_CNnum_toNormal_Num(a))
    df['主建物面積'] = df['主建物面積'].astype(float)
    df = df[ df['主建物面積'] >= 1 ]


    most_rich_buyerInfo = [0, 0] # [floor, 每坪買多少？]
    for indx in range(len(df)):
        curr_row = df.iloc[indx]

        try:
            # 車車資訊
            carcar_land_used = float(curr_row['車位移轉總面積(平方公尺)']) * 0.3025
            carcar_moneycost = int(int(curr_row['車位總價元']) /10000)
            # 主建物資訊
            bought_land_size = round(( float(curr_row['主建物面積']) +float(curr_row['附屬建物面積']) + float(curr_row['陽台面積']) )* 0.3025, 2)
            bought_shared_land_percent = round((1 - ((bought_land_size / float(curr_row['建物移轉總面積平方公尺']) / 0.3025)))*100, 2)
            if isinstance(curr_row['移轉層次'], str):
                which_floor = curr_row['移轉層次'][:-1]
            elif isinstance(curr_row['移轉層次'], str):
                which_floor = int(curr_row['移轉層次']) if curr_row['移轉層次'] != math.nan else 0

            which_floor = get_floor_byCNstr(which_floor)
            if not which_floor: continue # 地下室不宜居住啦
            total_moneycost = int(int(curr_row['總價元']) / 10000)
            
            
            # 處理交易日期民國轉西元
            _ = f"{curr_row['交易年月日']}"
            if len(_) < 8: # _ = '1110501'? 
                dt_bought_house = datetime.datetime.strptime(f"{int(_[:-4]) + 1911}{_[-4:]}","%Y%m%d")
            else:
                dt_bought_house = datetime.datetime.strptime(f"{int(_[:-4]) + 1911}{_[-4:]}","%Y%m%d")

            pp_bought_datetime = datetime.datetime.strftime(dt_bought_house, "%Y-%m-%d")


            # 屋齡
            if isinstance(curr_row['建築完成年月'], str) and len(curr_row['建築完成年月'][:-4]) > 1:
                house_num_old = datetime.date.today().year - (int(curr_row['建築完成年月'][:-4]) + 1911)
                house_so_old = house_num_old
            else:
                house_so_old = -1

            # 每坪數單價

            single_land_cost = round(float(curr_row['單價元坪'] / 10000), 2)
            if math.isnan( curr_row['單價元坪'] ):
                continue
      
            
            db.cursor().execute("INSERT INTO houseInfo (BUY_YEAR,BUY_DATE,HOUSE_ADDR,HOUSE_TYPE,FLOOR,HOUSE_YEAR,LAND_SIZE,PUBLIC_LAND_RATE,TOTAL_PRISE,PER_LAND_PRISE, COMMENT) \
                VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
                    dt_bought_house.year, 
                    pp_bought_datetime, 
                    curr_row['土地位置建物門牌'],
                    curr_row['建物型態'] + (curr_row['主要用途'] if '用' in str(curr_row['主要用途']) else ''), 
                    which_floor,
                    house_so_old, 
                    bought_land_size, 
                    bought_shared_land_percent, 
                    total_moneycost, 
                    single_land_cost, 
                    f"含車位{carcar_moneycost}萬（{carcar_land_used:.2f}坪）"if carcar_moneycost >= 1 else ''
                ])

        except Exception as ex:
            print(ex)
     

# collect all the CSV files recored the house info. (from file system)
dirs = [d for d in os.listdir() if d[:4] == 'real']
for in_city_symbol in country_map.values():
    dfs = []
    for d in dirs:
        if os.path.isfile(os.path.join(d, f'{in_city_symbol}_lvr_land_a.csv')):
            df = pd.read_csv(os.path.join(d,f'{in_city_symbol}_lvr_land_a.csv'), index_col=False)
            df['Q'] = d[-1]
            parse([ df.iloc[1:] ])
            db.commit()
db.close()
