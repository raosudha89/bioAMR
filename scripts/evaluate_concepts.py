import sys, os
import pickle

def evaluate_concepts(gold_amr_nx_graphs.p, auto_amr_nx_graphs.p):
	gold_amr_nx_graphs = pickle.load(gold_amr_nx_graphs.p, "rb")	
	auto_amr_nx_graphs = pickle.load(auto_amr_nx_graphs.p, "rb")	

	for ids in gold_amr_nx_graphs.keys():
		gold_amr_nx_graph = gold_amr_nx_graphs[id]
		auto_amr_nx_graph = auto_amr_nx_graphs[id]


if __name__ == "__main__":
	if len(sys.argv < 3):
		print "usage: evaluate_concepts.py gold_amr_nx_graphs.p auto_amr_nx_graphs.p"
		sys.exit(0)
	gold_amr_nx_graphs.p = sys.argv[1]
	auto_amr_nx_graphs.p = sys.argv[2]
	evaluate_concepts(gold_amr_nx_graphs.p, auto_amr_nx_graphs.p)
