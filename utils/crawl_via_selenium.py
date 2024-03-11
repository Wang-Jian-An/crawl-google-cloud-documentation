from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--start-maximized")

def crawl_Chrome(func):

    """
    <Explanation TBD>
    """

    def deco(**kwargs):

        with webdriver.Chrome(
            service = Service(ChromeDriverManager().install()),
            options = options
        ) as driver:
            crawl_result = func(driver, **kwargs)
        return crawl_result
    return deco
