import requests
import json
import bs4
import time
from bs4 import BeautifulSoup

def get_gk_links():
    url = 'http://www.nsu.ru/education/schedule/Html_GK/schedule.htm'
    source_code = requests.get(url)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")
    links = []
    for link in soup.find_all('li'):
        print('http://www.nsu.ru/education/schedule/Html_GK/' + link.a.get('href'))
        links.append('http://www.nsu.ru/education/schedule/Html_GK/' + link.a.get('href'))
    return links
#    for link in soup.find_all('a'):
#        print(link.string)
#        print('http://www.nsu.ru/education/schedule/Html_GK/' + link.get('href'))


def get_lk_links():
    url = 'http://www.nsu.ru/education/schedule/Html_LK/'
    source_code = requests.get(url)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")
    links = []
    for link in soup.find_all('li'):
        print('http://www.nsu.ru/education/schedule/Html_LK/' + link.a.get('href'))
        links.append('http://www.nsu.ru/education/schedule/Html_LK/' + link.a.get('href'))
    return links


def get_lk1_links():

    url = 'http://www.nsu.ru/education/schedule/Html_LK1/'
    source_code = requests.get(url)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")
    links = []

    for link in soup.find_all('li'):
        print('http://www.nsu.ru/education/schedule/Html_LK1/' + link.a.get('href'))
        links.append('http://www.nsu.ru/education/schedule/Html_LK1/' + link.a.get('href'))

    return links


def get_schedule(links):

    nsu_schedule = dict()
    for link in links:
        source_code = requests.get(link)
        text = source_code.text
        soup = BeautifulSoup(text, "html.parser")
        for group_link in soup.find_all('a'):
            if has_digit(group_link.string):
                group_number = group_link.string
                last_slash = link.rindex('/')
                url = link[:last_slash+1] + group_link.get('href')
                # url = 'http://www.nsu.ru/education/schedule/Html_GK/Groups/16351_1.htm'
                print(url)
                group_source_code = requests.get(url)
                group_text = group_source_code.text
                group_soup = BeautifulSoup(group_text, "html.parser")
                group_sch = []
                for trs in group_soup.find_all('tr'):
                    if trs.td.string is not None:
                        if has_digit(trs.td.string) and (':' in trs.td.string or '.' in trs.td.string):
                            subj = []
                            for shit1 in trs.find_all('td', recursive=False):
                                # print(shit1.a)
                                # print(shit1.string)
                                # print(shit1.text)
                                if 'ауд' in shit1.text:
                                    strs = parse_content(shit1)
                                    # if len(shit1.contents) == 5:
                                    #     strs = shit1.contents[0].text + '\n' + shit1.contents[1] + '\n' + shit1.contents[4].text
                                    #
                                    # elif len(shit1.contents) == 6:
                                    #     strs = shit1.contents[0] + '\n' + shit1.contents[2] + '\n' + shit1.contents[5].text
                                    #
                                    # elif len(shit1.contents) == 4:
                                    #     strs = shit1.contents[0].text
                                    #
                                    # else:
                                    #     pair = shit1.find_all('td')
                                    #     if pair[0].text.strip() != '' and pair[1].text.strip() != '':
                                    #
                                    #     elif pair[0].text.strip() == '':
                                    #         content = pair[1].hr
                                    #         if content is None:
                                    #             content = pair[1].contents
                                    #         else:
                                    #             content = content.contents
                                    #         if isinstance(content[0], bs4.element.Tag):
                                    #             strs = '//////////\n----------\n' + content[0].text + '\n' + content[1] + '\n' + content[4].text
                                    #         else:
                                    #             strs = '//////////\n----------\n' + content[0] + '\n' + content[2] + '\n' + content[5].text
                                    #     else:
                                    #         content = pair[0].hr
                                    #         if content is None:
                                    #             content = pair[0].contents
                                    #         else:
                                    #             content = content.contents
                                    #         if isinstance(content[0], bs4.element.Tag):
                                    #             strs = content[0].text + '\n' + content[1] + '\n' + content[4].text + '\n----------\n//////////'
                                    #         else:
                                    #             strs = content[0] + '\n' + content[2] + '\n' + content[5].text + '\n----------\n//////////'
                                    subj.append(strs)
                                    print(strs)
                                elif shit1.text.rstrip() == '':
                                    subj.append([''])  # empty subject
                                else:
                                    subj.append(shit1.text)  # subject time
                            group_sch.append(subj)
                print(group_sch)
                group_dict = dict()  # all days with subjects
                for i in range(1, 7):
                    daydict = dict()  # 1 day dict
                    for j in range(0, 7):
                        strg = [group_sch[j][0]] + group_sch[j][i]  # subject in day with time
                        daydict[j] = strg
                    group_dict[i] = daydict
                nsu_schedule[group_number] = group_dict
                time.sleep(1)

    with open('sch.txt', 'w') as output:
        json.dump(nsu_schedule, output)


def parse_content(tagContent):

    subjs = list()

    if len(tagContent.contents) == 5:
        if isinstance(tagContent.contents[0], bs4.element.NavigableString) and isinstance(tagContent.contents[2], bs4.element.NavigableString):
            strs = tagContent.contents[0] + '\n' + tagContent.contents[2]
        else:
            strs = tagContent.contents[0].text + '\n' + tagContent.contents[1] + '\n' + tagContent.contents[4].text

        subjs.append(strs)

    elif len(tagContent.contents) == 6:
        strs = tagContent.contents[0] + '\n' + tagContent.contents[2] + '\n' + tagContent.contents[5].text
        subjs.append(strs)

    elif len(tagContent.contents) == 4:
        strs = tagContent.contents[0].text
        if isinstance(tagContent.contents[1], bs4.element.NavigableString):
            strs += '\n' + tagContent.contents[1]
        subjs.append(strs)
    elif len(tagContent.contents) == 1:
        subjs = parse_content(tagContent.contents[0])
    else:
        pair = tagContent.find_all('td')
        if pair[0].text.strip() != '' and pair[1].text.strip() != '':
            #strs = parse_content(pair[0]) + '\n----------\n' + parse_content(pair[1])
            subjs += parse_content(pair[0])
            subjs += parse_content(pair[1])
        elif pair[0].text.strip() == '':
            content = pair[1]
            #strs = '//////////\n----------\n' + parse_content(content)
            subjs.append('empty_pair')
            subjs += parse_content(content)
        #     content = pair[1].hr
        #     if content is None:
        #         content = pair[1].contents
        #     else:
        #         content = content.contents
        #     if isinstance(content[0], bs4.element.Tag):
        #         strs = '//////////\n----------\n' + content[0].text + '\n' + content[1] + '\n' + content[4].text
        #     else:
        #         strs = '//////////\n----------\n' + content[0] + '\n' + content[2] + '\n' + content[5].text
        else:
            content = pair[0]
            # strs = parse_content(content) + '\n----------\n//////////'
            subjs += parse_content(content)
            subjs.append('empty_pair')
            # content = pair[0].hr
            # if content is None:
            #     content = pair[0].contents
            # else:
            #     content = content.contents
            # if isinstance(content[0], bs4.element.Tag):
            #     strs = content[0].text + '\n' + content[1] + '\n' + content[4].text + '\n----------\n//////////'
            # else:
            #     strs = content[0] + '\n' + content[2] + '\n' + content[5].text + '\n----------\n//////////'

    return subjs


def has_digit(string):
    return any(char.isdigit() for char in string)

links = get_gk_links() + get_lk_links() + get_lk1_links()
print(links)
get_schedule(links)

