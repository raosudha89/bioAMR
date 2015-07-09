import sys, os
import pickle
import nltk

def is_very_long(sent):
	if len(sent.split(" ")) > 100:
		return True
	for word in sent.split(" "):
		if len(word) > 100:
			return True
	return False

def entities_in_a_list(sent, A, B):
	pos_tags = nltk.pos_tag(nltk.word_tokenize(sent))
	print(pos_tags)
	inside = False
	not_in_list = False
	for word, tag in pos_tags:
		if A in word and B in word:
			return True
		if A in word or B in word:
			if inside:
				return True
			inside = True
		if inside:
			if tag not in ['NN', 'NNS', 'NNP', 'NNPS', 'CC', 'DT', ',', ':', '-NONE-', '(', ')']: 
				return False
	return True

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: python3 filter_training_examples training_examples_pickle_file filtered_training_examples_out_dir")
		sys.exit(0)
	training_examples_pickle_file = sys.argv[1]
	filtered_training_examples = {}
	training_examples = pickle.load(open(training_examples_pickle_file, 'rb'))
	filtered_training_examples_out_dir = sys.argv[2]
	filtered_training_examples_out_file = open(os.path.join(filtered_training_examples_out_dir, "filtered_training_examples"), 'w')
	test_set_for_AMR_parser_out_file = open(os.path.join(filtered_training_examples_out_dir, "test_set_for_AMR_parser"), 'w')
	for k, sents  in training_examples.items():
		(A, B, rel) = k
		#print("")
		#print(k)
		filtered_sents = []
		for sent in sents:
			if is_very_long(sent):
				continue
			if not entities_in_a_list(sent, A, B):
				filtered_sents.append(sent)
			#else:
			#	print(sent)
		if filtered_sents:
			filtered_training_examples[k] = filtered_sents

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
	
	pickle.dump(filtered_training_examples, open(os.path.join(filtered_training_examples_out_dir, "filtered_training_examples.p"), 'wb'))
