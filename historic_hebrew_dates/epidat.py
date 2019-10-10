import csv
import glob
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen
import os

import dateutil
from bs4 import BeautifulSoup
import pandas as pd


def harvest_records_files():
    overview_url = 'http://www.steinheim-institut.de/cgi-bin/epidat?info=howtoharvest'
    html = urlopen(overview_url).read()
    soup = BeautifulSoup(html, f'html.parser')
    anchors = soup.find_all('a', text='list of records ')
    records_list_urls = [
        'http://www.steinheim-institut.de/cgi-bin/epidat'+a['href'] for a in anchors]
    id_pattern = r'^.*resources\-(\w+)$'
    for i, url in enumerate(records_list_urls):
        db_id = re.match(id_pattern, url).group(1)

        with(open(f'data/epidat/records_files/{db_id}.xml', 'wb')) as f:
            content = urlopen(url).read()
            f.write(content)

        print(f'{i}/{len(records_list_urls)}', end='\r')
    print('\n')


def harvest_all_dbs():
    file_list = glob.glob('data/epidat/records_files/*.xml')

    for i, filename in enumerate(file_list):
        print(f'{i}/{len(file_list)}')
        try:
            harvest_tei(filename)
        except:
            print(f'failed:\t{filename}')
        print('\n')


def harvest_tei(records_file):
    db_id = os.path.basename(records_file.strip('.xml'))

    tree = ET.parse(records_file)
    i = 0
    size = sum(1 for _ in tree.iter())
    for elem in tree.iter():
        if elem.tag == 'resource':
            file_path = f'data/epidat/TEI/{db_id}/{elem.attrib["id"]}.xml'
            if not os.path.exists(file_path):
                data = urlopen(elem.attrib['href'])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(data.read())
        i += 1
        print(f'{db_id}:\t\t{i}/{size}', end='\r')


def extract_inscriptions():
    databases = [os.path.basename(os.path.normpath(path))
                 for path in sorted(glob.glob('data/epidat/TEI/*/'))]
    for db in databases:
        ins = extract_database(db)


def extract_database(database_name):
    record_list = sorted(glob.glob(
        f'data/epidat/TEI/{database_name}/*.xml', recursive=True))

    with open(f'data/epidat/transcriptions/{database_name}.csv', 'w') as f:
        csv_writer = csv.writer(
            f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["id", "transcription", "year", "month", "day"])

        for record in record_list:
            csv_writer.writerow(extract_record(record).values())


def extract_record(record_path):
    fields = {
        'file_id': Path(record_path).name.rstrip('.xml'),
        'transcription': None,
        'year': None,
        'month': None,
        'day': None
    }

    with open(record_path) as f:
        soup = BeautifulSoup(f.read(), 'lxml')

        try:
            edition = soup.find('div', {'type': 'edition'})
            ab = edition.find('ab').text
            lines = [l.lstrip().rstrip() for l in ab.splitlines()]
            non_empty_lines = [l for l in lines if len(l) > 0]
            fields['transcription'] = ' '.join(non_empty_lines)
        except:
            pass

        try:
            # TODO: multiple people in one inscription
            person = soup.find('person')
            death = person.find('death')
            when = death['when']
            parsed = dateutil.parser.parse(when)
            fields['year'], fields['month'], fields['day'] = parsed.year, parsed.month, parsed.day
        except:
            pass

    return fields


def combine_inscriptions():
    file_list = glob.glob('data/epidat/transcriptions/*.csv')
    df = pd.concat([pd.read_csv(f) for f in file_list], ignore_index=True)
    df = df.dropna()
    df[['year', 'month', 'day']] = df[['year', 'month', 'day']].astype(int)
    return df


def main():
    # worms_records = 'data/epidat_worms_records.xml'
    # harvest_tei (worms_records)
    # parser = DateParser(lang='hebrew')
    # extract_dates('data/epidat_worms_transcriptions.xml',
    #               parser.search_pattern)
    # extract_inscriptions()
    df = combine_inscriptions()


if __name__ == '__main__':
    main()
