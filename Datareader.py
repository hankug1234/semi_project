import FinanceDataReader as fdr
import pandas as pd

class Datareader:
    def __init__(self):
        self.dr = fdr.DataReader
        self.sl = fdr.StockListing
        self.fc_list = None
        self.cur_s_data = None

    def get_graph_data(self,f_code,*s_name):
        self.read_stock_datas(f_code,*s_name)
        return self.to_graph_type(*s_name)

    def read_stock_datas(self,f_code,*s_name):
        if self.fc_list is None:
            self.fc_list = self.sl(f_code)
            self.fc_list.set_index('Name',inplace=True)

        sd_dict = {}

        for name in s_name:
            if name not in self.fc_list.index:
                print(f"don't exist stock {name}")
                return False
            if self.cur_s_data is not None:
                if name in self.cur_s_data.keys():
                    continue

            code = self.fc_list.loc[name,'Symbol']
            s_data = self.dr(symbol=code)
            s_data['name'] = name
            s_data['Date'] = s_data.index
            sd_dict[name] = s_data

        if self.cur_s_data is None:
            self.cur_s_data = sd_dict
        else:
            for name in sd_dict.keys():
                self.cur_s_data[name] = sd_dict[name]
        return True

    def to_graph_type(self,*stock_names):
        stock_names = list(stock_names)
        if(len(stock_names) == 0):
            print('no stock names')
            return False

        if self.cur_s_data is None:
            print('not cur_s_data')
            return False

        for name in stock_names:
            if name not in self.cur_s_data.keys():
                return False

        graph_type = [self.cur_s_data[x] for x in stock_names]
        return pd.concat(graph_type,axis=0)



    def n_m_avg(self,n,stock, column):
        if stock in self.cur_s_data.keys():
            df = self.cur_s_data[stock]
        else:
            print(f'dont exist {stock} data')
            return None

        if column in df.columns:
            for i, c in enumerate(df.columns):
                if c == column:
                    c_n = i
                    return [df.iloc[i:i + (n - 1), c_n].sum() / len(df[column]) for i in range(len(df) - n)]
        return None

