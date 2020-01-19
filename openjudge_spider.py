import requests
from bs4 import BeautifulSoup
import json
import re
import base64

proxies = {"http": "Your proxy here", "https": "Your proxy here"}
use_proxy = False
# Use proxy may help to accerate downloading images.


def single_img_to_b64(urlin):
    prev_urlin = urlin
    retry_count = 0
    while True:
        try:
            if retry_count > 5:
                print("Max retry count reached. Skipping...")
                retry_count += 1
                return ""
            urlin = urlin.group()
            urlin = urlin.split("src=\\\"")[1].split("\\\"")[0]
            if (not bool(re.match("http://", urlin))) and (not (bool(re.match("https://", urlin)))):
                print(
                    "This image is invalid, and it is not a bug of this application, it's a bug of openjudge. "
                    "URL: %s" % urlin)
                return ""
            print("Fetching: " + urlin)
            if use_proxy:
                r = requests.get(urlin, proxies=proxies).content
            else:
                r = requests.get(urlin).content
            retry_count = 0
            return "src=\\\"data:image/png;base64," + base64.b64encode(r).decode("utf-8") + "\\\""
        except Exception as Ex:
            print(Ex)
            urlin = prev_urlin
            retry_count += 1
            continue


def img_to_b64():
    filing = open("result.json", "r", encoding="utf-8")
    string_obj = str(filing.read())
    filing.close()
    string_obj = re.sub(r"src=\\\"[\w.:/]+\\\"", single_img_to_b64, string_obj)
    filing = open("result.json", "w", encoding="utf-8")
    filing.write(string_obj)
    filing.close()


def exercise_page_detector(url):
    while True:
        try:
            if use_proxy:
                datareceived = BeautifulSoup(requests.get(url, proxies=proxies).text, "lxml")
            else:
                datareceived = BeautifulSoup(requests.get(url).text, "lxml")
            break
        except Exception as Ex:
            continue
    json_string_generate = {}
    for i in datareceived.find_all("div"):
        if i.get("id") == "pageTitle":
            json_string_generate["title"] = str(i.h2.string)
        if i.get("class") == ["problem-page", "col-9"]:
            for z in i.find_all("dl"):
                if z.get("class") == ["problem-params"]:
                    for m in z.find_all("dt"):
                        if str(m.string) == "总时间限制: ":
                            json_string_generate["total_time_limit"] = str(m.next_sibling.next_sibling.string)
                        if str(m.string) == "单个测试点时间限制: ":
                            json_string_generate["single_time_limit"] = str(m.next_sibling.next_sibling.string)
                        if str(m.string) == "内存限制: ":
                            json_string_generate["memory_limit"] = str(m.next_sibling.next_sibling.string)
                if z.get("class") == ["problem-content"]:
                    for m in z.find_all("dt"):
                        if str(m.string) == "描述":
                            stringout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                stringout += str(k)
                            json_string_generate["description"] = stringout
                        if str(m.string) == "输入":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["input"] = strout
                        if str(m.string) == "输出":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["output"] = strout
                        if str(m.string) == "样例输入":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["example_input"] = strout
                        if str(m.string) == "样例输出":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["example_output"] = strout
                        if str(m.string) == "提示":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["tip"] = strout
                        if str(m.string) == "来源":
                            strout = ""
                            for k in m.next_sibling.next_sibling.contents:
                                strout += str(k)
                            json_string_generate["origin"] = strout
        if i.get("class") == ["problem-statistics", "col-3"]:
            m = i.dl
            for h in m.find_all("dt"):
                if str(h.string) == "全局题号":
                    json_string_generate["global_exercise_number"] = str(h.next_sibling.next_sibling.string)
                if str(h.string) == "提交次数":
                    json_string_generate["total_submit_count"] = str(h.next_sibling.next_sibling.string)
                if str(h.string) == "尝试人数":
                    json_string_generate["tried_coder_count"] = str(h.next_sibling.next_sibling.string)
                if str(h.string) == "通过人数":
                    json_string_generate["accepted_coder_count"] = str(h.next_sibling.next_sibling.string)
    return json_string_generate


class spider_competition_page:
    def __init__(self, url):
        url = url.rstrip("/")
        prev_data = ""
        times = 1
        dict_for_json_out = {}
        self.global_name = "http://" + url.split("/")[2]
        while True:
            try:
                if use_proxy:
                    now_data = requests.get(url + "?page=%s" % times, proxies=proxies).text
                else:
                    now_data = requests.get(url + "?page=%s" % times).text
                if BeautifulSoup(now_data, "lxml").find_all("table") == \
                        BeautifulSoup(prev_data, "lxml").find_all("table"):
                    print("File exporting.\nFilename: result.json")
                    filing = open("result.json", "w", encoding="utf-8")
                    filing.write(json.dumps(dict_for_json_out))
                    filing.close()
                    print("File exported successfully.")
                    while True:
                        Choose = input("[ALERT: HIGHLY EXPERIMENTAL FUNCTION] Need to convert img url to base64 url ("
                                       "Y/N)?")
                        if (Choose == "Y") or (Choose == "y"):
                            print("Please wait...")
                            img_to_b64()
                            print("Success. Exiting...")
                            exit()
                        elif (Choose == "N") or (Choose == "n"):
                            print("OK. Exiting...")
                            exit()
                        else:
                            print("No valid input. Please try again.")
                            continue
                prev_data = now_data
                self.content = BeautifulSoup(now_data, "lxml")
                self.table = self.content.find_all("table")[0].tbody.find_all("tr")
                for j in self.table:
                    for o in j.find_all("td"):
                        if o.get("class") == ["title"]:
                            dict_for_json_out[str(o.a.string)] = exercise_page_detector(
                                self.global_name + str(o.a.get("href")))
                            print("Fetching: " + self.global_name + str(o.a.get("href")))
                times += 1
            except Exception as Ex:
                continue


class spider_mainpage:
    def __init__(self, prefix):
        while True:
            try:
                self.competition_dict = {}
                if use_proxy:
                    robj = requests.get("http://%s.openjudge.cn/" % prefix, proxies=proxies)
                else:
                    robj = requests.get("http://%s.openjudge.cn/" % prefix)
                print("Load " + ("http://%s.openjudge.cn/" % prefix) + " complete.")
                self.main_url = "http://%s.openjudge.cn/" % prefix
                self.raw_content = robj.text
                print("Content length: " + str(len(self.raw_content)))
                if self.raw_content == "":
                    print("Wrong prefix. Press enter to exit...")
                    input()
                    exit()
                self.content = BeautifulSoup(self.raw_content, features="lxml")
                print("Webpage title is: " + str(self.content.title.string), end="")
                print()
                self.divs = self.content.find_all("div")
                for i in self.divs:
                    if i.get("class") == ['group-description']:
                        self.description = i.p.string
                    if i.get("class") == ["group-name"]:
                        self.name = i.h1.string
                print("Group name is: " + str(self.name))
                print("Group description is: " + str(self.description))
                print("=====LOADING COMPETITION LIST=====")
                for i in self.divs:
                    if i.get("class") == ["main-content"]:
                        self.main_content = i
                        break
                for i in self.main_content.find_all("ul"):
                    if i.get("class") == ["current-contest", "label"]:
                        for x in i.find_all("li"):
                            self.competition_dict[str(x.h3.a.string)] = self.main_url.rstrip("/") + str(
                                x.h3.a.get("href"))
                for l in self.divs:
                    if l.get("class") == ["past-contest", "label"]:
                        self.past_url = self.main_url.rstrip("/") + str(
                            l.h3.a.get("href"))
                        break
                currpage = 1
                prev_data = ""
                while True:
                    try:
                        if use_proxy:
                            robj_subli = requests.get(self.past_url + "?page=%s" % currpage, proxies=proxies)
                        else:
                            robj_subli = requests.get(self.past_url + "?page=%s" % currpage)
                        if prev_data == str(robj_subli.text):
                            break
                        else:
                            currpage += 1
                            prev_data = str(robj_subli.text)
                        robj_subli = BeautifulSoup(robj_subli.text, "lxml")
                    except Exception as Ex:
                        continue
                    curr_table = robj_subli.find_all("table")
                    tableobj = None
                    for y in curr_table:
                        if y.get("id") == "pastContest":
                            tableobj = y
                            break
                    for y in tableobj.tbody.find_all("tr"):
                        self.competition_dict[str(y.a.string)] = str(self.main_url.rstrip("/") + y.a.get("href"))
                print("Found %s competition(s)." % len(self.competition_dict))
                self.selector = list(self.competition_dict.keys())
                for i in range(0, len(self.selector)):
                    print("%s   %s" % (i, self.selector[i]))
                while True:
                    try:
                        spider_competition_page(self.competition_dict[self.selector[int(input("Enter the number of "
                                                                                              "competition: "))]])
                        break
                    except Exception as Ex:
                        print("Wrong input. Please input again.")
            except Exception as Ex:
                print(str(Ex) + str("\nTrying to reload..."))
            break


spider_mainpage(input("Enter prefix of domain: "))
