import sys, os
import re
import networkx as nx
import pyparsing
#import cPickle as pickle
import pickle

nodes = []
relations = []
amr_nx_graph = None

def add_edge(node_A, node_B):
	global relations
	global amr_nx_graph
	if amr_nx_graph.has_node(node_A) and amr_nx_graph.has_node(node_B) and relations:
		relation = relations.pop()
		amr_nx_graph.add_edge(node_A, node_B, relation=relation)

def get_all_nodes(amr_graph_as_list):
	global nodes
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			nodes.append(node)
		elif isinstance(element, list):
			get_all_nodes(element)

def add_to_nx_graph(amr_graph_as_list, prev_level_root=None, prev_level_child_num=0, pass_num=1):
	global nodes
	global relations
	global amr_nx_graph
	current_root = None
	curr_level_child_num = 0
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			instance = amr_graph_as_list[i + 1]
			amr_nx_graph.add_node(node, instance=instance, child_num=prev_level_child_num, parent=prev_level_root)
			add_edge(prev_level_root, node)
			current_root = node
			curr_level_child_num = 0
		elif isinstance(element, list):
			add_to_nx_graph(element, current_root, curr_level_child_num)
			curr_level_child_num += 1
		elif element[0] == ":":
			relations.append(element[1:])
		else:
			if i - 1 >= 0 and amr_graph_as_list[i - 1] == '/' or i + 1 < len(amr_graph_as_list) and amr_graph_as_list[i + 1] == '/':
				pass
			else:
				if element not in nodes:
					node = current_root + ":" + str(curr_level_child_num) + ":" + element
					amr_nx_graph.add_node(node, instance=element, child_num=curr_level_child_num, parent=current_root)
					curr_level_child_num +=1
					add_edge(current_root, node)
					nodes.append(node)
				else:
					add_edge(current_root, element)
	return current_root

def update_nx_graph(amr_graph_as_list, prev_level_root=None, prev_level_child_num=0):
	global nodes
	global relations
	global amr_nx_graph
	current_root = None
	curr_level_child_num = 0
	for i in range(len(amr_graph_as_list)):
		element = amr_graph_as_list[i]
		if element == '/':
			node = amr_graph_as_list[i - 1]
			current_root = node
			curr_level_child_num = 0
		elif isinstance(element, list):
			update_nx_graph(element, current_root, curr_level_child_num)
			curr_level_child_num += 1
		elif element[0] == ":":
			pass
		else:
			if i - 1 >= 0 and amr_graph_as_list[i - 1] == '/' or i + 1 < len(amr_graph_as_list) and amr_graph_as_list[i + 1] == '/':
				pass
			else:
				if element not in nodes:
					node = current_root + ":" + str(curr_level_child_num) + ":" + element
					amr_nx_graph.add_node(node, instance=element, child_num=curr_level_child_num, parent=current_root)
					curr_level_child_num +=1
					add_edge(current_root, node)
					nodes.append(node)
				else:
					add_edge(current_root, element)
	return current_root

def main(argv):
	if len(argv) < 1:
		print "usage: amr_reader.py <amr_file>"
		return
	amr_aligned = open(argv[0])
	ids = []
	sentences = []
	alignments = []
	amr_graphs = []
	line = amr_aligned.readline()
	while (line != ""):
		if line.startswith("# ::id"):
			ids.append(line.split("::")[1].strip("# ::id").strip())
		if line.startswith("# ::tok"):
			sentences.append(line.strip("# ::tok").strip("\n"))
		elif line.startswith("# ::snt"):
			sentences.append(line.strip("# ::snt").strip("\n"))
		elif line.startswith("# ::alignments"):
			alignments.append(line.split("::")[1].strip("# ::alignments"))
		elif line.strip().startswith("("):
			amr_graph = line.strip(" \n")
			line = amr_aligned.readline()
			line = line.strip()
			while(line != ""):
				amr_graph +=  " " + line
				line = amr_aligned.readline()
				line = line.strip()
			amr_graphs.append(amr_graph)
		line = amr_aligned.readline()

	amr_nx_graphs = {}
	print_to_file = 1
	for i in range(len(amr_graphs)):
		global amr_nx_graph
		amr_nx_graph = nx.MultiDiGraph()
		global nodes
		nodes = []	
		global relations
		relations = []
		parens = pyparsing.nestedExpr('(', ')')
		amr_graph_as_list = parens.parseString(amr_graphs[i]).asList()
		get_all_nodes(amr_graph_as_list[0])
		root = add_to_nx_graph(amr_graph_as_list[0])
		#update_nx_graph(amr_graph_as_list[0])
		if print_to_file:
			print ids[i]
			print sentences[i]
			print root
			print amr_nx_graph.nodes(data=True)
			print amr_nx_graph.edges(data=True)
			print
		if not alignments:
			amr_nx_graphs[ids[i]] = [root, amr_nx_graph, sentences[i]]
		else:
			amr_nx_graphs[ids[i]] = [root, amr_nx_graph, sentences[i], alignments[i]]
	pickle.dump(amr_nx_graphs, open("data/" + os.path.splitext(os.path.basename(argv[0]))[0] + ".amr_nx_graphs.p", "wb"))

if __name__ == "__main__":
    main(sys.argv[1:])
