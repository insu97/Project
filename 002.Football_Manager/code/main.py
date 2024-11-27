# selenium의 webdriver를 사용하기 위한 import
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 헤드리스 모드
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--verbose")

from selenium.webdriver.chrome.service import Service
# ChromeDriver 서비스 설정
service = Service(service_args=["--verbose", "--log-path=chromedriver.log"])

prefs = {
    "profile.managed_default_content_settings.javascript": 2  # JavaScript 비활성화
}
options.add_experimental_option("prefs", prefs)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# selenium으로 키를 조작하기 위한 import
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time
import pandas as pd
from multiprocessing import Pool

player_info_cols = ["Name", "Club", "Country", "Position(s)", "Foot", "Height", "Weight", "Wages"]

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

field_player_df = pd.DataFrame(columns=player_info_cols + field_player_cols)
goalkeeper_df = pd.DataFrame(columns=player_info_cols + goalkeeper_cols)

def scrape_player_data(start, end):
    print(start, end)
    # 크롬드라이버 실행
    driver = webdriver.Chrome(service=service, options=options) # driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)  # 최대 20초 대기

    try:

        # 크롬 드라이버에 url 주소 넣고 실행
        driver.get('https://fminside.net/players')

        # JavaScript로 광고 숨기기
        driver.execute_script("""
                document.querySelectorAll('*[id]').forEach(element => {
                    if (/^google_ads_iframe/.test(element.id)) {
                        element.remove();
                    }
                });
            """)

        # 페이지가 완전히 로딩되도록 3초동안 기다림
        time.sleep(3)

        for i in range(start, end):

            while True:
                try:
                    element = driver.find_element(By.XPATH, f'//*[@id="player_table"]/div/div[3]/ul[{i}]/li[3]/span[2]/b/a')
                    break  # 요소가 발견되면 반복 종료
                except:
                    # 요소가 없으면 "Load data" 클릭
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="player_table"]/div/div[3]/a')))
                    element.click()

                    # driver.find_element(By.XPATH, '//*[@id="player_table"]/div/div[3]/a').click()
                    # time.sleep(3)
            try:
                element = driver.find_element(By.XPATH, '//*[@id="player_table"]/div/div[3]/ul[%s]/li[3]/span[2]/b/a' % i)
            except:
                print(1)

            try:
                ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
            except:
                print(2)

            try:
                driver.switch_to.window(driver.window_handles[1])  # 새 창 전환
            except:
                print(3)

            time.sleep(1)

            player_data = []

            # data get

            ## player_info
            Name = driver.find_element(By.XPATH, '//*[@id="player"]/div[2]/ul/li[1]/span[2]')
            Club = driver.find_element(By.XPATH, '//*[@id="player"]/div[1]/div/ul/li[1]/a/span[2]')
            Country = driver.find_element(By.XPATH, '//*[@id="player"]/div[1]/div/ul/li[2]/span/a')
            Position = driver.find_element(By.XPATH, '//*[@id="player"]/div[2]/ul/li[3]/span[2]')
            Foot = driver.find_element(By.XPATH, '//*[@id="player"]/div[2]/ul/li[4]/span[2]')
            Height = driver.find_element(By.XPATH, '//*[@id="player"]/div[2]/ul/li[5]/span[2]')
            Weight = driver.find_element(By.XPATH, '//*[@id="player"]/div[2]/ul/li[6]/span[2]')
            Wages = driver.find_element(By.XPATH, '//*[@id="player"]/div[3]/ul/li[3]/span[2]')
            player_data.extend(
                [Name.text, Club.text, Country.text, Position.text, Foot.text, Height.text, Weight.text, Wages.text])

            try:
                ## field_player_Attributes
                for fp in field_player_cols:
                    player_data.append(driver.find_element(By.XPATH, '//*[@id="%s"]/td[2]' % fp).text)

                field_player_df.loc[len(field_player_df), :] = player_data
            except:
                for gk in goalkeeper_cols:
                    player_data.append(driver.find_element(By.XPATH, '//*[@id="%s"]/td[2]' % gk).text)

                goalkeeper_df.loc[len(goalkeeper_df), :] = player_data

            driver.close()

            driver.switch_to.window(driver.window_handles[0])

            time.sleep(1)
    except Exception as e:
        print(f'Error Occurred: {e}')
    finally:
        driver.quit()

    return field_player_df, goalkeeper_df

def process_range(range_pair):
    """
    병렬 프로세스에서 실행할 함수. scrape_player_data를 호출합니다.
    """
    return scrape_player_data(range_pair[0], range_pair[1])

def main():
    total_players = 80
    chunk_size = 20
    ranges = [(i, min(i + chunk_size, total_players)) for i in range(1, total_players, chunk_size)]

    with Pool(processes=4) as pool:
        results = pool.map(process_range, ranges)

    field_player_data = pd.concat([res[0] for res in results if res[0] is not None], ignore_index=True)
    goalkeeper_data = pd.concat([res[1] for res in results if res[1] is not None], ignore_index=True)

    field_player_data.to_csv("../data/FM2024_field_player_info.csv", index=False, encoding='utf-8')
    goalkeeper_data.to_csv("../data/FM2024_goalkeeper_info.csv", index=False, encoding='utf-8')

if __name__ == "__main__":
    main()