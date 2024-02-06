import os
import yaml
import requests
import itertools
import bs4
from pprint import pprint
from bs4 import BeautifulSoup

base_url = "https://cloud.google.com"
with open("config.yaml", encoding = "utf-8") as f:
    config = yaml.safe_load(f)

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

    def crawl_item(
        html_text
    ):
        
        if "devsite-nav-heading" in html_text.get("class"):
            return []
        elif "devsite-nav-expandable" in html_text.get("class"):
            html_text = html_text.find("ul", {"class": "devsite-nav-section"})
            return [
                crawl_item(html_text = i) for i in html_text.children
            ]
        else:
            html_text = html_text.find("a")
            href = html_text.get("href")
            item_name = html_text.find("span").text
            return {
                "name": item_name,
                "href": href
            }

    req_text = request_and_decode_html(one_url = one_url)
    left_side_list = req_text.find("ul", {"class": "devsite-nav-list", "menu": "_book"})

    left_side = [
        crawl_item(
            html_text = i
        )
        for i in left_side_list.children
        if not(isinstance(i, bs4.element.NavigableString))
    ]
    
    final_left_side = list()
    for i in left_side:
        if type(i) == dict:
            final_left_side.append(i)
        elif type(i) == list:
            if i.__len__() == 1:
                i = i[0].copy()
            for j in i:
                if type(j) == dict:
                    final_left_side.append(j)
                else:
                    if i.__len__() == 1:
                        i = i[0].copy()
                    for k in j:
                        final_left_side.append(k)
    return final_left_side

# In[] 主要內容
def crawl_main_content(
    one_main_url: str
):
    
    """
    <Explanation TBD>
    """
    
    # req_text = requests.get(one_main_url)
    # req_text = BeautifulSoup(req_text.text, "html.parser")
    req_text = request_and_decode_html(one_url = one_main_url)
    req_text = req_text.find(
        "article", 
        {
            "class": "devsite-article"
        }
    )
    h1_title = req_text.find("h1").text

    req_text = req_text.find("div", "devsite-article-body clearfix")

    text_result = list()
    for child in req_text.children:
        if child.name:
            if child.name == "p":
                paragraph_text = child.get_text().replace("\n", " ")
                text_result.append(paragraph_text)
            elif child.name == "h2":
                h2_title = child.get_text()
                if "What's next" in h2_title:
                    break
                text_result.append(h2_title)
            elif child.name == "ul":
                ul_text = "\n".join(["- {}".format(i.get_text().replace("\n      ", "").replace("\n", " ")) for i in child.find_all("li")])
                text_result.append(ul_text)
    text_result = "\n".join(text_result).replace("\n\n", "\n")
    return h1_title + "\n" + text_result

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

    with open(os.path.join(data_path, file_name), "w") as f:
        f.write(text)
    return 

# In[] 主程式
def main():

    """
    <Explanation TBD>
    """

    one_url = config["url"][1]
    left_side = crawl_side_list(one_url = one_url)
    # pprint(left_side)

    # for one_main_name, one_main_url in zip(
    #     left_side_list_name, 
    #     left_side_list_href
    # ):
    #     text_result = crawl_main_content(one_main_url = one_main_url)
    #     store_text(
    #         cloud = "gcloud",
    #         file_name = one_main_name,
    #         text = text_result
    #     )
    return 


# In[] 程式執行
if __name__ == "__main__":
    main()