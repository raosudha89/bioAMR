import sys, os
import pickle
import nltk

def contains_interaction_term(sent, interaction_terms):
	for term in interaction_terms:
		if term in sent:
			return True
	return False

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: python filter_by_interaction_terms.py training_examples_pickle_file interaction_terms filtered_training_examples_out_dir")
		sys.exit(0)
	training_examples_pickle_file = sys.argv[1]
	filtered_training_examples = {}
	training_examples = pickle.load(open(training_examples_pickle_file, 'rb'))
	interaction_terms_file = open(sys.argv[2], 'r')
	filtered_training_examples_out_dir = sys.argv[3]
	filtered_training_examples_out_file = open(os.path.join(filtered_training_examples_out_dir, "filtered_training_examples"), 'w')
	test_set_for_AMR_parser_out_file = open(os.path.join(filtered_training_examples_out_dir, "sentences"), 'w')
	interaction_terms = []
	for line in interaction_terms_file.readlines():
		line = line.strip("\n").strip()
		if line:
			interaction_terms.append(line)
	for k, sents  in training_examples.items():
		(A, B, rel) = k
		filtered_sents = []
		for sent in sents:
			if contains_interaction_term(sent, interaction_terms): 
				filtered_sents.append(sent)
		if filtered_sents:
			#filtered_training_examples[k] = filtered_sents
			if (A,B) in filtered_training_examples:
				key = (A,B)
			elif (B,A) in filtered_training_examples:
				key = (B,A)
			else:
				key = (A,B)
				filtered_training_examples[key] = []
			filtered_training_examples[key] += filtered_sents

	for (k, vs) in filtered_training_examples.items():
		if not vs:
			continue
		filtered_training_examples_out_file.write(str(k))
		filtered_training_examples_out_file.write("\n")
		for v in vs:
			filtered_training_examples_out_file.write(str(v))
			filtered_training_examples_out_file.write("\n")
			test_set_for_AMR_parser_out_file.write(str(v))
			test_set_for_AMR_parser_out_file.write("\n")
		filtered_training_examples_out_file.write("\n")
	
	pickle.dump(filtered_training_examples, open(os.path.join(filtered_training_examples_out_dir, "filtered_training_examples.p"), 'wb'), protocol=0)
