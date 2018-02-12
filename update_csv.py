import csv
import requests
from lxml import html
from joblib import Parallel, delayed


def get_rows():
    print('Reading file')
    with open('./emendamenti.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        return [row for row in reader]


def get_tizio_nome_or_commissione(url):
    try:
        response = requests.get(url)
        tree = html.fromstring(response.content)
        names_paragraph = tree.xpath('//*[@id="testo"]/p[2]')[0]
        potential_names = names_paragraph.xpath('//a/text()')[4:]
        if len(potential_names) is 0:
            return 'Commissione'
        else:
            return ','.join(potential_names)
    except IndexError:
        return 'FAILED'


def write_new_rows(rows):
    print('Writing all new rows to file')
    with open('./with_sponsor.csv', newline='', mode='w+') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def update_row_with_name(row):
    nome = get_tizio_nome_or_commissione(row['URL'])
    row['SPONSOR'] = nome
    global counter
    counter = counter + 1
    return row

counter = 1
if __name__ == '__main__':
    rows = get_rows()

    to_do = rows

    new_rows = Parallel(n_jobs=4)(delayed(update_row_with_name)(row) for row in to_do)

    write_new_rows(new_rows)
