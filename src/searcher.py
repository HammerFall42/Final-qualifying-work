from myparser import MyParser
from stemmer import Stemmer
from dbcon import DBCon
import threading
from threading import Thread


class Searcher:
    def __init__(self, links_count=2, prec_param=2, fol_param=2, syn_param=2, depth_param=1):
        self.links_count = int(links_count)
        self.parser = MyParser(int(prec_param), int(fol_param), int(syn_param))
        self.depth = depth_param
        self.stemmer = Stemmer()
        self.dbcon = DBCon()
        self.thread_count = 1
        self.result = []

    def defineTheme(self, synonyms, tab, parent_id=-1):
        if parent_id < 0:
            res = self.dbcon.selectInfo(tab)
        else:
            res = self.dbcon.selectInfo(tab, parent_id)
        def_count = [0] * len(res)
        for k in range(len(res)):
            res_split = [res[k]["name"].split(" "), res[k]["descr"].split(" ")]
            for i in range(len(res_split[0])):
                res_split[0][i] = self.stemmer.stem(res_split[0][i])
            for i in range(len(res_split[1])):
                res_split[1][i] = self.stemmer.stem(res_split[1][i])
            for syn in synonyms:
                if syn in res_split[0]:
                    def_count[k] += 5
                if syn in res_split[1]:
                    def_count[k] += 1
        maxc = 0
        for i in range(len(def_count)):
            if def_count[i] > def_count[maxc]:
                maxc = i

        return maxc

    def defineSearchWords(self, synonyms, depth=1):
        maxc = self.defineTheme(synonyms, "themes")

        if depth == 1:
            search_words = []
            fl = self.dbcon.selectInfo("first_level", maxc + 1)
            for i in range(len(fl)):
                search_words.append(fl[i]["name"])
                sl = self.dbcon.selectInfo("second_level", i + 1)
                for w in sl:
                    search_words.append(w["name"])
        else:
            maxc = self.defineTheme(synonyms, "first_level", maxc + 1)
            if depth == 2:
                search_words = []
                sl = self.dbcon.selectInfo("second_level", maxc + 1)
                for i in range(len(sl)):
                    search_words.append(sl[i]["name"])
            else:
                maxc = self.defineTheme(synonyms, "second_level", maxc + 1)
                search_words = [self.dbcon.selectById(maxc + 1)[0]["name"]]

        return search_words


    def startSearch(self, urls, target, unsplittable=False):
        if unsplittable:
            synonyms = [target]
            semantic_words = []
        else:
            target_split = str(target).split(" ")
            split_len = len(target_split)
            synonyms = []

            if self.parser.syn_param != 0:
                for i in range(split_len):
                    synonyms += self.parser.parseSynonyms(target_split[i])
            else:
                synonyms = target_split

            for i in range(len(synonyms)):
                synonyms[i] = self.stemmer.stem(synonyms[i])

            if self.depth != -1:
                semantic_words = self.defineSearchWords(synonyms, self.depth)
                for i in range(len(semantic_words)):
                    semantic_words[i] = self.stemmer.stem(semantic_words[i])
            else:
                semantic_words = []

        self.result = [None] * len(urls)
        new_urls = []

        search_words = synonyms + semantic_words
        count = 0
        thread_pool = []
        for i in range(len(urls)):
            if count < self.thread_count:
                th = Thread(target=self.searchTarget, args=(urls[i], search_words, i))
                thread_pool.append(th)
                count += 1
            if count == self.thread_count:
                count = 0
                for j in range(len(thread_pool)):
                    thread_pool[j].start()
                    thread_pool[j].join()
                thread_pool = []
            if self.links_count > 0:
                new_urls += self.parser.findHrefs(urls[i], synonyms)[:self.links_count]
        if count > 0:
            count = 0
            for j in range(len(thread_pool)):
                thread_pool[j].start()
                thread_pool[j].join()
            thread_pool = []

        res = []
        for r in self.result:
            res += r
        self.result = [None] * (self.links_count * len(urls))

        for i in range(len(new_urls)):
            if count < self.thread_count:
                th = Thread(target=self.searchTarget, args=(new_urls[i], search_words, i))
                thread_pool.append(th)
                count += 1
            if count == self.thread_count:
                count = 0
                for j in range(len(thread_pool)):
                    thread_pool[j].start()
                    thread_pool[j].join()
                thread_pool = []
        if count > 0:
            for j in range(len(thread_pool)):
                thread_pool[j].start()
                thread_pool[j].join()

        for r in self.result:
            res += r
        self.result = []

        return res

    def searchTarget(self, url, search_words, i):
        self.result[i] = self.parser.parseHtml(url, search_words)

