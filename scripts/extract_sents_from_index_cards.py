import sys, os
import json

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("usage: python3 extract_sents_from_index_cards.py index_cards_dir output_file")
		sys.exit(0)

	index_cards_dir = sys.argv[1]
	output_file = open(sys.argv[2], 'w')
	training_examples = {}
	for root, directories, filenames in os.walk(index_cards_dir):
		for json_file in filenames:
			index_card = json.loads(open(os.path.join(root, json_file)).read())
			sentence = str(index_card["evidence"]).lstrip("[\'").rstrip("\']").replace("\\\\\\n", "").replace(" @", "").replace("@ ", "")
			output_file.write(sentence)
			output_file.write("\n")
