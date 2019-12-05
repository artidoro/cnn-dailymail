#!/usr/bin/env bash

for i in `seq 0 10 90`
do
    for j in {0..9}
        do
        chunk=$(($i+$j))
        nohup python3 preprocess_generate_labels.py \
              --input_dir=../bbc_stories_tokenized_reduced_1/chunk_${chunk} \
              --ner_output_dir=../bbc_reduce_1_ner_coref_heuristic_chain_labels \
              --contsel_output_dir=../bbc_reduced_1_contsel_tags_labels  > log/bbc_${chunk}.log 2>&1 &
        echo $chunk
        done
        wait
        echo "All Done for this iteration"
done

#python3 preprocess_generate_labels.py \
#              --input_dir=../cnn_stories_tokenized_chunked/chunk_1000 \
#              --ner_output_dir=../cnn_stories_ner_coref_heuristic_chain_labels \
#              --contsel_output_dir=../cnn_stories_contsel_tags_labels