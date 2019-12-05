#%%
import json
import random

#%%
with open("./bbc_chain_extractor/XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json") as json_data:
    train_dev_test_dict = json.load(json_data)

train_ids = train_dev_test_dict['train']
test_ids = train_dev_test_dict['test']
val_ids = train_dev_test_dict['validation']

#%%
print(len(train_ids), len(test_ids), len(val_ids))

#%%
with open('bbc_ids_test.txt', 'w') as test_ids_file:
    for test_id in test_ids:
        test_ids_file.write(test_id + '\n')

#%%
with open('bbc_ids_train.txt', 'w') as train_ids_file:
    for train_id in train_ids:
        train_ids_file.write(train_id + '\n')

#%%
with open('bbc_ids_val.txt', 'w') as val_ids_file:
    for val_id in val_ids:
        val_ids_file.write(val_id + '\n')


#%%
with open('bbc_ids_train.txt') as train_ids_file:
    print(len(train_ids_file.readlines()))

#%%
with open('bbc_ids_val.txt') as val_ids_file:
    print(len(val_ids_file.readlines()))

#%%
with open('bbc_ids_test.txt') as test_ids_file:
    print(len(test_ids_file.readlines()))

#%%

#####
# Reduced dataset 10K train 1k eval 1k test
random.seed(0)
random.shuffle(train_ids)
random.shuffle(test_ids)
random.shuffle(val_ids)

#%%
train_ids = train_ids[:10000]
test_ids = test_ids[:1000]
val_ids = val_ids[:1000]

#%%
print(len(train_ids), len(test_ids), len(val_ids))

#%%
with open('bbc_ids_test_1k.txt', 'w') as test_ids_file:
    for test_id in test_ids:
        test_ids_file.write(test_id + '\n')

#%%
with open('bbc_ids_train_10k.txt', 'w') as train_ids_file:
    for train_id in train_ids:
        train_ids_file.write(train_id + '\n')

#%%
with open('bbc_ids_val_1k.txt', 'w') as val_ids_file:
    for val_id in val_ids:
        val_ids_file.write(val_id + '\n')


#%%
with open('bbc_ids_train_10k.txt') as train_ids_file:
    print(len(train_ids_file.readlines()))

#%%
with open('bbc_ids_val_1k.txt') as val_ids_file:
    print(len(val_ids_file.readlines()))

#%%
with open('bbc_ids_test_1k.txt') as test_ids_file:
    print(len(test_ids_file.readlines()))

