import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium.webdriver.common.keys import Keys

# DataFrame 정의
player_info_cols = ['Name', 'Age', 'Position(s)', 'Foot', 'Height', 'Weight', 'Club', 'Wages']

field_player_cols = [
    'corners', 'crossing', 'dribbling', 'finishing', 'first-touch', 'free-kick-taking', 'heading', 'long-shots',
    'long-throws', 'marking', 'passing', 'penalty-taking', 'tackling', 'technique', 'aggression', 'anticipation', 'bravery',
    'composure', 'concentration', 'decisions', 'determination', 'flair', 'leadership', 'off-the-ball', 'positioning',
    'teamwork', 'vision', 'work-rate', 'acceleration', 'agility', 'balance', 'jumping-reach', 'natural-fitness', 'pace',
    'stamina', 'strength'
]

goalkeeper_cols = [
    'aerial-reach', 'command-of-area', 'communication', 'eccentricity', 'first-touch', 'handling', 'kicking',
    'one-on-ones', 'passing', 'punching-tendency', 'reflexes', 'rushing-out-tendency', 'throwing','aggression',
    'anticipation', 'bravery', 'composure', 'concentration', 'decisions', 'determination', 'flair', 'leadership',
    'off-the-ball', 'positioning', 'teamwork', 'vision', 'work-rate', 'acceleration', 'agility', 'balance',
    'jumping-reach','natural-fitness', 'pace', 'stamina', 'strength', 'free-kick-taking', 'penalty-taking', 'technique'
]

field_player_df = pd.DataFrame(columns = player_info_cols + field_player_cols)
goalkeeper_df = pd.DataFrame(columns = player_info_cols + goalkeeper_cols)

# 크롤링 시작
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 헤드리스 모드

driver = webdriver.Chrome(options=options)
driver.get('https://fminside.net/')
driver.implicitly_wait(20)

driver.find_element(By.XPATH, '//*[@id="menu"]/ul[2]/li[3]/a').click()
driver.implicitly_wait(20)

for i in tqdm(range(1, 101)):
    while True:
        try:
            driver.find_element(By.XPATH, f'//*[@id="player_table"]/div/div[3]/ul[{i}]/li[3]/span[2]/b/a').send_keys(
                Keys.CONTROL + Keys.ENTER)
            break
        except:
            driver.find_element(By.XPATH, '//*[@id="player_table"]/div/div[3]/a').click()
            driver.implicitly_wait(10)

    driver.switch_to.window(driver.window_handles[-1])
    driver.implicitly_wait(20)

    info_url = driver.current_url
    info_req = Request(info_url, headers={'User-Agent': 'Mozilla/5.0'})
    info_html = urlopen(info_req).read()
    bs_obj = BeautifulSoup(info_html, 'html.parser')

    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

    pi_data = []

    # player_info 공통된 컬럼
    player_info_table = bs_obj.select('#player > div:nth-child(2) > ul')

    for i in range(1, 7):
        pi_data.append(player_info_table[0].select(f'li:nth-child({i}) > span.value')[0].text)

    player_contract_table = bs_obj.select('#player > div:nth-child(3) > ul')

    pi_data.append(player_contract_table[0].select(f'li:nth-child({1}) > span.value')[0].text)
    pi_data.append(player_contract_table[0].select(f'li:nth-child({3}) > span.value')[0].text)

    def field_player():
        # field_player_info
        fp_data = []

        player_stats_table = bs_obj.select('#player_stats')[0]

        technical_info = player_stats_table.select('div:nth-child(3) > table > tr > td')

        for i in range(1, len(technical_info), 2):
            fp_data.append(technical_info[i].text)

        mental_info = player_stats_table.select('div:nth-child(4) > table > tr > td')

        for i in range(1, len(mental_info), 2):
            fp_data.append(mental_info[i].text)

        physical_info = player_stats_table.select('div:nth-child(5) > table > tr > td')

        for i in range(1, len(physical_info), 2):
            fp_data.append(physical_info[i].text)

        return fp_data

    def goalkeeper():
        # goalkeeper_info
        gk_data = []

        player_stats_table = bs_obj.select('#player_stats')[0]

        goalkeeping_info = player_stats_table.select('div:nth-child(3) > table > tr > td')

        for i in range(1, len(goalkeeping_info), 2):
            gk_data.append(goalkeeping_info[i].text)

        mental_info = player_stats_table.select('div:nth-child(4) > table > tr > td')

        for i in range(1, len(mental_info), 2):
            gk_data.append(mental_info[i].text)

        physical_info = player_stats_table.select('div:nth-child(5) > table > tr > td')

        for i in range(1, len(physical_info), 2):
            gk_data.append(physical_info[i].text)

        return gk_data

    if pi_data[2] == 'GKGK':
        gk_data = goalkeeper()
        goalkeeper_df.loc[len(goalkeeper_df)] = pi_data + gk_data
    else:
        fp_data = field_player()
        field_player_df.loc[len(field_player_df)] = pi_data + fp_data

field_player_df.to_csv("../data/FM2024_field_player_info.csv", index=False, encoding='utf-8')
goalkeeper_df.to_csv("../data/FM2024_goalkeeper_info.csv", index=False, encoding='utf-8')

driver.quit()