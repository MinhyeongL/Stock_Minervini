import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from pykrx import stock


def Minervini:
    def __init__(self, company_df):
        self.company_df = company_df
        self.growth_stock = set()
        
    
    def filter_price(self):
        for col in tqdm(self.company_df.columns):
            tmp = self.company_df.loc[:, [com]]
            tmp['TimeStamp'] = pd.Series(tmp.index).apply(lambda x : x.timestamp()).values
            tmp['MA50'] = tmp[col].rolling(50).mean()
            tmp['MA150'] = tmp[col].rolling(150).mean()
            tmp['MA200'] = tmp[col].rolling(200).mean()


            if (tmp[col][-1] > tmp['MA150'][-1]) and (tmp[col][-1] > tmp['MA200'][-1]):
                self.growth_stock.add(col)
            else: continue

            if tmp['MA150'][-1] < tmp['MA200'][-1]:
                self.growth_stock.discard(col)

            if tmp['MA200'][-40:].corr(tmp['TimeStamp'][-40:]) < 0.5:
                self.growth_stock.discard(col)

            if tmp[col][-1] < tmp['MA50'][-1]:
                self.growth_stock.discard(col)

            if tmp[col][-1] < tmp[col].min()*1.3:
                self.growth_stock.discard(col)

            if tmp[col][-1] < tmp[col].max()*0.75:
                self.growth_stock.discard(col)
    
    
    def filter_eps(self, code_dict, start=='20210101', end='20231231'): 
        self.growth_finance = dict()
        for corp in tqdm(self.growth_stock):
            try:
                code = code_dict[corp]
                df = stock.get_market_fundamental_by_date(start, end, code, freq='m')
                df = df.resample('Q').last()
                if df.EPS[1] < df.EPS[5] < df.EPS[9]:
                    self.growth_finance[corp] = df
    
            except:
                continue
                
    
    def visualize(self):
        for corp in self.growth_finance.keys():
            print(corp)
            plt.figure(figsize=(10, 3))
            self.company_df[key].plot()
            plt.show()
    