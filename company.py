import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
from collections import deque

import FinanceDataReader as fdr
import OpenDartReader
import yfinance as yf
from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup
from urllib.request import urlopen


class Company:
    def __init__(self, api_key):
        self.api_key = api_key
        self.now = datetime.now().date()
        
    
    def get_company_list(self, magic=False):
        stock_list = fdr.StockListing('KRX').dropna().reset_index(drop=True)
        stock_list = stock_list[(stock_list.Market == 'KOSPI') | (stock_list.Market == 'KOSDAQ')].reset_index(drop = True)
        
        if magic:
            self.get_magic_stock_company_list()
            stock_list = stock_list[stock_list.Name.isin(self.magic_list)]
        
        self.stock_list = stock_list
        self.stock_code = self.stock_list.Code.tolist()
        
        
    def get_magic_stock_company_list(self):
        # 불러오려는 url 입력하기
        url = 'http://m.o.woobi.co.kr/stock/magicNewList.php'
        
        # urlopen 함수를 통해 web 변수를 생성
        web = urlopen(url)
        
        # BeautifulSoup으로 web 페이지상의 HTML 구조를 파싱
        source = BeautifulSoup(web, 'html.parser')
        
        self.magic_list = []
        for x in source.find_all('td', {'width' : '40%'})[1:]:
            self.magic_list.append(x.get_text().strip())
            
        
    def get_company_info(self, magic=False):
        dart = OpenDartReader(self.api_key)

        self.get_company_list(magic)

        company_list = deque()
        fail_list = deque(self.stock_code)

        pbar = tqdm(total=len(fail_list), desc='Processing', unit='iteration')

        while fail_list:
            code = fail_list.popleft()
            try:
                company_list.append(dart.company(code))
            except:
                fail_list.append(code)

            pbar.update(1)   

        company_dict = {}
        for x in tqdm(company_list):
            if x['status'] == '000':
                company_dict[x['stock_code']] = (x['stock_name'], x['corp_cls'])

        self.company_dict = company_dict


    def make_dataset(self, period=3):
#         self.get_company_info()

        df = pd.DataFrame()

        for code, (name, cls) in tqdm(self.company_dict.items()):
            if cls == 'Y':
                market = 'KS'
            elif cls == 'K':
                market = 'KQ'
            tmp = yf.download(f'{code}.{market}',
                              start = self.now-relativedelta(years=period),
                              end=self.now, progress=False)[['Close']].rename(columns = {'Close':name})
            df = pd.merge(df, tmp, how = 'outer', left_index = True, right_index = True)
        
        return df