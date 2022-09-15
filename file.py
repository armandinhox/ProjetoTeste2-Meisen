import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha


class Main:
    def __init__(self, CNPJ):
        opt = webdriver.ChromeOptions()
        # opt.add_argument('--headless')
        self.drive = webdriver.Chrome(options=opt)
        self.drive.get('http://www.sintegra.fazenda.pr.gov.br/sintegra/')
        self.solver = TwoCaptcha('29384ed19a19010816949d3034c67c39')
        self.cnpj = CNPJ

    def decp(self):
        try:
            el = WebDriverWait(self.drive, 120).until(
                lambda x: x.find_element(By.XPATH, '/html/body/center/div/form/table/tbody/tr[5]/td[2]/input'))
            self.drive.execute_script(
                """document.getElementById("imgSintegra").src = '/sintegra/captcha'+ '?' + Math.random() * 2;""")
            time.sleep(0.001)
            gg = self.drive.find_element(By.ID, 'imgSintegra')
            result = self.solver.normal(gg.screenshot_as_base64)
            el.send_keys(result['code'])
        except TimeoutException:
            return self.q()

    def find(self):
        self.decp()

        cnp = self.drive.find_element(By.ID, 'Sintegra1Cnpj')
        cnp.send_keys(self.cnpj)
        butt = self.drive.find_element(By.ID, 'empresa')
        butt.click()
        try:
            self.drive.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[3]/td[1]')
            return self.q()
        except NoSuchElementException:
            pass

    def getContent(self):
        try:
            WebDriverWait(self.drive, 120).until(lambda x: x.find_element(By.NAME, 'data[Sintegra1][campoAnterior]'))
            page = self.drive.page_source
            model = BeautifulSoup(page, features='html.parser')
            values = {}
            for td in model.find_all('table', class_='form_tabela_consulta'):
                cnt = td.findChildren('td', class_='form_conteudo')
                lbs = td.findChildren("td", class_='form_label')
                for i, j in zip(lbs, cnt):
                    values[i.text[:-1]] = j.text.strip()

            with open("data.json", "w", encoding='utf8') as fil:
                values.popitem()
                json.dump(values, fil, ensure_ascii=False, indent=4)
                print(json.dumps(values, ensure_ascii=False, indent=4))
        except UnexpectedAlertPresentException:
            print('INVALID CNPJ')
            alert = self.drive.switch_to.alert
            alert.accept()
            return self.q()
        except InvalidSessionIdException:
            print('INVALID CAPTCHA')
            self.find()

    def q(self):
        return self.drive.close()


if __name__ == '__main__':
    ses = Main('00.776.574/0001-56')
    ses.find()
    ses.getContent()
    ses.q()
