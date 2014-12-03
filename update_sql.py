__author__ = 'userme865'
# ver 0.1

import MySQLdb
def update_db():
    try:  # start msql and creat stable at first time
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
        cur = conn.cursor()
        conn.select_db('python')
        cur.execute('DROP TABLE dataexchange')
        cur.execute(
            "CREATE  TABLE dataexchange SELECT indexer.words, group_concat(indexer.pages ORDER BY indexer.words SEPARATOR ',') AS 'pages',group_concat(indexer.pagewords ORDER BY indexer.words SEPARATOR ',') AS 'pagewords' from indexer GROUP BY indexer.words")
        cur.execute("DROP TABLE  indexer")
        cur.execute("CREATE TABLE indexer SELECT* FROM dataexchange")
        conn.commit()
        cur.close()
        conn.close()

    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
