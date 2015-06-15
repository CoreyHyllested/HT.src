
VERSION=0.1
REVIEW_DATA="preprocessed/reviews"
echo "Calcuate coallocations v$VERSION"

command -v mahout >/dev/null 2>&1 || { echo >&2 "I require 'mahout' but it's not installed.  Aborting."; exit 1; }

echo "Sequence the review input"
# Sequence all documents (1 file = 1 document), N-Gram (ng) = 5; min documents = 2, min support for attribute is 3
mahout seqdirectory -i preprocessed/reviews/			-o processed/vectors_1_sequenced
mahout seq2sparse	-i processed/vectors_1_sequenced/	-o processed/vectors_2_sparse -ow -ng 5 --minDF 3 --minSupport 4
mahout org.apache.mahout.vectorizer.collocations.llr.CollocDriver -i processed/vectors_2_sparse/tokenized-documents -o processed/vectors_3_colloc2 -ow -ng 2 -u --minLLR 10 --minSupport 3
mahout org.apache.mahout.vectorizer.collocations.llr.CollocDriver -i processed/vectors_2_sparse/tokenized-documents -o processed/vectors_3_colloc3 -ow -ng 3 -u --minLLR 10 --minSupport 3

echo "Dumping output"
mahout seqdumper -i processed/vectors_3_colloc2/ngrams | grep -e "^Key:" | tr -d ':' | awk 'BEGIN{nr=0;} {nr++; print $5, "\t", $2, $3; }' | sort -n 
mahout seqdumper -i processed/vectors_3_colloc3/ngrams | grep -e "^Key:" | tr -d ':' | awk 'BEGIN{nr=0;} {nr++; print $5, "\t", $2, $3; }' | sort -n 
# cat collocations-bigrams.txt | 

