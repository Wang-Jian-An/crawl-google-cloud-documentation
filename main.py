import os
import io
import json
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
from monitor.folder import folder_exists

base_url = "https://cloud.google.com"
with open("config.yaml", encoding = "utf-8") as f:
    config = yaml.safe_load(f)

# In[] 主程式
def main():

    """
    <Explanation TBD>
    """

    # one_url = "https://cloud.google.com/sql/docs/mysql/backup-recovery/backups#what_backups_provide"
    link_map_title_dict = dict()
    error_content_dict = dict()
    error_aside_dict = dict()
    for one_url in config["url"]:
        try:
            each_document = crawl_side_list(one_url = one_url)

            with tqdm.tqdm(each_document) as t:
                for one_document in t:
                    try:
                        guide, title, text_result = crawl_main_content(one_main_url = one_document["href"])
                        json_content = text_preprocessing(
                            title = title,
                            text = text_result,
                            link = one_document["href"]
                        )
                        json_content.update(
                            guide = guide
                        )
                        store_text(
                            folder_path = "./Google-Cloud-Platform-Document/{}".format(
                                guide
                            ),
                            file_name = "{}.json".format(title.replace("/", "_")),
                            text = json_content
                        )

                        link_map_title_dict[one_document["href"]] = title
                        store_text(
                            folder_path = "./",
                            file_name = "link_map_title.json",
                            text = link_map_title_dict
                        )
                        time.sleep(random.random())
                    except Exception as e:
                        error_content_dict[one_document["name"]] = {
                            "href": one_document["href"],
                            "error": e.__str__()
                        }
                        store_text(
                            folder_path = "./",
                            file_name = "error_message.json",
                            text = error_content_dict
                        )
        except Exception as e: 
            error_aside_dict[one_url] = e.__str__()
            store_text(
                folder_path = "./",
                file_name = "error_aside_message.json",
                text = error_aside_dict
            )            
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

# In[] 爬取主要內容
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

        if html_text.name:
            if html_text.name == "h1":
                response = "# " + html_text.get_text()

            elif html_text.name == "h2":
                response = "\n## " + html_text.get_text() + "\n\n"

            elif html_text.name == "h3":
                response = "\n### " + html_text.get_text() + "\n\n"

            elif html_text.name == "table":
                response = pd.read_html(io.StringIO(str(html_text)))[0]
                response = response.to_markdown(index = None)

            elif html_text.name in ["ul", "ol"]:
                response = "".join(
                    [
                        "\n\n- " + get_content(html_text = i) + "\n"
                        for i in html_text.children
                    ]
                )

            elif html_text.name in ["section"]:
                response = "\n".join(
                    [
                        get_content(html_text = i)
                        for i in html_text.children
                    ]
                )

            elif html_text.name == "devsite-selector":
                response = "\n".join(
                    get_content(html_text = i)
                    for i in html_text.children 
                    if not(i.name == "devsite-tabs")
                )

            elif html_text.name == "devsite-hats-survey":
                response = ""

            elif html_text.name == "pre":
                response = "```\n{}\n```".format(html_text.get_text())

            elif html_text.name == "li":
                response = "".join(
                    [
                        get_content(html_text = i)
                        for i in html_text.children
                    ]
                )

            elif html_text.name == "a":
                response = "  [{}]({})  ".format(
                    html_text.get_text().replace("\n", ""),
                    html_text.get("href")
                )

            elif html_text.name == "b" or html_text.name == "strong":
                response = " **" + html_text.get_text() + "** "

            elif html_text.name in ["div", "aside", "devsite-code"]:
                if html_text.attrs:
                    if "class" in html_text.attrs.keys():
                        class_value = html_text.attrs["class"]
                        if "nocontent" in class_value:
                            return ""

                response = "".join(
                    [
                        get_content(html_text = i)
                        for i in html_text.children 
                    ]
                )

            elif html_text.name in ["code"]:
                response = " ".join(
                    [
                        "`" + get_content(html_text = i) + "`"
                        for i in html_text.children
                    ]
                )

            elif html_text.name in ["p", "span"]:
                response = " ".join(
                    [
                        get_content(html_text = i).replace("\n", "")
                        for i in html_text.children 
                    ]
                )

            else:
                response = ""

        else:
            if html_text.replace("\n", "").rstrip().lstrip() == "################ Command Line ################":
                response = ""
            
            else:
                response = html_text[:].replace("\n", " ").rstrip().lstrip()
        return response

    driver.get(one_main_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    req_text = driver.find_element(By.CLASS_NAME, "devsite-article")
    req_text = req_text.get_attribute("outerHTML")
    req_text = BeautifulSoup(req_text, "html.parser")

    guide_page = req_text.find("div", {"class": "devsite-article-meta nocontent".split(" ")})
    guide_page = guide_page.find("ul", {"class": "devsite-breadcrumb-list"})
    guide_page = [i.get_text() for i in guide_page.children if not(i == "\n")]
    guide_page = [i.replace("\n", "").replace("$", "").replace("'", "").lstrip().rstrip() for i in guide_page if not(i.replace("\n", "").lstrip().rstrip() in ["Home", "Technology areas"])][0]


    h1_title = "{} - {}".format(
        guide_page, 
        req_text.find("h1").get_text().replace("\n", "").lstrip().rstrip()
    )

    req_text = req_text.find("div", {"class": "devsite-article-body clearfix".split(" ")})

    text_result = "\n".join([
        get_content(
            html_text = i
        ).lstrip().rstrip()
        for i in req_text.children if not(isinstance(i, bs4.element.NavigableString)) and not(i is None)
    ])
    replace_pairs = [
        ("- \n", ""),
        ("-\n", ""), 
        ("##", "\n##"),
        ("###", "\n###"), 
        ("[\n", "["), 
        ("\n\n\n\n\n\n", ""),
        ("\n\n\n\n", ""), 
        ("\n\n\n", "\n"), 
        ("\n\n", "\n"), 
        ("  ", " "), 
        ("  ", " ")
    ]

    for one_pair in replace_pairs:
        text_result = text_result.replace(one_pair[0], one_pair[1])
    return (
        guide_page, 
        h1_title, 
        "# " + h1_title + "\n" + text_result.rstrip().lstrip()
    )

# In[] 主要內容前處理
def text_preprocessing(
    title: str, 
    text: str,
    link: str
):
    
    """
    
    """

    # Get abstract and real content
    first_h2 = text.find("## ")
    abstract = text[:first_h2]
    real_content = text[first_h2:]
    return {
        "title": title,
        "url": link,
        "abstract": abstract,
        "content": real_content
    }

# In[] 檔案儲存
@folder_exists
def store_text(
    folder_path: str, 
    file_name: str,
    text: str | dict
):
    
    """
    <Explanation TBD>
    """

    with open(os.path.join(folder_path, file_name), "w") as f:
        if file_name[-4:] == ".txt":
            f.write(text)
        elif file_name[-5:] == ".json":
            json.dump(text, f)
    return 

# In[] 程式執行
if __name__ == "__main__":
    main()