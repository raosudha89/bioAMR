import sys, os
import pickle

if __name__ == "__main__":
	training_example_pickle_files = sys.argv[1:]
	all_training_examples = {}
	for f_p in training_example_pickle_files:
		training_examples = pickle.load(open(f_p, 'rb'))
		for k, v in training_examples.iteritems():
			if not all_training_examples.has_key(k):
				all_training_examples[k] = []
			all_training_examples[k] += [sent.replace("\n", "") for sent in v]
	
	for (k, vs) in all_training_examples.iteritems():
		if not vs:
			continue
		print k
		for v in vs:
			print v
		print
	
	pickle.dump(all_training_examples, open("output/all_training_examples.p", 'wb'))
