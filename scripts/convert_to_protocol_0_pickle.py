import sys
import pickle

if __name__ == "__main__":
	input_pickle_file = sys.argv[1]
	output_pickle_file = sys.argv[2]
	data = pickle.load(open(input_pickle_file, 'rb'))
	pickle.dump(data, open(output_pickle_file, 'wb'), protocol=0)
