import sys, os
import pickle
import nltk

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: python3 filter_training_examples training_examples_pickle_file")
		sys.exit(0)
	training_examples_pickle_file = sys.argv[1]
	filtered_training_examples = {}
	training_examples = pickle.load(open(training_examples_pickle_file, 'rb'))
	for k, sents  in training_examples.items():
		(A, B, rel) = k
		filtered_sents = []
		for sent in sents:
			pos_tags = nltk.pos_tag(nltk.word_tokenize(sent))
			inside = False
			is_valid = True
			for word, tag in pos_tags:
				if A in word and B in word:
					is_valid = False
					break
				if A in word or B in word:
					if inside:
						break
					inside = True
				if inside:
					if tag in ['NN', 'NNS', 'NNP', 'NNPS', 'CC', 'DT', ',']:
						is_valid = False
						break
			if is_valid:
				filtered_sents.append(sent)
		if filtered_sents:
			filtered_training_examples[k] = filtered_sents
	
	for (k, vs) in filtered_training_examples.items():
		if not vs:
			continue
		print(k)
		for v in vs:
			print(v)
		print
	
	pickle.dump(filtered_training_examples, open("output/filtered_training_examples.p", 'wb'))
