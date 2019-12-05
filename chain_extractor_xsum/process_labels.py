import sys
import os
import hashlib
import struct
import subprocess
import collections
import tensorflow as tf
from tensorflow.core.example import example_pb2

dm_single_close_quote = '\u2019'  # unicode
dm_double_close_quote = '\u201d'
END_TOKENS = ['.', '!', '?', '...', "'", "`", '"', dm_single_close_quote, dm_double_close_quote,
              ")"]  # acceptable ways to end a sentence

# We use these to separate the summary sentences in the .bin datafiles
SENTENCE_START = '<s>'
SENTENCE_END = '</s>'

all_train_urls = "../url_lists/url_lists_reduced_1/bbc_ids_train.txt"
all_val_urls = "../url_lists/url_lists_reduced_1/bbc_ids_val.txt"
all_test_urls = "../url_lists/url_lists_reduced_1/bbc_ids_test.txt"


# These are the number of .story files we expect there to be in bbc_stories_dir
# num_expected_stories = 226711
num_expected_stories = 12000

VOCAB_SIZE = 200000
CHUNK_SIZE = 1000  # num examples per chunk, for the chunked data


def chunk_file(set_name):
    in_file = finished_files_dir+'/%s.bin' % set_name
    reader = open(in_file, "rb")
    chunk = 0
    finished = False
    while not finished:
        chunk_fname = os.path.join(chunks_dir, '%s_%03d.bin' % (set_name, chunk))  # new chunk
        with open(chunk_fname, 'wb') as writer:
            for _ in range(CHUNK_SIZE):
                len_bytes = reader.read(8)
                if not len_bytes:
                    finished = True
                    break
                str_len = struct.unpack('q', len_bytes)[0]
                example_str = struct.unpack('%ds' % str_len, reader.read(str_len))[0]
                writer.write(struct.pack('q', str_len))
                writer.write(struct.pack('%ds' % str_len, example_str))
            chunk += 1


def chunk_all():
    # Make a dir to hold the chunks
    if not os.path.isdir(chunks_dir):
        os.mkdir(chunks_dir)
    # Chunk the data
    for set_name in ['train', 'val', 'test']:
        print("Splitting %s data into chunks..." % set_name)
        chunk_file(set_name)
    print("Saved chunked data in %s" % chunks_dir)


def tokenize_stories(stories_dir, tokenized_stories_dir):
    """Maps a whole directory of .story files to a tokenized version using Stanford CoreNLP Tokenizer"""
    print("Preparing to tokenize %s to %s..." % (stories_dir, tokenized_stories_dir))
    stories = os.listdir(stories_dir)
    # make IO list file
    print("Making list of files to tokenize...")
    with open("mapping.txt", "w") as f:
        for s in stories:
            f.write("%s \t %s\n" % (os.path.join(stories_dir, s), os.path.join(tokenized_stories_dir, s)))
    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer', '-ioFileList', '-preserveLines', 'mapping.txt']
    print("Tokenizing %i files in %s and saving in %s..." % (len(stories), stories_dir, tokenized_stories_dir))
    subprocess.call(command)
    print("Stanford CoreNLP Tokenizer has finished.")
    os.remove("mapping.txt")

    # Check that the tokenized stories directory contains the same number of files as the original directory
    num_orig = len(os.listdir(stories_dir))
    num_tokenized = len(os.listdir(tokenized_stories_dir))
    if num_orig != num_tokenized:
        raise Exception(
            "The tokenized stories directory %s contains %i files, but it should contain the same number as %s (which has %i files). Was there an error during tokenization?" % (
            tokenized_stories_dir, num_tokenized, stories_dir, num_orig))
    print("Successfully finished tokenizing %s to %s.\n" % (stories_dir, tokenized_stories_dir))


def read_text_file(text_file):
    lines = []
    with open(text_file, "r") as f:
        for line in f:
            lines.append(line.strip())
    return lines


def hashhex(s):
    """Returns a heximal formated SHA1 hash of the input string."""
    h = hashlib.sha1()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def get_url_hashes(url_list):
    return [hashhex(url) for url in url_list]


def fix_missing_period(line):
    """Adds a period to a line that is missing a period"""
    if "@highlight" in line: return line
    if line == "": return line
    if line[-1] in END_TOKENS: return line
    # print line[-1]
    return line + " ."


def get_art_abs_lbs(story_file, label_file, chains_file):
    article = open(story_file + ".article", "r").read()
    abstract = open(story_file + ".abstract", "r").read()

    article_lines = article.split('<split1>')

    labels = read_text_file(label_file)
    chains = open(chains_file, "r").read()

    if len(labels) == 0 and len(article_lines)==0:
        labels = ""
    elif len(labels) == 0 and len(article_lines)!=0:
        print(story_file)
        print(labels)
        print(article_lines)
        exit(0)
    else:
        labels = labels[0]
    # Make article into a single string
    article = ' <split1> '.join(article_lines)
    if len(article.split()) != len(labels.split()):
        print(story_file)
        print("Article and label mismatch, check labeling process")
        print(len(article.split()))
        print(len(labels.split()))
        print(article)
        print(labels)
        a = article.split()
        b = labels.split()
        for i in range(len(article.split())):
            print(a[i],b[i])
        exit()

    return article, abstract, labels, chains


def write_to_bin(url_file, out_file, makevocab=False):
    """Reads the tokenized .story files corresponding to the urls listed in the url_file and writes them to a out_file."""
    print("Making bin file for URLs listed in %s..." % url_file)
    story_fnames = read_text_file(url_file)
    # url_hashes = get_url_hashes(url_list)
    # story_fnames = [s + ".story" for s in url_hashes]
    num_stories = len(story_fnames)

    if makevocab:
        vocab_counter = collections.Counter()

    with open(out_file, 'wb') as writer:
        for idx, s in enumerate(story_fnames):
            if idx % 1000 == 0:
                print("Writing story %i of %i; %.2f percent done" % (
                idx, num_stories, float(idx) * 100.0 / float(num_stories)))

            # Look in the tokenized story dirs to find the .story file corresponding to this url
            if os.path.isfile(os.path.join(bbc_tokenized_stories_dir, s + '.article')) and os.path.isfile(os.path.join(bbc_tokenized_stories_dir, s + '.abstract')):
                story_file = os.path.join(bbc_tokenized_stories_dir, s)
            else:
                print(
                    "Error: Couldn't find tokenized story file %s in tokenized story directory %s. Was there an error during tokenization?" % (
                    s, bbc_tokenized_stories_dir))
                # Check again if tokenized stories directories contain correct number of files
                print("Checking that the tokenized stories directory %s contains correct number of files..." % (
                bbc_tokenized_stories_dir))
                check_num_stories(bbc_tokenized_stories_dir, num_expected_stories * 2)
                raise Exception(
                    "Tokenized stories directory %s contains correct number of files but story file %s found in neither." % (
                    bbc_tokenized_stories_dir, s))
            if os.path.isfile(os.path.join(bbc_label_dir, s)):
                label_file = os.path.join(bbc_label_dir, s)
            else:
                print(
                    "Error: Couldn't find label story file %s in either label directory %s. Was there an error during labeling?" % (
                        s, bbc_label_dir))

            if os.path.isfile(os.path.join(bbc_chains_dir, s)):
                chains_file = os.path.join(bbc_chains_dir, s)
            else:
                print(
                    "Error: Couldn't find chains story file %s in either label directory %s. Was there an error during labeling?" % (
                        s, bbc_chains_dir))
            print("processing: "+s)
            # Get the strings to write to .bin file
            article, abstract, labels, chains = get_art_abs_lbs(story_file, label_file, chains_file)
            # Write to tf.Example
            tf_example = example_pb2.Example()
            tf_example.features.feature['article'].bytes_list.value.extend([str.encode(article)])
            tf_example.features.feature['abstract'].bytes_list.value.extend([str.encode(abstract)])
            tf_example.features.feature['labels'].bytes_list.value.extend([str.encode(labels)])
            tf_example.features.feature['links'].bytes_list.value.extend([str.encode(chains)])
            tf_example_str = tf_example.SerializeToString()
            str_len = len(tf_example_str)
            writer.write(struct.pack('q', str_len))
            writer.write(struct.pack('%ds' % str_len, tf_example_str))

            # Write the vocab to file, if applicable
            if makevocab:
                art_tokens = article.split(' ')
                abs_tokens = abstract.split(' ')
                abs_tokens = [t for t in abs_tokens if
                              t not in [SENTENCE_START, SENTENCE_END]]  # remove these tags from vocab
                tokens = art_tokens + abs_tokens
                tokens = [t.strip() for t in tokens]  # strip
                tokens = [t for t in tokens if t != ""]  # remove empty
                vocab_counter.update(tokens)

    print("Finished writing file %s\n" % out_file)

    # write vocab to file
    if makevocab:
        print("Writing vocab file...")
        with open(os.path.join(finished_files_dir, "vocab"), 'w') as writer:
            for word, count in vocab_counter.most_common(VOCAB_SIZE):
                writer.write(word + ' ' + str(count) + '\n')
        print("Finished writing vocab file")

def check_num_stories(stories_dir, num_expected):
    num_stories = len(os.listdir(stories_dir))
    if num_stories != num_expected:
        raise Exception(
            "stories directory %s contains %i files but should contain %i" % (stories_dir, num_stories, num_expected))
    return

if __name__ == '__main__':
    # Directory names for input and output directories.
    bbc_tokenized_stories_dir = '../bbc_stories_tokenized_reduced_1'
    bbc_label_dir = '../bbc_reduced_1_contsel_tags_labels'
    bbc_chains_dir = '../bbc_reduced_1_ner_coref_heuristic_chain_labels'
    finished_files_dir = "../finished_files_wlabels_wner_wcoref_chains_reduced_1"
    chunks_dir = os.path.join(finished_files_dir, "chunked")


    # Check the stories directories contain the correct number of .story files
    # May skip this for new dataset where we don't know num.
    check_num_stories(bbc_tokenized_stories_dir, num_expected_stories * 2) # One for the article and one for the abstract file
    check_num_stories(bbc_label_dir, num_expected_stories)
    check_num_stories(bbc_chains_dir, num_expected_stories)

    # # Create some new directories
    if not os.path.exists(finished_files_dir): os.makedirs(finished_files_dir)

    # Read the tokenized stories, do a little postprocessing then write to bin files
    write_to_bin(all_test_urls, os.path.join(finished_files_dir, "test.bin"))
    write_to_bin(all_val_urls, os.path.join(finished_files_dir, "val.bin"))
    write_to_bin(all_train_urls, os.path.join(finished_files_dir, "train.bin"), makevocab=True)

    # Chunk the data. This splits each of train.bin, val.bin and test.bin into smaller chunks, each containing e.g. 1000 examples, and saves them in finished_files/chunks
    chunk_all()