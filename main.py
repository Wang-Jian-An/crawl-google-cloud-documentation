import os
import yaml
import requests
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

    # req_text = requests.get(one_url)
    # req_text = BeautifulSoup(req_text.text, "html.parser")
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
    return left_side_list_name, left_side_list_href

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
    left_side_list_name, left_side_list_href = crawl_side_list(one_url = one_url)

    for one_main_name, one_main_url in zip(
        left_side_list_name, 
        left_side_list_href
    ):
        text_result = crawl_main_content(one_main_url = one_main_url)
        store_text(
            cloud = "gcloud",
            file_name = one_main_name,
            text = text_result
        )
    return 


# In[] 程式執行
if __name__ == "__main__":
    main()