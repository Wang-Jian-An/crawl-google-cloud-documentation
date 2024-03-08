import os
import io
import time
import tqdm
import yaml
import random
import requests
import pandas as pd
from pprint import pprint
import bs4
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from utils.crawl_via_selenium import crawl_Chrome

base_url = "https://cloud.google.com"
with open("config.yaml", encoding = "utf-8") as f:
    config = yaml.safe_load(f)

# In[] 主程式
def main():

    """
    <Explanation TBD>
    """

    # one_url = "https://cloud.google.com/sql/docs/mysql/backup-recovery/backups#what_backups_provide"
    for one_url in config["url"]:
        try:
            each_document = crawl_side_list(one_url = one_url)

            for one_document in tqdm.tqdm(each_document):
    
                text_result = crawl_main_content(one_main_url = one_url)
                store_text(
                    cloud = "gcloud",
                    file_name = "About Cloud SQL backups".replace("/", "_"),
                    text = text_result
                )
                time.sleep(random.random())
                print(one_document)
        except: 
            print(one_url)
    return 

# In[] 共用函式
def request_and_decode_html(
    one_url
):
    
    req_text = requests.get(one_url)
    req_text = BeautifulSoup(req_text.text, "html.parser")
    return req_text

# In[] 左側列表
def crawl_side_list(
    one_url: str
):

    """
    <Explanation TBD>
    """

    req_text = request_and_decode_html(one_url = one_url)
    left_side_list = req_text.find("ul", {"class": "devsite-nav-list", "menu": "_book"})
    left_side_list = left_side_list.find_all("a", {"class": "devsite-nav-title gc-analytics-event"})

    left_side_list_href = [
        base_url + i.get("href")
        for i in left_side_list
    ]
    left_side_list_name = [
        i.find("span").text 
        for i in left_side_list
    ]
    return [
        {
            "name": name,
            "href": href
        }
        for name, href in zip(
            left_side_list_name,
            left_side_list_href
        )
    ]

# In[] 主要內容
@crawl_Chrome
def crawl_main_content(
    driver, 
    one_main_url: str
):
    
    """
    <Explanation TBD>
    """
    
    def get_content(
        html_text
    ):

        if html_text.name == "h2":
            response = "## " + html_text.get_text()
        elif html_text.name == "h3":
            response = "### " + html_text.get_text()
        elif html_text.name == "div":
            if "ds-selector-tabs" in html_text.get("class"):
                html_text = html_text.find_all("section")
                response = "\n".join(
                    [
                        get_content(html_text = j)
                        for i in html_text for j in i.children if not(isinstance(j, bs4.element.NavigableString))
                    ]
                )
            else:
                html_text = html_text.find("div")
                if html_text:
                    if html_text.name == "table":
                        response = pd.read_html(io.StringIO(html_text))
                        response = response.to_markdown(index = None)
                    else:
                        response = html_text.get_text()
                else:
                    response = ""
        elif html_text.name == "table":
            response = pd.read_html(str(html_text))[0]
            response = response.to_markdown(index = None)
        elif html_text.name == "aside":
            response = ""

        elif html_text.name == "pre":
            response = "```\n{}\n```".format(html_text.get_text())
        else:
            response = html_text.get_text()
        return response.rstrip().lstrip()

    driver.get(one_main_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    req_text = driver.find_element(By.CLASS_NAME, "devsite-article")
    req_text = req_text.get_attribute("outerHTML")
    req_text = BeautifulSoup(req_text, "html.parser")
    h1_title = req_text.find("h1").text

    req_text = req_text.find("div", {"class": "devsite-article-body clearfix".split(" ")})

    text_result = [
        get_content(
            html_text = i
        )
        for i in req_text.children if not(isinstance(i, bs4.element.NavigableString)) and not(i is None)
    ]
    text_result = "\n".join(text_result).replace("##", "\n##").replace("###", "\n###").replace("###", "\n###").rstrip().lstrip()
    return "# " + h1_title + "\n" + text_result

one_url = "https://cloud.google.com/sql/docs/sqlserver/connect-instance-cloud-shell#gcloud"
print(crawl_main_content(one_main_url = one_url))

# In[] 檔案儲存
def store_text(
    cloud: str, 
    file_name: str,
    text: str
):
    
    """
    <Explanation TBD>
    """

    assert cloud in ["gcloud", "azure"], "There are two cloud provider, including 'gcloud' and 'azure'. "
    if cloud == "gcloud":
        data_path = config["gcloud_data_path"]
    elif cloud == "azure":
        pass

    with open(os.path.join(data_path, f"{file_name}.txt"), "w") as f:
        f.write(text)
    return 

# In[] 程式執行
if __name__ == "__main__":
    main()