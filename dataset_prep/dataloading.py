# You have dataset.jsonl: too large for RAM
# Build a torch.utils.data.IterableDataset that streams it line by line, yielding tokenized text. 

# Wrap it in a DataLoader with batch_size=8 and a 
# collate_fn that pads each batch to its longest sequence and returns 
# (input_ids [B, T], attention_mask [B, T]). 

# Then iterate one batch and print the shapes.

import json 
import random
from socket import IPV6_DSTOPTS
import torch  # pyright: ignore[reportMissingImports]
from torch.utils.data import DataLoader, IterableDataset  # pyright: ignore[reportMissingImports]
from transformers import GPT2Tokenizer
from torch.nn.utils.rnn import pad_sequence

# setting up fake data
input_fn='dataset.jsonl'
# dic={}
# with open(input_fn, 'w') as f:
#     for i in range(100_000):
#         rand_num = random.randint(10, 50)
#         the_str=''
#         for k in range(rand_num):
#             the_str+=str(k)
#         dic[f'text']=the_str
#         f.write(json.dumps(dic)+'\n')
#         dic={}


tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

class iterable_dataset_(IterableDataset):
    def __init__(self, path):
        super().__init__()
        self.path=path

    def __iter__(self, ):
        with open(self.path, 'r') as f:
            for line in f:
                obj=json.loads(line)
                text=obj['text']
                tokenized=tokenizer.encode(text)
                yield tokenized

def collate_fn(data):
    # data here is of size 8 
    input_ids, mask_stkd=[], []
    data=[torch.tensor(p) for p in data]
    max_len=max([len(p) for p in data])
    for dp in data:
        cur_len=len(dp)
        data_point=dp
        mask=torch.ones(cur_len, dtype=torch.int)
        if cur_len<max_len:
            padding=max_len-cur_len
            mask_pad= torch.zeros(padding, dtype=torch.int)
            data_point=torch.cat((data_point, mask_pad))
            mask=torch.cat((mask, mask_pad))
        input_ids.append(data_point) 
        mask_stkd.append(mask.bool())
    return torch.stack(input_ids), torch.stack(mask_stkd)

    

path = '/workspace/deep-learning/dataset_prep/dataset.jsonl'
my_idst=iterable_dataset_(path)

data_loader=DataLoader(my_idst, batch_size=8 ,collate_fn=collate_fn)

itr=iter(data_loader)
batch=next(itr)
input_ids, mask = batch

print('-'*100)
print(input_ids[mask])
print('-'*100)
print(input_ids[~mask])
assert (torch.all(input_ids[~mask] == 0))
assert (not(torch.any(input_ids[mask]==0)))