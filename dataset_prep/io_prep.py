# Read the file dataset.jsonl (potentially hundreds of gigabytes) containing text documents in the .jsonl format 
# (each line contains a document in the text field and its source in the meta field under pile_set_name), 
# some of which are duplicated. 

# Deduplicate these documents and write them to a file output.jsonl, keeping the maximum number of documents 
# from the same source according to the following limits: 
# 100000 documents from source "Wikipedia (en)" 
# 50000 documents from source "StackExchange". 
# 
# You can assume that the duplicated documents do not fit into 
# RAM, but deduplicated documents fit.

# Bonus for keeping memory footprint to a minimum.

import gdown
import json
from torch.utils.data import DataLoader, IterableDataset
import hashlib

# file_id = '1XYaC9CzaMSl72PMXW_zEMFqm1weiZqyt'
# gdown.download(id=file_id, output=output_filename, quiet=False)
output_filename = 'dataset.jsonl'
my_file='bruh.jsonl'

seen=set()
# 100000 documents from source "Wikipedia (en)" 
# 50000 documents from source "StackExchange". 
wiki_src, wiki_cnt="Wikipedia (en)", 0
se_src, se_cnt="StackExchange", 0

with open(my_file, 'w') as out:
    with open(output_filename, 'r') as f:
        # Count the number of lines in the file
        dup, num_lines, num_wiki, num_se=0,0,0,0
        for i, line in enumerate(f):
            line_dic=json.loads(line)
            text, src=line_dic['text'], line_dic['meta']['pile_set_name']
            
            # --- logging purposes ---
            num_lines+=1
            if src==wiki_src:
                num_wiki+=1
            if src==se_src:
                num_se+=1

            # --- finding duplicates ---
            text=hash(text)
            if text in seen:
                dup+=1
                continue
            if src== wiki_src:
                if wiki_cnt==100_000:
                    continue
                wiki_cnt+=1
            if src== se_src:
                if se_cnt==50_000:
                    continue
                se_cnt+=1 
            
            # --- writing it out ---
            seen.add(text)
            out.write(line)

#confirmation
print(num_lines, dup, num_wiki, num_se)

with open(my_file, 'r') as f:
    l=(sum(1 for _ in f))
    assert(l==num_lines-dup)


# # {"text": 
# # "Standardised protocol for primate faecal analysis.\nMacroscopic analysis of primate faeces as a way to 
# # study diet is well established, but lack of standardisation of methods may handicap comparative studies 
# # of the resulting data. Here we present a proven technique, including equipment and supplies, protocol an
# # d procedure, that yields quantitative data suitable for systematic investigation within and across prima
# # e taxa. As the problems of habituation become more obvious, the application of such indirect methods may 
# # increase in usefulness.", "meta": {"pile_set_name": "PubMed Abstracts"}}
