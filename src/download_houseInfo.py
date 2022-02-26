
import requests, tqdm
import os
import zipfile
import time
import os
import pandas as pd

def real_estate_crawler(year, season):
    if year > 1000:
        year -= 1911

    try:
        
      # download real estate zip file
      res = requests.get("https://plvr.land.moi.gov.tw//DownloadSeason?season="+str(year)+"S"+str(season)+"&type=zip&fileName=lvr_landcsv.zip")
      # save content to file
      fname = str(year)+str(season)+'.zip'
      open(fname, 'wb').write(res.content)

      # make additional folder for files to extract
      folder = 'real_estate' + str(year) + str(season)
      if not os.path.isdir(folder):
          os.mkdir(folder)

      # extract files to the folder
      with zipfile.ZipFile(fname, 'r') as zip_ref:
          zip_ref.extractall(folder)
          return True
    except zipfile.BadZipFile:
      return False

import shutil
for d in [d for d in os.listdir() if d[:4] == 'real']: shutil.rmtree(d)
for year in tqdm.tqdm(range(108, 112)):
    for season in range(1,5):
          if not real_estate_crawler(year, season): break # last one records?
