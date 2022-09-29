import sqlite3
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

def fetchHouseInfo_fromSqlite(in_city_name, in_house_addr, in_district, in_whichFloor, in_houseOld, in_yearRange, in_onlyHaveCarResult):

    db = sqlite3.connect('database.db')
    ret = {}
    
    most_rich_buyerInfo = [0, 0] # [floor, 每坪買多少？]

    # fetch all the records with that user specfic conditions
    search_result = list(db.cursor().execute("select * from houseinfo where HOUSE_ADDR like ? and HOUSE_ADDR like ? and HOUSE_ADDR like ?;", [f"%{in_city_name}%", f"%{in_house_addr}%", f"%{in_district}%"] ))
    for curr_record in search_result:
        ID,BUY_YEAR,BUY_DATE,HOUSE_ADDR,HOUSE_TYPE,FLOOR,HOUSE_YEAR,LAND_SIZE,PUBLIC_LAND_RATE,TOTAL_PRISE,PER_LAND_PRISE, COMMENT = curr_record

        # user have their input conditions?
        if in_houseOld != None and not in_houseOld in range(HOUSE_YEAR-5, HOUSE_YEAR+6):
            continue
        if not BUY_YEAR in in_yearRange:
            continue
        if in_onlyHaveCarResult and COMMENT == '':
            continue
        
        if not FLOOR in ret: ret[FLOOR] = {'perland_avgCost': 0, 'currFloor_avgSharedPercent':0, 'currFloorDB': []}
        
        if PER_LAND_PRISE >= most_rich_buyerInfo[1]:
            most_rich_buyerInfo = [FLOOR, PER_LAND_PRISE]
        ret[FLOOR]['currFloorDB'].append([ 
            BUY_DATE, HOUSE_ADDR, HOUSE_TYPE, f"{FLOOR}樓", HOUSE_YEAR, f"{LAND_SIZE:.2f}", f"{PUBLIC_LAND_RATE:.2f}%",
            f"{TOTAL_PRISE}萬", f"{PER_LAND_PRISE}萬", COMMENT
        ])
        ret[FLOOR]['perland_avgCost'] += int(PER_LAND_PRISE)
        ret[FLOOR]['currFloor_avgSharedPercent'] += int(PUBLIC_LAND_RATE)
        
    # generate the analysis report for the user
    if len(ret) < 1:
        return ['成交日期', '購買物件', '格局', '樓層', '屋齡', '主建物坪數', '公設比', '總價', '每坪價格（扣除車位）', '備註'], ret, {'lowest_floorInfo': [0,0], 'highest_floorInfo':[0,0], 'perFloor_addMoney': 0} 

    
    avg_landCost = 0
    try:
        for indx in ret:
            ret[indx]['perland_avgCost'] /= len(ret[indx]['currFloorDB'])
            ret[indx]['currFloor_avgSharedPercent'] /= len(ret[indx]['currFloorDB'])
        avg_landCost += ret[indx]['perland_avgCost'] 
    except:
        print(ret)

    avg_landCost = int(avg_landCost / len(ret))
    lowest_floorInfo, highest_floorInfo = [1000000, 0], [-1000000, 0]  # [ floor, perland_cost? ]
    lowest_floorIndx = sorted(ret.keys())[0]
    lowest_floorInfo = [lowest_floorIndx, ret[lowest_floorIndx]['perland_avgCost']]
    highest_floorIndx = sorted(ret.keys())[-1]
    highest_floorInfo = [highest_floorIndx, ret[highest_floorIndx]['perland_avgCost']]

    analyzeResult = { 
        'avg_landCost': avg_landCost,
        'lowest_floorInfo': lowest_floorInfo, 
        'highest_floorInfo': highest_floorInfo, 
        'richest_buyerInfo': most_rich_buyerInfo,
        'perFloor_addMoney': int((highest_floorInfo[1] - lowest_floorInfo[1]) / (highest_floorInfo[0] - lowest_floorInfo[0] + 0.001) * 10000) }
        
    return ['成交日期', '購買物件', '格局', '樓層', '屋齡', '主建物坪數', '公設比', '總價', '每坪價格（扣除車位）', '備註'], ret, analyzeResult

    
