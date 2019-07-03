from urllib.request import urlopen
import glob
import time
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from pathlib import Path


def harvest_tei():
    tree = ET.parse('data/epidat_worms_records.xml')

    i = 0
    size = sum(1 for _ in tree.iter())
    for elem in tree.iter():
        if elem.tag == 'resource':
            data = urlopen(elem.attrib['href'])
            file_path = f'data/epidat/worms/{elem.attrib["id"]}.xml'
            with open(file_path, 'wb') as f:
                f.write(data.read())
            i += 1
            print(f'{i}/{size}', end='\r')


def extract_inscriptions():
    file_list = glob.glob('data/epidat/*/*.xml', recursive=True)

    for file_path in sorted(file_list):
        with open(file_path) as f:
            try:
                soup = BeautifulSoup(f.read(), 'lxml')
                edition = soup.find('div', {'type': 'edition'})
                ab = edition.find('ab').text
                lines = [l.lstrip().rstrip()
                         for l in ab.splitlines()]
                non_empty_lines = [l for l in lines if len(l) > 0]
                transcription = ' '.join(non_empty_lines)
                file_id = Path(file_path).name.rstrip('.xml')
                with open('data/epidat_worms_transcriptions.xml', 'a') as wf:
                    wf.write(f'\"{file_id}\", \"{transcription}\"\n')
            except:
                continue


extract_inscriptions()
