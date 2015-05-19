
VERSION=0.1
REVIEW_DATA="preprocessed/reviews"
echo "Calcuate coallocations v$VERSION"

command -v mahout >/dev/null 2>&1 || { echo >&2 "I require 'mahout' but it's not installed.  Aborting."; exit 1; }

echo "Sequence the review input"
mahout seqdirectory -i preprocessed/reviews/			-o processed/vectors_1_sequenced
mahout seq2sparse	-i processed/vectors_1_sequenced/	-o processed/vectors_2_sparse	-ng 5
mahout org.apache.mahout.vectorizer.collocations.llr.CollocDriver -i processed/vectors_2_sparse/tokenized-documents -o processed/vectors_3_colloc2 -ow -ng 2 -u
mahout org.apache.mahout.vectorizer.collocations.llr.CollocDriver -i processed/vectors_2_sparse/tokenized-documents -o processed/vectors_3_colloc3 -ow -ng 3 -u

echo "Dumping output"
mahout seqdumper -i processed/vectors_3_colloc2/ngrams
mahout seqdumper -i processed/vectors_3_colloc3/ngrams
