import sqlite3



def get_table(table):
    sql="SELECT * FROM %s"%table
    con=sqlite3.connect("/Volumes/Movie/Lovecos/lovecos.db")
    cur=con.cursor()
    res=cur.execute(sql)
    for r in res:
        print(r)
    
if __name__ == '__main__':
    get_table('chinacos')