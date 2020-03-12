"""
Author: Tessa Pham
Description: Util functions.
Created: 02/26/2020
Modified:
"""
from collections import defaultdict
from string import punctuation
from bs4 import BeautifulSoup, Tag

def parse_sgml(markup):
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

def get_word_alignments():
    """
    Saves word alignments of all bitexts links.tsv, one bitext per line,
    with bitext index as ID.
    """
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    bitext_count = 0
    with open('evbc/links.tsv', 'w') as links_file:
        for filename in filenames:
            with open(f'evbc/{filename}.sgml', 'r') as sgml_file:
                _, _, ev = parse_sgml(sgml_file.read())
                for i in range(1, len(ev) + 1):
                    links = ev[i]
                    links_file.write(f'{bitext_count + i}\t{links}\n')
                bitext_count += len(ev)
    return bitext_count

def parse_doc_texts():
    """Parses single-language texts from all documents into TXT files."""
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    for filename in filenames:
        with open(f'evbc/{filename}.sgml', 'r') as sgml_file:
            en, vn, _ = parse_sgml(sgml_file.read())
            write_doc_txt(vn, f'evbc/parse-vn/{filename}')
            write_doc_txt(en, f'evbc/parse-en/{filename}')

def parse_sent_texts():
    """
    Parses single-language sentences from all documents each into a TXT file.
    """
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    en_sent_count = 0
    vn_sent_count = 0
    en_token_count = 0
    vn_token_count = 0

    with open('evbc/links.tsv', 'w') as links_file:
        for filename in filenames:
            with open(f'evbc/{filename}.sgml', 'r') as sgml_file:
                en, vn, _ = parse_sgml(sgml_file.read())
                for i in range(1, len(en) + 1):
                    sent = en[i]
                    tokens = list(filter(lambda i: i not in punctuation, sent.split())) # filter out punctuation
                    en_token_count += len(tokens)
                    write_sent_txt(sent, f'evbc/parse-en/{en_sent_count + i}')
                en_sent_count += len(en)
                for i in range(1, len(vn) + 1):
                    sent = vn[i]
                    tokens = list(filter(lambda i: i not in punctuation, sent.split()))
                    vn_token_count += len(tokens)
                    write_sent_txt(sent, f'evbc/parse-vn/{vn_sent_count + i}')
                vn_sent_count += len(vn)

    with open('evbc/info.en', 'w') as info_en, open(f'evbc/info.vn', 'w') as info_vn:
        info_en.write(f'# English sentences: {en_sent_count}\n')
        info_en.write(f'# English tokens: {en_token_count}')
        info_vn.write(f'# Vietnamese sentences: {vn_sent_count}\n')
        info_vn.write(f'# Vietnamese tokens: {vn_token_count}')

def get_parsed_sents():
    """Returns lists of IDs of successfully parsed sentences and error sentences."""
    with open('xml_ids.txt', 'r') as file:
        return [int(sent_id) for sent_id in file.read().split('\n')]

def parse_xml(markup):
    """Parses UCCA annotations in XML files."""
    soup = BeautifulSoup(markup, 'xml')
    terminals = soup.find_all('attributes', paragraph='1')

    return terminals

def get_unmatched_sentences():
    """
    Returns a list of IDs of sentences whose number of terminals in UCCA parse
    doesn't match its number of tokens.
    """
    ids = get_parsed_sents()
    unmatched = []
    for n in ids:
        with open(f'en-parses/{n}_0.xml', 'r') as xml_file, open(f'evbc/parse-en/{n}.txt', 'r') as txt_file:
            terminals = parse_xml(xml_file.read())
            tokens = txt_file.read().split()
            # assumption: terminals > tokens
            if len(terminals) > len(tokens):
                unmatched.append(n)
    return unmatched

def get_token_dicts(sent_id, links):
    """
    Returns:
        en_token_dict: key = id of Engish token, value = the token itself
        vn_token_dict: key = id of Vietnamese token, value = the token itself
        ev_token_dict: key = id of English token, value = list of ids of Vietnamese tokens it is matched to 
    """
    en_token_dict, vn_token_dict, ev_token_dict = {}, {}, {}
    with open(f'evbc/parse-en/{sent_id}.txt', 'r') as en_file, open(f'evbc/parse-vn/{sent_id}.txt', 'r') as vn_file:
        en_sent = en_file.read()
        vn_sent = vn_file.read()
        en_tokens = en_sent.split()
        vn_tokens = vn_sent.split()
        en_token_dict = {i + 1: en_tokens[i] for i in range(len(en_tokens))}
        vn_token_dict = {j + 1: vn_tokens[j] for j in range(len(vn_tokens))}
    
    links = links.split(';')
    for link in links:
        en_token_ids, vn_token_ids = link.split('-')
        ev_token_dict = {en_id: vn_token_ids.split(',') for en_id in en_token_ids.split(',')}
    return en_token_dict, ev_token_dict, vn_token_dict

def main():
    pass

main()
