__author__ = 'userme865'
import MySQLdb

import math
import update
import semantic


def find_all_index(arr, item):
    return [i for i, a in enumerate(arr) if a == item]


def TermWeight_In_document(term):
    global total_num_pages
    conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
    cur = conn.cursor()
    conn.select_db('python')
    find = cur.execute('select * from indexer where words = %s', [term])
    result = cur.fetchone()  # ----------------------------------------modify---- fetchall
    cur.close()
    conn.close()

    # Index_Doc = [i for i in result[1].split(',')]
    # Num_Doc = len(Index_Doc)  # Number of Documents
    Num_Doc = total_num_pages
    if find == 0:
        print ''
        return {}, Num_Doc, 1
    Dic_TermInDoc = [eval(j) for j in result[2].split(',')]
    Num_Doc_Contain_Term = len(Dic_TermInDoc)  # Number of documents that contain Term
    Weight_Terms_doc = {dic.keys()[0]: dic.values()[0] * math.log(Num_Doc * 1.0 / Num_Doc_Contain_Term) for dic in
                        Dic_TermInDoc}  # {page1:w1,pagen:wn}for term 1
    return Weight_Terms_doc, Num_Doc, Num_Doc_Contain_Term


def TermWeight_Total(terms):
    termdic = {}  # {term1:w1,term:wm}
    docdic = []  # [# {page1:w1,pagen:wn}for term 1,# {page1:w1,pagen,wn}for term 2]
    for term in terms:
        tuple = TermWeight_In_document(term)

        Freq = len([i for i, a in enumerate(terms) if a == term]) * 1
        Weight_Term = Freq * math.log(tuple[1] * 1.0 / tuple[2])
        termdic[term] = Weight_Term
        docdic.append(tuple[0])
    return termdic, docdic


# #termdic:{term1:w1,term:wm}   docdic:[{page1:weight1,page2:weight2},{page1:weighte1}] for different term
# direction: term1,term2........term n
def scores(terms):
    update.update_db()
    weight_group_for_page = []  # [[page1...],[.page2..],....]
    score = {}
    rq_term_weight, page_weight_for_term = TermWeight_Total(terms)
    weight_req = rq_term_weight.values()  #[weight of term1....weight of termm]
    pages_index_sum = []
    for page_weight in page_weight_for_term:
        pages_for_term = page_weight.keys()
        for page in pages_for_term:
            if page not in pages_index_sum:
                pages_index_sum.append(page)

    for pageIndex in pages_index_sum:
        weight_sub = []
        for page_weight in page_weight_for_term:
            try:
                weight_sub.append(page_weight[pageIndex])
            except:
                weight_sub.append(0)
        weight_group_for_page.append(weight_sub)

    for weight_list in weight_group_for_page:
        sum_1 = 0
        sum_2 = 0
        sum_3 = 0
        for wr in weight_req:
            sum_1 = sum_1 + wr * weight_list[weight_req.index(wr)]
            sum_2 = sum_2 + wr * wr
        for wd in weight_list:
            sum_3 = sum_3 + wd * wd
        score[pages_index_sum.pop(0)] = sum_1 * 1.0 / (math.sqrt(sum_2) * math.sqrt(sum_3))
    return score


if __name__ == '__main__':
    print 'Please write keywords'
    raw = raw_input()
    try:  # start msql and creat stable at first time
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
        cur = conn.cursor()
        conn.select_db('python')
        total_num_pages = cur.execute('select url from pagedic')
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    # raw = 'know'
    raw_extraction = str(raw).lower().split(' ')
    and_index = find_all_index(raw_extraction, 'and')
    not_index = find_all_index(raw_extraction, 'or')
    RequireWords = semantic.pasrsing(str(raw))  # get every word from request
    back_result = scores(RequireWords)
    back_sorted = sorted(zip(back_result.values(), back_result.keys()), reverse=True)
    num_result = len(back_sorted)
    display_index = 0
    print 'Found '+str(num_result)+' results. Click link:'
    for item in back_sorted:
        display_index += 1
        id = item[1]
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
            cur = conn.cursor()
            conn.select_db('python')
            InitialIndex = cur.execute('select url from pagedic where id =%s', [id])
            url = cur.fetchone()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        print str(display_index)+'...'+str(url)
    print 'Designed By Ding Chao'









