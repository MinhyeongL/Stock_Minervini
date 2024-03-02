import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt

from pykrx import stock
import yfinance as yf


class Minervini:
    def __init__(self, company_df):
        self.company_df = company_df
        self.growth_stock = set()
        
    
    def filter_price(self):
        for col in tqdm(self.company_df.columns):
            tmp = self.company_df.loc[:, [col]]
            tmp['TimeStamp'] = pd.Series(tmp.index).apply(lambda x : x.timestamp()).values
            tmp['MA50'] = tmp[col].rolling(50).mean()
            tmp['MA150'] = tmp[col].rolling(150).mean()
            tmp['MA200'] = tmp[col].rolling(200).mean()
#             self.tmp = tmp
            # 1
            if (tmp[col][-1] > tmp['MA150'][-1]) and (tmp[col][-1] > tmp['MA200'][-1]):
                self.growth_stock.add(col)
            else: continue
            
            # 2. 150일 이동평균선이 200일 이동평균선 위에 있다.
            if tmp['MA150'][-1] < tmp['MA200'][-1]:
                self.growth_stock.discard(col)
                
            # 3. 200일 이동평균선이 적어도 1개월 동안 상승 추세에 있다.
            if tmp['MA200'][-40:].corr(tmp['TimeStamp'][-40:]) < 0.5:
                self.growth_stock.discard(col)
                
            # 4. 50(10주)일 이동평균선이 150일 이동평균선 및 200일 이동평균선 위에 있다.
            if tmp['MA50'][-1] < tmp['MA150'][-1]:
                self.growth_stock.discard(col)
            if tmp['MA50'][-1] < tmp['MA200'][-1]:
                self.growth_stock.discard(col)
                
            # 5. 현 주가가 50일 이동평균선 위에 있다.
            if tmp[col][-1] < tmp['MA50'][-1]:
                self.growth_stock.discard(col)
                
            # 6. 현 주가가 52주 신저가보다 최소한 30퍼센트 위에 있다.
            if tmp[col][-1] < tmp.iloc[int(len(tmp)*0.5):, 0].min()*1.3:
                self.growth_stock.discard(col)
                
            # 7. 현 주가가 최소한 52주 신고가의 25퍼센트 안에 있다.(신고가에 가까울수록 좋다.)
            if tmp[col][-1] < tmp.iloc[int(len(tmp)*0.5):, 0].max()*0.75:
                self.growth_stock.discard(col)
                    
    
#     def filter_eps(self, code_dict, start='20210101', end='20240131'): 
#         self.growth_finance = dict()
#         for corp in tqdm(self.growth_stock):
#             try:
#                 code = code_dict[corp]
#                 df = stock.get_market_fundamental_by_date(start, end, code, freq='m')
#                 df = df.resample('Q').last()
#                 if df.EPS[1] < df.EPS[5] < df.EPS[9]:
#                     self.growth_finance[corp] = df
    
#             except:
#                 continue
    
    
    def filter_eps(self, code_dict):
        self.growth_finance = dict()
        for corp in tqdm(self.growth_stock):
            try:
                code = code_dict[corp]
                tmp = yf.Ticker(code)
                eps = tmp.income_stmt.T[::-1][['Basic EPS']]
        
                i = 1
                sign = False
                while i < len(eps):
                    if eps.iloc[i-1, 0] > eps.iloc[i, 0]:
                        sign = True
                        break
                    i += 1
                if sign == True:
                    continue
                self.growth_finance[corp] = eps
            except:
                continue
        
    
    
    
    def visualize(self):
        for corp in sorted(list(self.growth_finance.keys())):
            print(corp)
            plt.figure(figsize=(10, 6))
            self.company_df[corp].plot(label = corp)
            self.company_df[corp].rolling(50).mean().plot(label = 'MA50')
            self.company_df[corp].rolling(150).mean().plot(label = 'MA150')
            self.company_df[corp].rolling(200).mean().plot(label = 'MA200')
            
            plt.legend(loc = 'lower right')
            plt.show()
