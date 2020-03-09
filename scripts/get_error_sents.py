with open('xml_ids.txt', 'r') as file:
    ids = [int(sent_id) for sent_id in file.read().split('\n')]
    print(f'# IDs: {len(ids)}')
    error_sents = list(set(range(1, 45309)) - set(ids))
    print(f'Error sentences: {error_sents}')
