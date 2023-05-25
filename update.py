import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

os.system("mode con cols=130 lines=4")

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
headers = {
    'User-Agent': user_agent
}


def get_hero():
    hero_name = []
    hero_links = []
    url = 'https://www.dotabuff.com/heroes'
    response = requests.get(url, headers=headers, timeout=5)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    links_temp = soup.select(".hero-grid a[href]")

    for link in links_temp:
        hero_links.append(link["href"])

    for name in soup.find_all(class_="name"):
        hero_name.append(name.text.strip())
    
    return hero_name, hero_links

def scrape_hero(hero, link):
    url = 'https://www.dotabuff.com'+link+'/counters'
    response = requests.get(url, headers=headers, timeout=5)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    data = []
    for tr in soup.find_all('tr'):
        hero_name_elem = tr.find('td', {'class': 'cell-xlarge'})
        if hero_name_elem:
            hero_name = hero_name_elem.find('a').text
            score = float(tr.find_all('td')[2].text.strip('%'))
            win_rate = float(tr.find_all('td')[3].text.strip('%'))
            data.append((score, hero_name, win_rate))

    for i in range(len(data)):
        score, hero_name, win_rate = data[i]
        score = -score
        data[i] = (score, hero_name, win_rate)

    min_score = min([x[0] for x in data])

    for i in range(len(data)):
        score, hero_name, win_rate = data[i]
        score += -min_score
        data[i] = (score, hero_name, win_rate)

    
    with open(f'database/{hero}.txt', 'w') as f:
        for win_rate, hero_name, score in data:
            f.write(f'{hero_name}: {score:.2f}, {win_rate}\n')

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    hero_names, links = get_hero()
    with open("database/Heroes.txt", "w") as file:
        for item in hero_names:
            file.write(item + "\n")
    total = len(links)
    count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        for link in links:
            executor.submit(scrape_hero, hero_names[count], link)
            os.system("cls")
            print('by Rizeru')
            count += 1
            progress = int(count / total * 100)
            bar = '[' + '#' * progress + ' ' * (100 - progress) + ']'
            print(f'Progress: {bar} {progress}% ({count}/{total})')
            if count == total:
                print('Recording...')
