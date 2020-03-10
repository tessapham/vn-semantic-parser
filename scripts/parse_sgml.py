"""
Author: Tessa Pham
Description: Functions to parse bitexts in SGML files into separate English and Vietnamese texts.
Created: 02/26/2020
Modified:
"""

from collections import defaultdict
from string import punctuation
from bs4 import BeautifulSoup, Tag

def parse(markup):
    """
    Parses an SGML file into English text, Vietnamese text, and word alignments,
    stored in dictionaries keyed by sentence IDs.
    """
    en = defaultdict(str)
    vn = defaultdict(str)
    ev = defaultdict(str)
    soup = BeautifulSoup(markup, 'html.parser')
    for spair in soup.find_all('spair'):
        sent_id = int(spair.get('id')) # convert ID from string to int
        for child in spair.children:
            if isinstance(child, Tag):
                tag = child.get('id')[:2]
                if tag == 'en':
                    en[sent_id] = child.string
                elif tag == 'vn':
                    vn[sent_id] = child.string
                elif tag == 'ev':
                    ev[sent_id] = child.string
    return en, vn, ev

def write_tsv(sent_dict, filename):
    """Writes a dictionary of sentences to a TSV file including sentence IDs."""
    with open(f'{filename}.tsv', 'w') as file:
        for i in range(1, len(sent_dict) + 1):
            file.write(f'{i}\t{sent_dict[i]}\n')

def write_doc_txt(sent_dict, filename):
    """
    Writes single-language text in a document to a TXT file, one sentence per line
    without ID, using document ID as filename.
    """
    with open(f'{filename}.txt', 'w') as file:
        for i in range(1, len(sent_dict) + 1):
            file.write(f'{sent_dict[i]}\n')

def write_sent_txt(sent, filename):
    """
    Writes a sentence to a TXT file, using sentence index out of all same-language
    sentences (in all documents) as filename.
    """
    with open(f'{filename}.txt', 'w') as file:
            file.write(sent)

def main():
    work_dir = input('Enter relative path to work directory: ')
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    # filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 11)] # test first 10 docs
    en_sent_count = 0
    vn_sent_count = 0
    ev_sent_count = 0
    en_token_count = 0
    vn_token_count = 0

    with open(f'{work_dir}/links.tsv', 'w') as links_file:
        for filename in filenames:
            with open(f'{work_dir}/{filename}.sgml', 'r') as sgml_file:
                en, vn, ev = parse(sgml_file.read())
                """
                # parse text per document
                write_doc_txt(vn, f'{work_dir}/parse-vn/{filename}')
                write_doc_txt(en, f'{work_dir}/parse-en/{filename}')
                write_doc_txt(ev, f'{work_dir}/parse-ev/{filename}')
                """
                """
                # parse text per sentence
                for i in range(1, len(en) + 1):
                    sent = en[i]
                    tokens = list(filter(lambda i: i not in punctuation, sent.split())) # filter out punctuation
                    en_token_count += len(tokens)
                    write_sent_txt(sent, f'{work_dir}/parse-en/{en_sent_count + i}')
                en_sent_count += len(en)
                for i in range(1, len(vn) + 1):
                    sent = vn[i]
                    tokens = list(filter(lambda i: i not in punctuation, sent.split()))
                    vn_token_count += len(tokens)
                    write_sent_txt(sent, f'{work_dir}/parse-vn/{vn_sent_count + i}')
                vn_sent_count += len(vn)
                """
                # save word alignments of all bitexts links.tsv, one bitext per line, with bitext index as ID
                for i in range(1, len(ev) + 1):
                    links = ev[i]
                    links_file.write(f'{ev_sent_count + i}\t{links}\n')
                ev_sent_count += len(ev)

    """
    with open(f'{work_dir}/info.en', 'w') as info_en, open(f'{work_dir}/info.vn', 'w') as info_vn:
        info_en.write(f'# English sentences: {en_sent_count}\n')
        info_en.write(f'# English tokens: {en_token_count}')
        info_vn.write(f'# Vietnamese sentences: {vn_sent_count}\n')
        info_vn.write(f'# Vietnamese tokens: {vn_token_count}')
    
    print(f'# English sentences: {en_sent_count}')
    print(f'# Vietnamese sentences: {vn_sent_count}')
    print(f'# English tokens: {en_token_count}')
    print(f'# Vietnamese tokens: {vn_token_count}')
    """
    print(f'# bitexts: {ev_sent_count}')

main()