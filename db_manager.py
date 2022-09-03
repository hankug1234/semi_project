import pymysql as db
import pandas as pd

class DB_manager:
    def __init__(self,path='config.json'):
        self.config = pd.read_json(path,orient='index')
        self.table_list = None
        self.convert_table = {'int64':'BIGINT','float64':'DECIMAL(25,7)','object':'TEXT','datetime64[ns]':'DATETIME','category':'ENUM','bool':'BOOL'}
        cd = self.config[0]
        try:
            self.conn = db.connect(host=cd[0], user=cd[1], password=cd[2])
            self.cursor = self.conn.cursor()
            make_db = f"create database if not exists {cd[3]};"
            use = f"use {cd[3]};"
            self.cursor.execute(make_db)
            self.cursor.execute(use)
            self.conn.commit()
        except Exception as e:
            print(e)
        self.get_table_list()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def save_dr(self,dr):
        fc_list = dr.get_fc_list()
        data = dr.cur_s_data

        if fc_list is None:
            print("fc_list is None")
        else:
            if dr.fc_code.lower() in self.table_list:
                pass
            else:
                self.save_data(fc_list,dr.fc_code)

        if data is None:
            print("cur_s_data is None")
        else:
            for k in data.keys():
                if k.lower() in self.table_list:
                    continue
                self.save_data(data[k],k)


    def save_data(self,df,name,p_key=None):
        try:
            self.create_table(df,name,p_key)
            self.insert_table(df,name)
            return True
        except Exception as e:
            print(e)
            return False

    def read_data(self,name):
        try:
            sql = f"select * from {name}"
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            sql = f"show columns from {name}"
            self.cursor.execute(sql)
            columns = self.cursor.fetchall()
            columns = [col[0] for col in columns]
            df = pd.DataFrame(data = data,columns=columns)
            return df
        except Exception as e:
            print(e)
            return None


    def get_table_list(self):
        sql = 'show tables'
        self.cursor.execute(sql)
        self.table_list = [t[0] for t in self.cursor.fetchall()]
        return self.table_list


    def create_table_sql(self,type_list,name,col_name,p_key=None):
        conver_table = self.convert_table
        table = []
        t_sql = []
        table.append('(')
        for i,t in enumerate(type_list):
            t_sql.append("`"+col_name[i]+"`"+" "+conver_table[t])
        table.append(",".join(t_sql))
        if p_key is None:
            table.append(',id INT auto_increment primary key')
        else:
            table.append(f',primary key({p_key})')
        table.append(') character set utf8')
        " ".join(table)
        make_table = f'create table if not exists {name} {" ".join(table)}'
        return make_table

    def create_insert_sql(self,table_name,col_names,cols_type,stock_record):
        sql = []
        filed=[]
        values=[]
        value=[]
        sql.append(f'insert into {table_name} ')
        filed.append("(")
        filed.append(",".join(["`"+column+"`" for column in col_names]))
        filed.append(")")
        sql.append(" ".join(filed))
        sql.append('values')
        for record in stock_record:
            for i,data in enumerate(record):
                d = str(data)
                if d in ["nan","NaT"]:
                    value.append('null')
                else:
                    if cols_type[i] == 'TEXT' or cols_type[i] == 'DATETIME':
                        value.append('"'+d+'"')
                    else:
                        value.append(d)
            values.append("("+",".join(value)+")")
            del value
            value = []
        sql.append(",".join(values))
        return " ".join(sql)



    def create_table(self,df,name,p_key=None):
        cols = df.columns
        cols_type = [str(df[t].dtype) for t in cols]
        sql = self.create_table_sql(cols_type,name,cols,p_key)
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def insert_table(self,df,name):
        cols = df.columns
        cols_type = [self.convert_table[str(df[t].dtype)] for t in cols]
        sql = self.create_insert_sql(name,cols,cols_type,df.values)
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()


