#%%
import os
import shutil

#%%
train_10k_path = 'url_lists/url_lists_reduced_1/bbc_ids_train.txt'
test_1k_path = 'url_lists/url_lists_reduced_1/bbc_ids_test.txt'
val_1k_path = 'url_lists/url_lists_reduced_1/bbc_ids_val.txt'

# %%
def read_file_names(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        return [line.strip() for line in lines]

# %%
train_10k = read_file_names(train_10k_path)
test_1k = read_file_names(test_1k_path)
val_1k = read_file_names(val_1k_path)

# %%
def copy_files(file_names, root_path_source, root_path_dest):
    for name in file_names:
        source_path = os.path.join(root_path_source, name)
        article_source_path = source_path + '.article'
        abstract_source_path = source_path + '.abstract'

        destination_path = os.path.join(root_path_dest, name)
        article_dest_path = destination_path + '.article'
        abstract_dest_path = destination_path + '.abstract'

        shutil.copy(article_source_path, article_dest_path)
        shutil.copy(abstract_source_path, abstract_dest_path)


# %%
root_path_source = './bbc_stories_tokenized'
root_path_dest = './bbc_stories_tokenized_reduced_1'

if not os.path.exists(root_path_dest): os.makedirs(root_path_dest)


# %%
copy_files(train_10k, root_path_source, root_path_dest)
copy_files(test_1k, root_path_source, root_path_dest)
copy_files(val_1k, root_path_source, root_path_dest)

# %%
