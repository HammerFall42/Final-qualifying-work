import time
from selenium import webdriver
from urllib.parse import urlparse


class MyParser:
    def __init__(self, prec_param=3, fol_param=3, syn_param=3):
        self.prec_param = prec_param
        self.fol_param = fol_param
        self.syn_param = syn_param
        self.headers = ["h1", "h2", "h3", "h4", "h5", "h6", "hr"]
        self.tags = ["p", "li", "ul", "ol"] + self.headers

    def parseHtml(self, url, target):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('--no-sandbox')
        browser = webdriver.Chrome("./chromedriver.exe", options=option)

        try:
            browser.get(url)
            time.sleep(1)
        except:
            return []

        elements = []
        for i in range(len(target)):
            temp = browser.find_elements_by_xpath("//*[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), '" + target[i] + "')]")
            for j in temp:
                if j not in elements:
                    elements.append(j)
        strings = []

        i = 0
        while i < len(elements):
            if elements[i].tag_name == 'p':
                all_preceding = browser.find_elements_by_xpath(
                    "//*[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), '" + str(elements[i].text) + "')]//preceding-sibling::p")
                apc_len = len(all_preceding)
                for j in range(min(self.prec_param, apc_len - 1), 0, -1):
                    if all_preceding[apc_len - j - 1] not in elements:
                        strings.append([all_preceding[apc_len - j].text + "\n", "p"])
                    else:
                        break
                strings.append([elements[i].text + "\n", "p"])
                all_following = browser.find_elements_by_xpath(
                    "//*[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), '" + str(elements[i].text) + "')]/following-sibling::p")
                fol_len = len(all_following)
                for j in range(min(self.fol_param, fol_len)):
                    if all_following[j] not in elements:
                        strings.append([all_following[j].text + "\n", "p"])
                    else:
                        break
                strings[len(strings) - 1][0] += "\n"
            elif elements[i].tag_name == 'ul' or elements[i].tag_name == 'ol':
                items = elements[i].find_elements_by_tag_name("li")
                for item in items:
                    strings.append([item.text, "li"])
            elif elements[i].tag_name == 'li':
                temp = elements[i].find_element_by_xpath("..")
                items = temp.find_elements_by_tag_name("li")
                for item in items:
                    strings.append([item.text, "li"])
            elif elements[i].tag_name in self.headers:
                strings.append([elements[i].text, "h"])
                items = elements[i].find_elements_by_xpath(".//*")
                for item in items:
                    strings.append([item.text, "p"])
            else:
                try:
                    temp = elements[i].find_element_by_xpath("..")
                except:
                    i += 1
                    continue
                if temp.tag_name in self.tags:
                    elements[i] = temp
                    i -= 1
            i += 1

        strings.append(["Источник: " + url, "p"])

        return strings

    def findHrefs(self, url, synonyms):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('--no-sandbox')
        browser = webdriver.Chrome("./chromedriver.exe", options=option)

        try:
            browser.get(url)
            time.sleep(1)
        except:
            return []

        elems = browser.find_elements_by_xpath("//a[@href]")
        right_urls = []
        example = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        for elem in elems:
            for syn in synonyms:
                if syn in elem.get_attribute("title") or \
                        syn in elem.get_attribute("id"):
                    right_urls.append(elem.get_attribute("href"))
        for elem in elems:
            href = elem.get_attribute("href")
            parsed_uri = urlparse(href)
            result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if result == example and href not in right_urls:
                right_urls.append(href)

        return right_urls

    def parseSynonyms(self, word):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('--no-sandbox')
        browser = webdriver.Chrome("./chromedriver.exe", options=option)
        url = "https://synonymonline.ru/" + word[0].upper() + "/" + word
        browser.get(url)
        time.sleep(1)

        elems = browser.find_elements_by_css_selector("ol li")

        synonyms = [word]
        for i in range(min(self.syn_param, len(elems))):
            synonyms.append(elems[i].text)

        return synonyms
