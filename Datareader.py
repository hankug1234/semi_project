import FinanceDataReader as fdr
import pandas as pd

class Datareader:
    def __init__(self):
        #data_stor
        self.dr = fdr.DataReader
        self.sl = fdr.StockListing
        self.fc_list = None
        self.cur_s_data = None
        self.fc_code = None
        self.current_graph_data =  pd.DataFrame({'Date':[0],'Close':[0]})
        self.default_graph = pd.DataFrame({'Date':[0],'Close':[0]})
        self.current_show_stock_list = None
        self.current_m_avg_graph_data = None
        self.multi_state = False

    def on_multi_state(self):
        self.multi_state = True
    def off_multi_state(self):
        self.multi_state  = False
    def read_fc(self,f_code):
        if self.fc_list is None:
            self.fc_code = f_code
            self.fc_list = self.sl(f_code)
            self.fc_list.set_index('Name',inplace=True)

    def get_graph_data(self,f_code,*s_name):
        self.read_stock_datas(f_code,*s_name)
        if(self.multi_state):
            self.current_show_stock_list.extend([*s_name])
            self.current_graph_data = self.to_graph_type(*self.current_show_stock_list).loc[:,['Close','name','Date']]
        else:
            self.current_graph_data = self.to_graph_type(*s_name).loc[:,['Close','name','Date']]
            self.current_show_stock_list = [*s_name]
        return self.current_graph_data

    def get_graph_mavg_data(self,f_code,s_name,*n_avgs):
        self.read_stock_datas(f_code,s_name)
        result = [self.n_m_avg(n,s_name, 'Close') for n in n_avgs]
        result.append(self.cur_s_data[s_name].loc[:,['Close','name','Date']])
        self.current_m_avg_graph_data = pd.concat(result,axis=0)
        return self.current_m_avg_graph_data

    def read_stock_datas(self,f_code,*s_name):
        if self.fc_list is None:
            self.fc_code = f_code
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
                    mavg = pd.DataFrame(data={'Close':[df.iloc[i:i + n, c_n].sum() / n for i in range(len(df) - n+1)]})
                    mavg['Date'] = df.index[:len(df)-n+1]
                    mavg['name'] = f'mavg{n}'
                    mavg.index = mavg['Date']
                    return mavg
        return None

