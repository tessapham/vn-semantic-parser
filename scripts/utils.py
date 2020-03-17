"""
Author: Tessa Pham
Description: Util functions.
Created: 02/26/2020
Modified:
"""
from collections import defaultdict
from string import punctuation
from bs4 import BeautifulSoup, Tag
from ucca import convert, visualization

def parse_sgml(markup):
    """
    Parses an SGML file into EN text, VN text, and word alignments,
    stored in dictionaries keyed by sentence IDs.
    Note: Sentence IDs in this method are of type int.
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
    """
    Writes a dictionary of sentences to a TSV file including sentence IDs.
    """
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

def write_links_file():
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

def parse_doc_texts():
    """
    Parses single-language (EN, VN) texts from every document each into a TXT file.
    """
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    for filename in filenames:
        with open(f'evbc/{filename}.sgml', 'r') as sgml_file:
            en, vn, _ = parse_sgml(sgml_file.read())
            write_doc_txt(vn, f'evbc/parse-vn/{filename}')
            write_doc_txt(en, f'evbc/parse-en/{filename}')

def parse_sent_texts():
    """
    Parses single-language sentences from every document each into a TXT file.
    Note: Sentence IDs in this method are of type int.
    """
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    en_sent_count = 0
    vn_sent_count = 0
    en_token_count = 0
    vn_token_count = 0

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
    """
    Returns IDs of successfully parsed sentences.
    """
    with open('xml_ids.txt', 'r') as file:
        return file.read().split('\n')

def convert_parses():
    """
    Converts the UCCA parse of each EN sentence to that of their VN counterpart by swapping words
    based on word alignments.
    Returns a dictionary: key = sentence ID, value = set of IDs of unmatched terminals to be removed.
    """
    links = {}
    # save links in a dictionary: key = sentence ID, value = links
    with open('evbc/links.tsv', 'r') as links_file:
        lines = links_file.readlines()
        links = {line.split('\t')[0]: line.split('\t')[1] for line in lines}

    ids = get_parsed_sents()
    rm_nodes_dict = {}
    for n in ids:
        with open(f'en-parses/{n}_0.xml', 'r') as en_file, open(f'evbc/parse-en/{n}.txt', 'r') as txt_file:
            # skip if # terminals doesn't match # tokens
            soup = BeautifulSoup(en_file.read(), 'xml')
            terminals = soup.find_all('attributes', paragraph='1')
            tokens = txt_file.read().split()
            if len(terminals) != len(tokens): continue

            en_token_dict, ev_token_dict, vn_token_dict = get_token_dicts(n, links[n])
            
            # skip if any EN or VN token ID in links isn't present in en_token_dict or vn_token_dict
            en_diff = set(ev_token_dict.keys()) - set(en_token_dict.keys())
            if en_diff:
                print(f'sentence ID: {n}, different EN token IDs: {en_diff}')
                continue
            vn_diff = set(sum(ev_token_dict.values(), [])) - set(vn_token_dict.keys())
            if vn_diff:
                print(f'sentence ID: {n}, different VN token IDs: {vn_diff}')
                continue
            
            # use token dictionaries for this sentence to swap EN-VN tokens
            for en_id, vn_ids in ev_token_dict.items():
                vn_tokens = [vn_token_dict[token_id] for token_id in vn_ids]
                soup.find('attributes', paragraph='1', paragraph_position=en_id)['text'] = ' '.join(vn_tokens)
            
            # record node IDs of unmatched EN tokens to be removed
            unmatched = set(en_token_dict.keys()) - set(ev_token_dict.keys())
            rm_nodes_dict[n] = [f'0.{token_id}' for token_id in unmatched]
            # temporarily replace unmatched tokens with empty string
            for token_id in unmatched:
                soup.find('attributes', paragraph='1', paragraph_position=token_id)['text'] = ''

            # write BeatifulSoup object to vn_file
            converted = '\n'.join(soup.prettify().split('\n')[1:]) # remove encoding line
            with open(f'vn-parses/{n}_0.xml', 'w') as vn_file:
                vn_file.write(converted)
    
    return rm_nodes_dict

def trim_parse(sent_id, rm_nodes):
    """
    Removes terminal nodes that do not have a corresponding VN token and any of their parents
    that has only 1 child as the unmatched node.
    Returns IDs of removed nodes.
    """
    passage = convert.file2passage(f'vn-parses/{sent_id}_0.xml')
    removed = set()
    while rm_nodes:
        node_id = rm_nodes.pop(0)
        if node_id not in removed:
            node = passage.by_id(node_id)
            rm_nodes.extend([p.ID for p in node.parents if len(p.children) == 1])
            node.destroy()
            removed.add(node_id)
    convert.passage2file(passage, f'vn-parses/{sent_id}_0.xml')
    return removed
            
def trim_parses():
    rm_nodes_dict = convert_parses()
    ids = get_parsed_sents()
    for n in ids:
        if n not in rm_nodes_dict: continue
        trim_parse(n, rm_nodes_dict[n])

def word_reorder_parses():
    pass

def get_token_dicts(sent_id, links):
    """
    Returns:
        en_token_dict: key = ID of Engish token, value = the token itself
        vn_token_dict: key = ID of VN token, value = the token itself
        ev_token_dict: key = ID of EN token, value = IDs of VN tokens it is matched to 
    """
    en_token_dict, vn_token_dict, ev_token_dict = {}, {}, {}
    with open(f'evbc/parse-en/{sent_id}.txt', 'r') as en_file, open(f'evbc/parse-vn/{sent_id}.txt', 'r') as vn_file:
        en_sent = en_file.read()
        vn_sent = vn_file.read()
        en_tokens = en_sent.split()
        vn_tokens = vn_sent.split()
        en_token_dict = {str(i + 1): en_tokens[i] for i in range(len(en_tokens))}
        vn_token_dict = {str(j + 1): vn_tokens[j] for j in range(len(vn_tokens))}
    
    links = links.split(';')
    for link in links[:-1]: # last link is blank
        en_token_ids, vn_token_ids = link.split('-')
        for en_id in en_token_ids.split(','):
            ev_token_dict[en_id] = vn_token_ids.split(',')
    # if last token is punctuation, match with VN last token
    en_last_id = str(len(en_tokens))
    vn_last_id = str(len(vn_tokens))
    if en_last_id not in ev_token_dict and en_token_dict[en_last_id] == vn_token_dict[vn_last_id]:
        ev_token_dict[en_last_id] = [vn_last_id]
    
    return en_token_dict, ev_token_dict, vn_token_dict

def main():
    trim_parses()

main()
