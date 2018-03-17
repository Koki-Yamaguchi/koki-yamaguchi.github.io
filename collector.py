import requests, json
from bs4 import BeautifulSoup

def collect():
    '''
    html = requests.get('https://raw.githubusercontent.com/kenkoooo/AtCoderProblems/master/atcoder-problems-frontend/resources/ac.json')
    soup = BeautifulSoup(html.text, 'lxml')
    json_data_tmp = soup.find("p").string
    with open('./json/user_list.json', mode = 'w', encoding = 'utf-8') as file:
        file.write(json_data_tmp)
    '''
    json_data = open('./json/user_list.json', 'r')
    users = []
    json_dict = json.load(json_data)
    for data in json_dict:
        users.append(data['user_id'])

    first = 380
    for i in range(first, len(users)):
        #check if this user is Japanese
        url = 'https://beta.atcoder.jp/ranking?f.Country=&f.UserScreenName=' + users[i]
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        elems = soup.find("table", class_="table-bordered") 
        img = elems.find("img")
        if (img == None):
            print("NOT VALID")
            continue
        if img.prettify()[-10:-8] == 'JP':
            print("JAPANESE :", users[i])
            url = 'http://kenkoooo.com/atcoder/atcoder-api/results?user=' + users[i]
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'lxml')
            data = soup.find("p").string
            if data != None:
                with open('./json/users/' + users[i] + '.json', mode = 'w', encoding = 'utf-8') as file:
                    file.write(data)
                print(url, i, len(users))
        else:
            print("COUNTRY :", img.prettify()[-10:-8])

if __name__ == '__main__':
    collect()
