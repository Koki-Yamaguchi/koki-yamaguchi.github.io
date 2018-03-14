import requests, re, webbrowser, MeCab, glob, sqlite3, time
import generator
from bs4 import BeautifulSoup
mecab = MeCab.Tagger('-d /usr/local/mecab/lib/mecab/dic/mecab-ipadic-neologd/')

def get_all_urls(type):
    all_urls = []
    if type == 0: #AGC
        alpha = ['a', 'b', 'c', 'd', 'e', 'f']
        for number in range(1, 22):
            for i in range(0, 6):
                if number == 9 and i == 5:
                    continue
                numstr = str(number)
                if len(numstr) == 1:
                    numstr = '00' + numstr
                elif len(numstr) == 2:
                    numstr = '0' + numstr
                url = 'https://beta.atcoder.jp/contests/agc' + numstr + '/submissions?f.Task=agc' + numstr + '_' + alpha[i] + '&f.Language=3003&f.Status=AC&f.User=&page='
                all_urls.append(url)
    elif type == 1: #ABC
        alpha = ['#', 'a', 'b', 'c', 'd']
        for number in range(1, 42):
            for i in range(1, 5):
                numstr = str(number)
                if len(numstr) == 1:
                    numstr = '00' + numstr
                elif len(numstr) == 2:
                    numstr = '0' + numstr
                if number >= 20: #ABC problems have tricky urls
                    url = 'https://beta.atcoder.jp/contests/abc' + numstr + '/submissions?f.Task=abc' + numstr + '_' + alpha[i] + '&f.Language=3003&f.Status=AC&f.User=&page='
                else:
                    url = 'https://beta.atcoder.jp/contests/abc' + numstr + '/submissions?f.Task=abc' + numstr + '_' + str(i) + '&f.Language=3003&f.Status=AC&f.User=&page='
                all_urls.append(url)
    elif type == 2: #ARC
        alpha = ['#', 'a', 'b', 'c', 'd']
        for number in range(1, 92):
            for i in range(1, 5):
                numstr = str(number)
                if len(numstr) == 1:
                    numstr = '00' + numstr
                elif len(numstr) == 2:
                    numstr = '0' + numstr
                if number >= 35: #ARC problems have tricky urls
                    url = 'https://beta.atcoder.jp/contests/arc' + numstr + '/submissions?f.Task=arc' + numstr + '_' + alpha[i] + '&f.Language=3003&f.Status=AC&f.User=&page='
                else:
                    url = 'https://beta.atcoder.jp/contests/arc' + numstr + '/submissions?f.Task=arc' + numstr + '_' + str(i) + '&f.Language=3003&f.Status=AC&f.User=&page='
                all_urls.append(url)
    return all_urls

def tokenize(text):
    list = []
    node = mecab.parseToNode(text)
    while (node):
        feature = node.feature.split(',')
        is_noun = feature[0] == '名詞'
        is_number = feature[1] == '数'
        if is_noun and not is_number:
            list.append(node.surface.lower())
        node = node.next
    return list

def clean_ja(texts):
    stop_words_filename = glob.glob('./stop_words.txt')
    f = open(stop_words_filename[0])
    stop_words = f.read()
    result = [word for word in texts if word not in stop_words]
    return result

def get_statement(url):
    problem_url = url[0:40] + 'tasks/' + url[59:67]
    print(problem_url)
    html = requests.get(problem_url)
    soup = BeautifulSoup(html.text, 'lxml')
    all_text = soup.find("div", {"id" : "task-statement"})
    statement = all_text.find("section").text
    tokenized_statement = tokenize(statement)
    clean_statement = clean_ja(tokenized_statement)
    return clean_statement

def get_stop_words():
    stop_words = ['int', 'double', 'bool', 'include', 'for', 'if', 'else', 'while', 'continue', 'break', 
                  'return', 'namespace', 'algorithm', 'iostream', 'bits', 'std', 'cstdio', 'c', 'h',
                  'typedef', 'define', 'struct', 'using', 'min', 'max', 'const',
                  ]
    return stop_words

def get_words(code):
    words = []
    str = ""
    for w in code:
        if not w.isalpha():
            if str != "":
                words.append(str)
                str = ""
        elif w.isalpha():
            str = str + w
    if str != "":
        words.append(str)
    return words

def clean(words, stop_words):
    clean_words = []
    for w in words:
        if w not in stop_words:
            clean_words.append(w)
    return clean_words

def get_codes(all_url):
    page_number = 1
    submissions_url = []
    upper_bound = 5
    cnt = 0
    end = False
    while not end:
        cur_url = all_url + str(page_number)
        html = requests.get(cur_url)
        soup = BeautifulSoup(html.text, 'lxml')
        elems = soup.find_all("a", text = re.compile("Detail"))
        if len(elems) == 0:
            break
        for e in elems:
            suburl = e.attrs['href']
            submissions_url.append('https://beta.atcoder.jp' + suburl)
            cnt += 1
            if cnt >= upper_bound:
                end = True
                break
        page_number += 1
    codes = []
    for url in submissions_url:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        elems = soup.select("#submission-code")
        codes.append([url, elems[0].getText()])
    stop_words = get_stop_words()
    clean_codes = []
    for url_code in codes:
        words = get_words(url_code[1])
        unique_words = list(set(words))
        clean_words = clean(unique_words, stop_words)
        clean_codes.append(clean_words)
    return clean_codes

def classify(statement, codes):
    tags = ['グラフ', '数論', '幾何', '動的計画法', 'データ構造', '文字列', '確率・組合せ', 'ゲーム']
    apparent_keys = [['グラフ', '木', '連結', '辺', '頂点', 'パス',],
                     [],
                     ['半径',],
                     [],
                     [],
                     ['文字列',],
                     ['確率',],
                     ['ゲーム', 'プレイ', 'プレイヤー', '勝ち', '負け'],
                    ]
    good_keys =     [['G', 'g', 'Edge', 'edge', 'Graph', 'graph', 'cycle', 'deg', 'dfs', 'tree', 'dijkstra',],
                     ['gcd', 'lcm', 'extgcd', 'prime', 'phi',],
                     ['point', 'points', 'Point', 'Points', 'line', 'Line', 'imag', 'real', 
                      'circle', 'rad', 'EPS', 'eps', 'Convexhull', 'Intersect', 'intersect',],
                     ['dp',],
                     ['SegmentTree', 'segmenttree', 'segtree', 'seg', 'Segtree', 'Seg', 
                      'FenwickTree', 'fenwicktree', 'Fenwick', 'fenwick', 'bit', 'BIT', 'BinaryIndexedTree', 
                      'UnionFind', 'UF', 'uf', 'unite', 'same', 'unionfind', 'Unionfind',
                      'LazySegmentTree', 'lazy',
                      'update', 'build', 'query',],
                     [],
                     ['C', 'inv', 'Inv', 'fact', 'invfact', 'Fact', 'Invfact', 'choose', 'mod', 'MOD'],
                     ['grundy', 'g', 'gr', 'Alice', 'Bob', 'Takahashi', 'Aoki', 'First', 'Second',
                      'ALICE', 'BOB', 'TAKAHASHI', 'AOKI', 'Draw', 'DRAW',],
                    ]
    not_good_keys = [['gcd',],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                     [],
                    ]
    tag_list = []
    for i in range(0, len(tags)):
        ok = False
        for key in apparent_keys[i]:
            if key in statement:
                ok = True
                break
        if not ok:
            yes_cnt = 0
            no_cnt = 0
            for code in codes:
                good = False
                for key in good_keys[i]:
                    if key in code:
                        good = True
                if not good:
                    no_cnt += 1
                else:
                    for key in not_good_keys[i]:
                        if key in code:
                            good = False
                    if not good:
                        no_cnt += 1
                    else:
                        yes_cnt += 1
            if yes_cnt > no_cnt:
                ok = True
        if ok:
            tag_list.append(tags[i])

    if len(tag_list) == 0:
        tag_list.append('その他')
    return tag_list

def make_database(tag_list, type):
    for g in tag_list:
        url = g[0]
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        title = soup.find("span", class_="h2").text
        name = title[4:len(title)]
        tags = ' '.join(g[1])
        id = url[len(url) - 8:len(url) - 5].upper() + ' ' + url[len(url) - 5:len(url) - 2] + ' '
        if type == 0:
            id = id + url[len(url) - 1].upper()
        elif type == 1:
            s = url[len(url) - 1]
            if s.isdigit():
                alpha = ['#', 'A', 'B', 'C', 'D']
                id = id + alpha[int(s)]
            else:
                id = id + s.upper()
        elif type == 2:
            s = url[len(url) - 1]
            if s.isdigit():
                alpha = ['#', 'C', 'D', 'E', 'F']
                id = id + alpha[int(s)]
            else:
                id = id + s.upper()
        data = [id, name, url, tags]

        sql = sqlite3.connect('./database/problems.db')
        if type == 0:
            sql.execute("create table if not exists AGC(id, name, url, tags)")
            sql.execute("insert into AGC values(?, ?, ?, ?)", data)
        elif type == 1:
            sql.execute("create table if not exists ABC(id, name, url, tags)")
            sql.execute("insert into ABC values(?, ?, ?, ?)", data)
        elif type == 2:
            sql.execute("create table if not exists ARC(id, name, url, tags)")
            sql.execute("insert into ARC values(?, ?, ?, ?)", data)
        sql.commit()
        sql.close()

if __name__ == '__main__':
    for type in range(0, 3): #AGC:0, ABC:1, ARC:2
        if type == 1: #not work with ABC problems due to its strange URL
            continue
        all_urls = get_all_urls(type)
        url_statement_codes = [[url[0:40] + 'tasks/' + url[59:67], get_statement(url), get_codes(url)] for url in all_urls]
        tag_list = [] #[[url, [tag1, tag2, ..., ]], ...]
        for usc in url_statement_codes:
            tmp = []
            tmp.append(usc[0])
            tmp.append(classify(usc[1], usc[2]))
            tag_list.append(tmp)
        make_database(tag_list, type) 
    generator.generate()
