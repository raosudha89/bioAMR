import sys, os
import pickle
import subprocess

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("python label_using_amr.py training_examples_pickle_file")
		sys.exit(0)
	training_examples_pickle_file = sys.argv[1]
	training_examples = pickle.load(open(training_examples_pickle_file, 'rb'))
	tmp_sent_file = open("/tmp/sent_file", 'w')
	for k, sents in training_examples.items():
		for sent in sents:
			tmp_sent_file.write(sent)
			#subprocess.call(['~pust/amrdecoder/run.sh /tmp/sent_file /tmp/amr_file'])
			os.system('~pust/amrdecoder/run.sh /tmp/sent_file /tmp/amr_file')
			tmp_amr_file = open("/tmp/amr_file", 'r')
			for line in tmp_amr_file.readlines():
				print(line)
			tmp_sent_file.truncate()
			break
		break
