# import pymssql
#
# conn = pymssql.connect(server='volttroniot.database.windows.net', user='volttron@volttroniot', password='vvvVVV123@@@', database='database_volttron')
#
# # cursor = conn.cursor()
# query3= ("CREATE TABLE VolttronTest12(SetPointID int,ParameterName varchar(255),ParameterValue int);")
# query = ("INSERT INTO VolttronTest12(SetPointID, ParameterName, ParameterValue) VALUES ('1','SetPoint1','12');")
# query1 = ("INSERT INTO VolttronTest12(SetPointID, ParameterName, ParameterValue) VALUES ('2','SetPoint2','13');")
# query2 = ("INSERT INTO VolttronTest12(SetPointID, ParameterName, ParameterValue) VALUES ('3','SetPoint3','14');")
# cursor.execute(query3)
# cursor.execute(query)
# cursor.execute(query1)
# cursor.execute(query2)
# cursor.execute(
#     "SELECT * FROM VolttronTest12;"
# )
# row = cursor.fetchone()
# print (row)
# while row:
#     print "Inserted instance ID : " + str(row[0])
#     print "Inserted parameter name : " + str(row[1])
#     print "Inserted parameter value : " + str(row[2])

import pymssql

conn = pymssql.connect(server='volttroniot.database.windows.net', user='volttron@volttroniot', password='vvvVVV123@@@',
                       database='database1')
cur = conn.cursor()
conn.autocommit(True)
cur.execute('CREATE TABLE test2(id INT, name VARCHAR(100))')
cur.executemany("INSERT INTO test2 VALUES(%d, %s)", \
    [ (1, 'John Doe'), (2, 'Jane Doe') ])

cur.execute('SELECT * FROM test2 WHERE name=%s', 'John Doe')
row = cur.fetchone()
while row:
    print "ID=%d, Name=%s" % (row[0], row[1])
    row = cur.fetchone()
# if you call execute() with one argument, you can use % sign as usual
# (it loses its special meaning).
conn.close()

