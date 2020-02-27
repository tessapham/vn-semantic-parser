from collections import defaultdict
from bs4 import BeautifulSoup, Tag

def parse(markup):
    """
    Parses an SGML file into English text, Vietnamese text, and word alignments,
    stored in dictionaries keyed by sentence IDs
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

def write_tsv(sent_dict, path):
    """Writes a dictionary of sentences to a TSV file including sentence IDs."""
    with open(path, 'w') as file:
        for i in range(1, len(sent_dict) + 1):
            file.write(f'{i}\t{sent_dict[str(i)]}\n')

def write_txt(sent_dict, path):
    """Writes a dictionary of sentences to a TXT file without sentence IDs."""
    with open(path, 'w') as file:
        for i in range(1, len(sent_dict) + 1):
            file.write(f'{sent_dict[str(i)]} ')

def main():
    work_dir = input('Enter relative path to work directory: ')
    filenames = [f'N{str(file_num).zfill(4)}' for file_num in range(1, 1001)] # N0001 to N1000
    for filename in filenames:
        with open(f'{work_dir}/{filename}.sgml', 'r') as file:
            en, vn, ev = parse(file.read())
            write_txt(vn, f'{work_dir}/{filename}_vn.txt')
            write_txt(en, f'{work_dir}/{filename}_en.txt')

main()