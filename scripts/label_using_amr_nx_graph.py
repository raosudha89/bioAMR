import sys
import pickle
import networkx as nx
import pdb

def get_all_protein_nodes(amr_nx_graph, protein_list):
	protein_nodes = []
	for node in amr_nx_graph.nodes():
		if amr_nx_graph.node[node]['instance'] == 'protein':
			children = amr_nx_graph.successors(node)
			for child in children:
				grandchildren = amr_nx_graph.successors(child)
				for grandchild in grandchildren:
					if amr_nx_graph.node[grandchild]['instance'].strip("\"").strip("\'") in protein_list:
						protein_nodes.append(grandchild)
	return protein_nodes

def show_path_info(path, amr_nx_graph):
	info = "(" + amr_nx_graph.node[path[0]]['instance'] + ")" + "__"
	for i in range(1, len(path)):
		edge_label = amr_nx_graph[path[i-1]][path[i]][0]['relation']
		info += edge_label + "__"
		info += "(" + amr_nx_graph.node[path[i]]['instance'] + ")"
		info += "__"
	info = info.rstrip("__")
	print info

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage python label_using_amr_nx_graph.py amr_nx_graphs.p protein_list interaction_terms")
		sys.exit(0)
	amr_nx_graphs_p = sys.argv[1]
	amr_nx_graphs = pickle.load(open(amr_nx_graphs_p, 'rb'))
	protein_list = []
	protein_list_file = open(sys.argv[2], 'r')
	for line in protein_list_file.readlines():
		protein_list.append(line.strip('\n'))
	interaction_terms = []
	interaction_terms_file = open(sys.argv[3], 'r')
	for line in interaction_terms_file.readlines():
		interaction_terms.append(line.strip('\n'))
	for k, value in amr_nx_graphs.items():
		[root, amr_nx_graph, sentence] = value
		#get all protein nodes which are in the 'protein_list'
		protein_nodes = get_all_protein_nodes(amr_nx_graph, protein_list)
		#between every two protein nodes, find shortest path via lcs
		for i in range(len(protein_nodes)):
			for j in range(i+1, len(protein_nodes)):
				p1 = protein_nodes[i]
				p2 = protein_nodes[j]
				path = nx.dijkstra_path(amr_nx_graph.to_undirected(), p1, p2)
				show_path_info(path, amr_nx_graph.to_undirected())
				break
			break
		break
		#print this path along with the edge labels
		#similary print the dependency path along with the edge labels
		#if both paths contain any of the interaction_terms, then add such an interaction
