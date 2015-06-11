import sys, os
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


def evaluate_concepts(gold_amr_nx_graphs_p, auto_amr_nx_graphs_p):
	#amr_nx_graph_data -> {amr_id, [root, amr_nx_graph, sentence, alignment=None]}	
	gold_amr_nx_graphs_data = pickle.load(open(gold_amr_nx_graphs_p, "rb"))
	auto_amr_nx_graphs_data = pickle.load(open(auto_amr_nx_graphs_p, "rb"))
	P = 0
	R = 0
	F1 = 0
	for amr_id in gold_amr_nx_graphs_data.keys():
		gold_amr_nx_graph = gold_amr_nx_graphs_data[amr_id][1]
		auto_amr_nx_graph = auto_amr_nx_graphs_data[amr_id][1]
		gold_concepts = [gold_amr_nx_graph.node[n]["instance"] for n in gold_amr_nx_graph.nodes()]
		auto_concepts = [auto_amr_nx_graph.node[n]["instance"] for n in auto_amr_nx_graph.nodes()]
		p, r, f1 = calculate_p_r_f1(gold_concepts, auto_concepts)
		P += p
		R += r
		F1 += f1
	
	N = len(gold_amr_nx_graphs_data.keys())

	print "Precision %.2f" % (P*1.0/N)
	print "Recall %.2f" % (R*1.0/N)
	print "F1 %.2f" % (F1*1.0/N)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "usage: evaluate_concepts_py gold_amr_nx_graphs_p auto_amr_nx_graphs_p"
		sys.exit(0)
	gold_amr_nx_graphs_p = sys.argv[1]
	auto_amr_nx_graphs_p = sys.argv[2]
	evaluate_concepts(gold_amr_nx_graphs_p, auto_amr_nx_graphs_p)
