import requests
import string
from lxml import html
import csv


class Senator:
    def __init__(self, name, link):
        self.name = name
        self.link = 'http://www.senato.it{}'.format(link)
        self.parties = []

    def set_parties(self, parties):
        self.parties = parties

    def __str__(self):
        return 'Senator: {}, url {}, parties {}'.format(self.name, self.link, self.parties)


def extract_senator_names(text):
    tree = html.fromstring(text)
    names = tree.xpath("//div[contains(@class, 'linkSenatore')]/p[1]/a/text()")
    links = tree.xpath("//div[contains(@class, 'linkSenatore')]/p[1]/a/@href")

    if len(names) is len(links):
        return [Senator(name, links[index]) for index, name in enumerate(names)]
    else:
        print('mmhh')


def get_all_senators(base_url):
    names_links = []
    for letter in string.ascii_lowercase:
        formatted_url = base_url.format(alphabet_letter=letter)
        print('Getting {}'.format(formatted_url))
        response = requests.get(formatted_url)

        if response.status_code == 200:
            name_link = extract_senator_names(response.text)
            names_links.extend(name_link)
        else:
            print('No senators at {}'.format(formatted_url))
    return names_links


def get_parties_from(link):
    response = requests.get(link)
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        parties = tree.xpath("//a[starts-with(@href, 'http://www.senato.it/loc/link.asp?tipodoc=sgrp')]/text()")
        return [party.strip() for party in parties]
    else:
        print('mmh. response was {}'.format(response))


def write_to_csv(legislature, senators_with_parties):
    filename = 'senators_and_parties/senators_parties_legislature_{}.csv'.format(legislature)
    print("Writing senators for legislature {} to file {}".format(legislature, filename))
    data = [['NAME', 'PARTIES']]
    for senator in senators_with_parties:
        data.append([senator.name, ';'.join(senator.parties)])

    with open(filename, 'w+',
              encoding='utf-8') as myFile:
        writer = csv.writer(myFile, lineterminator='\n')
        writer.writerows(data)


if __name__ == '__main__':
    for legislature in [14, 15, 16, 17]:
        print('Getting legislature {}'.format(legislature))
        base_url = 'http://www.senato.it/leg/{legislature}/BGT/Schede/Attsen/Sen{{alphabet_letter}}.html'

        senators = get_all_senators(base_url.format(legislature=legislature))
        print("Got {} senators for legislature {}".format(len(senators), legislature))

        for index, senator in enumerate(senators):
            print('Getting parties for senator {}/{}'.format(index + 1, len(senators)))
            senator.set_parties(get_parties_from(senator.link))

        write_to_csv(legislature, senators)
        print("Writing complete for legislature {}".format(legislature))
