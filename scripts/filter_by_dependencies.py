import sys, os
import pickle
from stanford import StanfordParser
interaction_terms = []
sp = None

def has_interaction_term_as_lcs_in_dependency(sent, A, B):
	indices_of_A = []
	indices_of_B = []
	sent = sent.encode('utf-8')
	A = A.encode('utf-8')
	B = B.encode('utf-8')
	print(sent)
	print(A, B)
	parsed_sentence = sp.parse(sent)
	for i in range(1, len(parsed_sentence.word)):
		if A in parsed_sentence.word[i]:
			indices_of_A.append(i)
		if B in parsed_sentence.word[i]:
			indices_of_B.append(i)
	index_pairs = []
	for a in indices_of_A:
		for b in indices_of_B:
			index_pairs.append((a, b))
	shortest_path_words = ""
	for (i, j) in index_pairs:
		lcn, shortest_path = parsed_sentence.get_least_common_node(i, j) #sp is 1 based
		shortest_path_words = [parsed_sentence.word[index] for index in shortest_path]
		print(shortest_path_words)
		for word in shortest_path_words:
			for term in interaction_terms:
				if term in word:
					return term
	return None

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: jython filter_by_dependencies.py training_examples_pickle_file interaction_terms_file filtered_training_examples_out_dir stanford_parser_file")
		sys.exit(0)
	training_examples_pickle_file = sys.argv[1]
	filtered_training_examples = {}
	training_examples = pickle.load(open(training_examples_pickle_file, 'rb'))
	interaction_terms_file = open(sys.argv[2], 'r')
	filtered_training_examples_out_dir = sys.argv[3]
	filtered_training_examples_out_file = open(os.path.join(filtered_training_examples_out_dir, "filtered_training_examples"), 'w')
	test_set_for_AMR_parser_out_file = open(os.path.join(filtered_training_examples_out_dir, "sentences"), 'w')
	global interaction_terms
	for line in interaction_terms_file.readlines():
		line = line.strip("\n").strip()
		if line:
			interaction_terms.append(line)
	parser_file = sys.argv[4]
	global sp
	sp = StanfordParser(parser_file)
	max_count = 100000
	count = 0
	for k, sents  in training_examples.items():
		A = k[0]
		B = k[1]
		A = A.encode('utf-8')
		B = B.encode('utf-8')
		for sent in sents:
			count += 1
			print("\n")
			print(count)
			if count > max_count:
				break
			sent = sent.encode('utf-8')
			if "Abbreviations" in sent:
				continue
			interaction_term = has_interaction_term_as_lcs_in_dependency(sent, A, B)
			if interaction_term:
				key = (A, B, interaction_term)
				if key not in filtered_training_examples:
					filtered_training_examples[key] = []
				filtered_training_examples[key].append(sent)
		if count > max_count:
			break

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
