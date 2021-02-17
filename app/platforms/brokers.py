from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

import os

from datetime import datetime
from bs4 import BeautifulSoup


class BaseScraper:

    def __init__(self, headless=True, suppress_logs=True):
        self.suppress_logs = suppress_logs
        self.headless = headless
        self.driver = self.initialise_selenium()

    def initialise_selenium(self):
        caps = DesiredCapabilities.CHROME
        chrome_options = Options()

        if self.suppress_logs:
            chrome_options.add_argument("--log-level=3")

        if self.headless:
            chrome_options.add_argument('--headless')

        d = uc.Chrome(options=chrome_options, desired_capabilities=caps)

        # d = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
        return d

    def get_by_xpath_element_when_ready(self, xpath, delay=5, *args, **kwargs):
        try:
            return WebDriverWait(self.driver, delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            raise TimeoutException('Unable to find element specified by xpath: {xpath}'.format(xpath=xpath))

    def login(self):
        raise NotImplementedError


class Trading212(BaseScraper):

    login_url = 'https://www.trading212.com/en/login'
    username_input_id = 'username-real'
    password_input_id = 'pass-real'
    login_button_xpath = '//input[@class="button-login"]'
    onboarding_popup_close_xpath = '//div[contains(@class,"eq-onboarding")]//div[@class="close-icon"]'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def login(self):
        
        self.driver.get(self.login_url)

        username_field = self.driver.find_element_by_id(self.username_input_id)
        username_field.send_keys(os.environ['TRADING212_USER'])

        password_field = self.driver.find_element_by_id(self.password_input_id)
        password_field.send_keys(os.environ['TRADING212_PASS'])

        login_button = self.driver.find_element_by_xpath(self.login_button_xpath)
        login_button.click()

        onboarding_close_button = self.get_by_xpath_element_when_ready(self.onboarding_popup_close_xpath, delay=10)
        onboarding_close_button.click()

        return True
        
    def get_owned(self):

        self.get_by_xpath_element_when_ready('//tbody[@class="table-body"]//tr')
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        output = []
        positions = soup.find("div", {"id": "positionsTable"}).findAll("tr")
        for stock in positions:
            vals = stock.findAll("td")
            if len(vals) == 0:
                continue            
            output.append({
                'symbol': vals[0].text.strip(),
                'shares_owned': float(vals[2].text),
                'value_purchased_at': float(vals[3].text),
                'date_purchased': datetime.strptime(vals[6].text, '%d.%m.%Y %H:%M:%S'),
            })
        return output


class EToro(BaseScraper):

    login_url = 'https://www.etoro.com/login'
    portfolio_url = 'https://www.etoro.com/portfolio'
    username_input_id = 'username'
    password_input_id = 'password'
    login_button_xpath = '//button[@automation-id="login-sts-btn-sign-in"]'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def login(self):
        
        self.driver.get(self.login_url)

        username_field = self.driver.find_element_by_id(self.username_input_id)
        username_field.send_keys(os.environ['ETORO_USER'])

        password_field = self.driver.find_element_by_id(self.password_input_id)
        password_field.send_keys(os.environ['ETORO_PASS'])
        
        login_button = self.driver.find_element_by_xpath(self.login_button_xpath)
        login_button.click()

        try:
            popup_button = self.get_by_xpath_element_when_ready('//div[@automation-id="success-stories-notification-btn-dismiss"]', delay=5)
            popup_button.click()
        except TimeoutException:
            pass


        return True

    def _navigate_to_portfolio(self):
        self.driver.get(self.portfolio_url)

    def get_owned(self):

        self._navigate_to_portfolio()
        positions_xpath = '//*[contains(@data-etoro-automation-id, "portfolio-overview-row")]'
        
        output = []
        self.get_by_xpath_element_when_ready(positions_xpath)
        positions = self.driver.find_elements_by_xpath(positions_xpath)
        for p in positions:
            ticker = p.find_element_by_xpath('.//div[@data-etoro-automation-id="portfolio-overview-table-body-cell-market-name"]').text
            vals = p.find_elements_by_xpath('.//ui-table-cell')
            output.append({
                'symbol': ticker,
                'shares_owned': float(vals[0].text.split('\n')[0]),
                'value_purchased_at': float(vals[1].text),
            })
        return output
            

if __name__ == '__main__':

    positions = dict()

    e = EToro(headless=False)
    login_success = e.login()
    if login_success:
        positions['eToro'] = e.get_owned()

    t = Trading212(headless=True)
    login_success = t.login()
    if login_success:
        positions['Trading 212'] = t.get_owned()
    

    for platform, data in positions.items():
        for position in data:
            s = Stock.objects.get(pk=position['symbol'])
            O = 0

    # @transaction.atomic
    # def update_teams():

    #     stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    #     shares_owned = models.FloatField()
    #     value_purchased_at = models.FloatField()
        
    #     for p in positions:
    #         Owned.objects.create(
    #             team_id=t['id'],
    #             defaults={
    #                 'team_code': t['code'],
    #                 'team_name': t['name'],
    #                 'team_name_short': t['short_name'],
    #             }
    #         )



    w = 0