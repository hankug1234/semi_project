import FinanceDataReader as fdr
import pandas as pd
import db_manager
import t_db_manager
from datetime import datetime
class Datareader:
    def __init__(self):
        self.dr = fdr.DataReader
        self.sl = fdr.StockListing
        self.fc_list = None
        self.cur_s_data = None
        self.fc_code = None
        self.current_graph_data =  pd.DataFrame({'Date':[datetime.now()],'Close':[0],'name':['NO DATA']})
        self.default_graph = pd.DataFrame({'Date':[datetime.now()],'Close':[0],'name':['NO DATA']})
        self.current_show_stock_list = []
        self.current_m_avg_graph_data = None
        self.multi_state = False
        self.manager = t_db_manager.DB_manager()#db_manager.DB_manager()

    def read_period_stock_data(self,f_code,s_name,start,end):
        if self.fc_list is None:
            self.fc_code = f_code
            if f_code in self.manager.table_list:
                self.fc_list = self.manager.read_data(f_code)
            else:
                self.fc_list = self.sl(f_code)
            self.fc_list.set_index('Name',inplace=True)

        if s_name not in self.fc_list.index:
            print(f"don't exist stock {s_name}")
            return False

        code = self.fc_list.loc[s_name, 'Symbol']
        s_data = self.dr(code,start,end)
        s_data['name'] = s_name
        s_data['Date'] = s_data.index
        return s_data

    def sync_db(self):
        for name in self.manager.need_sync_lists.keys():
            self.data_sync(name)
            print(f"{name} sync success")
    def data_sync(self,name):
        need_sync_lists = self.manager.need_sync_lists.keys()
        if name.lower() in need_sync_lists:
            data = self.read_period_stock_data('KRX',name.upper(),self.manager.need_sync_lists[name],datetime.now())
            self.manager.save_data(data,name)


    def get_graph_period_data(self,df,start,end):
        start = pd.to_datetime(start, format='%Y-%m-%d %H:%M:%S')
        end = pd.to_datetime(end, format='%Y-%m-%d %H:%M')
        data = df[(df['Date'] > start) & (df['Date'] < end)]
        if len(data) == 0:
            return pd.DataFrame({'Date':[0],'Close':[0],'name':['NO DATA']})
        return data



    def get_fc_list(self):
        if self.fc_list is None:
            return None
        return self.fc_list.reset_index()

    def on_multi_state(self):
        self.multi_state = True
    def off_multi_state(self):
        self.multi_state = False
    def read_fc(self,f_code):
        if self.fc_list is None:
            self.fc_code = f_code
            if f_code in self.manager.table_list:
                self.fc_list = self.manager.read_data(f_code)
            else:
                self.fc_list = self.sl(f_code)
            self.fc_list.set_index('Name',inplace=True)

    def get_graph_data(self,f_code,*s_name):
        self.read_stock_datas(f_code,*s_name)
        if(self.multi_state):
            for name in [*s_name]:
                if name in self.current_show_stock_list:
                    continue
                else:
                    self.current_show_stock_list.append(name)
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
            if f_code.lower() in self.manager.table_list:
                self.fc_list = self.manager.read_data(f_code)
            else:
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
                elif name.lower() in self.manager.table_list:
                    s_data = self.manager.read_data(name)
                    sd_dict[name] = s_data
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
                    mavg['Date'] = list(df['Date'][:len(df)-n+1])
                    mavg['name'] = f'mavg{n}'
                    mavg.index = mavg['Date']
                    return mavg
        return None