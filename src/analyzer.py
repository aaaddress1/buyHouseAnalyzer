
import datetime, os, math, numpy
import pandas as pd

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

# 歷年資料夾
dirs = [d for d in os.listdir() if d[:4] == 'real']

dfs_db = {}
for city_symbol in ['a','f']:# 'b', 'c', 'd', 'e',  ]:#'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 't', 'u', 'v', 'w', 'x']:
	dfs = []
	for d in dirs:
		if os.path.isfile(os.path.join(d, f'{city_symbol}_lvr_land_a.csv')):
			df = pd.read_csv(os.path.join(d,f'{city_symbol}_lvr_land_a.csv'), index_col=False)
			df['Q'] = d[-1]
			dfs.append(df.iloc[1:])
		dfs_db[city_symbol] = dfs
			
	

# Taipei = "a"
def fetchHouseInfo(in_city_symbol, in_house_addr, in_district, in_whichFloor):
	df = pd.concat(dfs_db[in_city_symbol], sort=True)

	# 平方公尺換成坪
	df['單價元平方公尺'] = df['單價元平方公尺'].astype(float)
	df['單價元坪'] = df['單價元平方公尺'] * 3.30579
	# 建物型態
	df['建物型態2'] = df['建物型態'].str.split('(').str[0]
	df = df[df['備註'].isnull()]

	df['土地位置建物門牌'] = df['土地位置建物門牌'].apply(lambda a: transform_CNnum_toNormal_Num(a))
	

	if in_house_addr: df = df[ df['土地位置建物門牌'].str.contains(in_house_addr, na=False) ]
	if in_district: df = df[ df['鄉鎮市區'].str.contains(in_district, na=False) ]
	df = df[ df['主建物面積'] >= 1 ]
	ret = {}
	for indx in range(len(df)):
		curr_row = df.iloc[indx]

		try:
			# 車車資訊
			carcar_land_used = float(curr_row['車位移轉總面積(平方公尺)']) * 0.3025
			carcar_moneycost = int(int(curr_row['車位總價元']) /10000)

			# 主建物資訊
			bought_land_size = float(curr_row['建物移轉總面積平方公尺']) * 0.3025 - carcar_land_used
			bought_shared_land_size = float(curr_row['建物移轉總面積平方公尺']) * 0.3025 - (float(curr_row['主建物面積']) + float(curr_row['附屬建物面積']) + float(curr_row['陽台面積']))* 0.3025
			
			if isinstance(curr_row['移轉層次'], str):
				which_floor = curr_row['移轉層次'][:-1]
			elif isinstance(curr_row['移轉層次'], str):
				which_floor = int(curr_row['移轉層次']) if curr_row['移轉層次'] != math.nan else 0

			which_floor = get_floor_byCNstr(which_floor)
			total_moneycost = int(curr_row['總價元']) / 10000
			
			
			# 處理交易日期民國轉西元
			_ = f"{curr_row['交易年月日']}"
			dt_bought_house = datetime.datetime.strptime(f"{int(_[:-4]) + 1911}{_[-4:]}","%Y%m%d")
			pp_bought_datetime = datetime.datetime.strftime(dt_bought_house, "%Y-%m-%d")


			# 屋齡
			if isinstance(curr_row['建築完成年月'], str):
				house_so_old = f"{datetime.date.today().year - (int(curr_row['建築完成年月'][:-4]) + 1911)}年"
			else:
				house_so_old = "不詳"


			# 每坪數單價
			try:
				single_land_cost = float(curr_row['單價元坪'] / 10000) 
			except:
				single_land_cost = '不詳'

			# 濾掉地下室、土地購買、一樓店面
			if which_floor and bought_land_size > 0 and curr_row['建物現況格局-房'] != '0':

				if not which_floor in ret: ret[which_floor] = []
				ret[which_floor].append([ 
					pp_bought_datetime, 
					curr_row['土地位置建物門牌'],
					f"{curr_row['建物現況格局-房']}房{curr_row['建物現況格局-廳']}廳{curr_row['建物現況格局-衛']}衛/{curr_row['建物現況格局-隔間']}夾層",
					which_floor,
					house_so_old, 
					bought_land_size, 
					f"{int(bought_shared_land_size * 100/( float(curr_row['建物移轉總面積平方公尺']) * 0.3025))}%",
					total_moneycost, 
					single_land_cost,
					f"含車位{carcar_moneycost}萬（{carcar_land_used:.2f}坪）"if carcar_moneycost >= 1 else ''
				])
		except Exception as ex:
			raise (ex)
	return ['成交日期', '購買物件', '房/廳/衛/夾層', '樓層', '屋齡', '主建物坪數', '公設比', '總價（萬）', '每坪價格（扣除車位）/萬', '備註'], ret