import sys, os, re
import pickle

def calculate_p_r_f1(gold_concepts, auto_concepts):
	tp = len(set(gold_concepts).intersection(auto_concepts))
	fn = len(set(gold_concepts).difference(auto_concepts))
	fp = len(set(auto_concepts).difference(gold_concepts))
	if tp+fp == 0:
		p = 0
	else:
		p = tp*1.0/(tp + fp)
	if tp+fn == 0:
		r = 0
	else:
		r = tp*1.0/(tp + fn)
	if p+r == 0:
		f1 = 0
	else:
		f1 = 2*p*r/(p + r)
	return p, r, f1

def get_seen_concepts_count(train_data_list):
	seen_concepts_count = {}
	for train_amr_nx_graphs_data in train_data_list:
		for amr_id in train_amr_nx_graphs_data.keys():
			train_amr_nx_graph = train_amr_nx_graphs_data[amr_id][1]
			for n in train_amr_nx_graph.nodes():
				concept = train_amr_nx_graph.node[n]["instance"].lower()
				concept = re.sub("~e\.[0-9,]*",'', concept)
				if not seen_concepts_count.has_key(concept):
					seen_concepts_count[concept] = 0
				seen_concepts_count[concept] += 1
	return seen_concepts_count	

def evaluate_concepts(gold_amr_nx_graphs_p, auto_amr_nx_graphs_p, train_amr_nx_graphs_p_1, train_amr_nx_graphs_p_2, train_amr_nx_graphs_p_3):
	#amr_nx_graph_data -> {amr_id, [root, amr_nx_graph, sentence, alignment=None]}	
	gold_amr_nx_graphs_data = pickle.load(open(gold_amr_nx_graphs_p, "rb"))
	auto_amr_nx_graphs_data = pickle.load(open(auto_amr_nx_graphs_p, "rb"))
	train_amr_nx_graphs_data_1 = pickle.load(open(train_amr_nx_graphs_p_1, "rb"))
	train_amr_nx_graphs_data_2 = pickle.load(open(train_amr_nx_graphs_p_2, "rb"))
	train_amr_nx_graphs_data_3 = pickle.load(open(train_amr_nx_graphs_p_3, "rb"))
	seen_concepts_count = get_seen_concepts_count([train_amr_nx_graphs_data_1, train_amr_nx_graphs_data_2, train_amr_nx_graphs_data_3])
	P = 0
	R = 0
	F1 = 0
	seen_accuracy = 0
	unseen_concepts = 0
	for amr_id in gold_amr_nx_graphs_data.keys():
		gold_amr_nx_graph = gold_amr_nx_graphs_data[amr_id][1]
		auto_amr_nx_graph = auto_amr_nx_graphs_data[amr_id][1]
		gold_concepts = [gold_amr_nx_graph.node[n]["instance"].lower() for n in gold_amr_nx_graph.nodes()]
		gold_concepts = ["protein" if c.lower() == "enzyme" else c for c in gold_concepts]
		auto_concepts = [auto_amr_nx_graph.node[n]["instance"].lower() for n in auto_amr_nx_graph.nodes()]
		p, r, f1 = calculate_p_r_f1(gold_concepts, auto_concepts)
		P += p
		R += r
		F1 += f1
		#print out some analysis
		print amr_id
		print gold_amr_nx_graphs_data[amr_id][2] 
		print "TP", set(gold_concepts).intersection(auto_concepts)
		print "FN", set(gold_concepts).difference(auto_concepts)
		print "FP", set(auto_concepts).difference(gold_concepts)
		print "%.2f, %.2f, %.2f" % (p, r, f1)
		print
		fn = set(gold_concepts).difference(auto_concepts)
		for c in fn:
			if seen_concepts_count.has_key(c):
				print "Seen", c, seen_concepts_count[c], " times"
		print
		print

		seen_gold_concepts = [gold_concept for gold_concept in gold_concepts if seen_concepts_count.has_key(gold_concept)]
		seen_accuracy += len(set(seen_gold_concepts).intersection(auto_concepts))*1.0/len(seen_gold_concepts)	
		#unseen_concepts += len([gold_concept for gold_concept in gold_concepts if not seen_concepts_count.has_key(gold_concept)])*1.0/len(gold_concepts)
		unseen_concepts += (len(gold_concepts) - len(seen_gold_concepts))*1.0/len(gold_concepts)

	N = len(gold_amr_nx_graphs_data.keys())

	print "Precision %.2f" % (P*1.0/N)
	print "Recall %.2f" % (R*1.0/N)
	print "F1 %.2f" % (F1*1.0/N)

	print "Seen concepts accuracy %.2f" % (seen_accuracy*1.0/N)
	print "Avg unseen concepts %.2f" % (unseen_concepts*1.0/N)

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "usage: evaluate_concepts_py gold_amr_nx_graphs_p auto_amr_nx_graphs_p train_amr_nx_graphs_p_1 train_amr_nx_graphs_p_2 train_amr_nx_graphs_p_3"
		sys.exit(0)
	gold_amr_nx_graphs_p = sys.argv[1]
	auto_amr_nx_graphs_p = sys.argv[2]
	train_amr_nx_graphs_p_1 = sys.argv[3]
	train_amr_nx_graphs_p_2 = sys.argv[4]
	train_amr_nx_graphs_p_3 = sys.argv[5]

	evaluate_concepts(gold_amr_nx_graphs_p, auto_amr_nx_graphs_p, train_amr_nx_graphs_p_1, train_amr_nx_graphs_p_2, train_amr_nx_graphs_p_3)
