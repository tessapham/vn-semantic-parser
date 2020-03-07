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
        sent_id = spair.get('id')
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
            file.write(f'{i}\t{sent_dict[str(i)]}\n')

def write_txt(sent_dict, doc_id):
    """
    Writes each sentence in a dictionary to a TXT file without an ID,
    using document ID as prefix to filename.
    """
    for i in range(1, len(sent_dict) + 1):
        write_sent_txt(sent_dict[str(i)], f'{doc_id}_{i}')

def write_sent_txt(sent, filename):
    """Writes a sentence to a TXT file."""
    with open(f'{filename}.txt', 'w') as file:
            file.write(sent)

def main():
    work_dir = input('Enter relative path to work directory: ')
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    # filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 11)] # test first 10 docs
    en_sent_count = 0
    vn_sent_count = 0
    en_token_count = 0
    vn_token_count = 0

    for filename in filenames:
        with open(f'{work_dir}/{filename}.sgml', 'r') as file:
            en, vn, ev = parse(file.read())
            # write_txt(vn, f'{work_dir}/{filename}_vn')
            # write_txt(en, f'{work_dir}/{filename}_en')
            for i in range(1, len(en) + 1):
                sent = en[str(i)]
                tokens = list(filter(lambda i: i not in punctuation, sent.split())) # filter out punctuation
                en_token_count += len(tokens)
                write_sent_txt(sent, f'{work_dir}/parse-en/{en_sent_count + i}')
            en_sent_count += len(en)
            for i in range(1, len(vn) + 1):
                sent = vn[str(i)]
                tokens = list(filter(lambda i: i not in punctuation, sent.split()))
                vn_token_count += len(tokens)
                write_sent_txt(sent, f'{work_dir}/parse-vn/{vn_sent_count + i}')
            vn_sent_count += len(vn)
    
    with open(f'{work_dir}/info.en', 'w') as info_en, open(f'{work_dir}/info.vn', 'w') as info_vn:
        info_en.write(f'# English sentences: {en_sent_count}\n')
        info_en.write(f'# English tokens: {en_token_count}')
        info_vn.write(f'# Vietnamese sentences: {vn_sent_count}\n')
        info_vn.write(f'# Vietnamese tokens: {vn_token_count}')
    
    print(f'# English sentences: {en_sent_count}')
    print(f'# Vietnamese sentences: {vn_sent_count}')
    print(f'# English tokens: {en_token_count}')
    print(f'# Vietnamese tokens: {vn_token_count}')

main()