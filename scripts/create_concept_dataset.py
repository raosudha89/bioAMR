import sys
import cPickle as pickle
import networkx as nx
import string

def traverse_depth_first(concept_nx_graph, parent=None):
	node_list = [] #list of pairs (concept_instance, concept_var_name) e.g. ('establish-01', 'e')
	if parent == None:
		parent = nx.topological_sort(concept_nx_graph)[0]
	node_list.append((concept_nx_graph.node[parent]['instance'], parent))
	children = []
	for child in concept_nx_graph.successors(parent):
		if concept_nx_graph.node[child]['parent'] == parent:
			children.append(child)
	if not children:
		return node_list
	ordered_children = [None]*len(children)
	order = []
	for child in children:
		order.append(concept_nx_graph.node[child]['child_num'])
	diff = max(order) + 1 - len(order)
	for child in children:
		ordered_children[concept_nx_graph.node[child]['child_num'] - diff] = child
	for child in ordered_children:
		node_list.extend(traverse_depth_first(concept_nx_graph, parent=child)) 
	return node_list		

def create_training_data(sentence, span_concept):
	training_data = []
	words = sentence.split()
	i = 0
	while i < len(words):
		span_start = str(i)
		if span_concept.has_key(span_start):
			span_end, span, concept_nx_graph = span_concept[span_start]
			node_list = traverse_depth_first(concept_nx_graph)
			labels = []
			concept_short_names = []
			for (concept_instance, concept_var_name) in node_list:
				labels.append(concept_instance)
				concept_short_names.append(concept_var_name)
			label = "_".join(labels)
			concept_short_name = "_".join(concept_short_names)
			training_data.append([" ".join(span), label, concept_short_name)
			i = int(span_end) 
		else:
			training_data.append([words[i], "NULL", "NULL")
			i += 1
	return training_data

visited_nodes = []

def get_node_paths(parent_path, parent, amr_nx_graph):
	#print parent_path
	if parent in visited_nodes:
		return {}
	visited_nodes.append(parent)
	if not amr_nx_graph.successors(parent):
		return {}
	node_paths = {}
	for child in amr_nx_graph.successors(parent):
		child_path = parent_path + '.' + str(amr_nx_graph.node[child]['child_num'])
		node_paths[child_path] = child
		#print node_list
		node_paths.update(get_node_paths(child_path, child, amr_nx_graph))
	return node_paths


forced_alignments = {} # Dictionary: key=instance of node; value=dict with counts of spans aligned to this node in data
my_stopwords = list(string.punctuation) + ['the', 'a', 'to', 'of', 'are', 'is', 'was']

def get_missing_alignment_data(root, amr_nx_graph, alignments, sentence):
	sent_len = len(sentence.split())
	spans = []
	for i in range(1, sent_len):
		spans.append(str(i-1) + "-" + str(i))
	node_paths = {"0": root}
	node_paths.update(get_node_paths("0", root, amr_nx_graph))
	aligned_node_paths = []
	aligned_spans = []
	for alignment in alignments.split():
		span, graph_fragments = alignment.split("|")
		aligned_spans.append(span)
		aligned_node_paths += graph_fragments.split("+")
	#print aligned_spans
	#print spans
	for node_path in node_paths.keys():
		if node_path not in aligned_node_paths:
			node_instance = amr_nx_graph.node[node_paths[node_path]]['instance']
			if node_instance == "multi-sentence":
				continue #since we handle these nodes differently
			if not forced_alignments.has_key(node_instance):
				forced_alignments[node_instance] = {}
			for span in spans:
				if span not in aligned_spans:
					span_start, span_end = span.split('-')
					span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
					if span_words in my_stopwords:
						continue
					if not forced_alignments[node_instance].has_key(span_words):
						forced_alignments[node_instance][span_words] = 0
					forced_alignments[node_instance][span_words] += 1


def add_missing_alignments(root, amr_nx_graph, alignments, sentence):
	sent_len = len(sentence.split())
	spans = []
	for i in range(1, sent_len):
		spans.append(str(i-1) + "-" + str(i))
	node_paths = {"0": root}
	node_paths.update(get_node_paths("0", root, amr_nx_graph))
	aligned_node_paths = []
	aligned_spans = []
	for alignment in alignments.split():
		span, graph_fragments = alignment.split("|")
		aligned_spans.append(span)
		aligned_node_paths += graph_fragments.split("+")
	new_alignments = []
	for node_path in node_paths.keys():
		if node_path not in aligned_node_paths:
			node_instance = amr_nx_graph.node[node_paths[node_path]]['instance']
			if node_instance == "multi-sentence":
				continue #since we handle these nodes differently
			max_count = 0
			most_aligned_span = ""
			most_aligned_span_words = ""
			unaligned_spans = []
			for span in spans:
				if span not in aligned_spans:
					unaligned_spans.append(span)
					span_start, span_end = span.split('-')
					span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
					if span_words in my_stopwords:
						continue
					count = forced_alignments[node_instance][span_words]
					if count > max_count:
						max_count = count
						most_aligned_span = span
						most_aligned_span_words = span_words
			if not unaligned_spans:
				continue
			if max_count == 0:
				span = unaligned_spans[0]
				most_aligned_span = span
				span_start, span_end = span.split('-')
				most_aligned_span_words = " ".join(sentence.split()[int(span_start):int(span_end)])
			new_alignments.append(most_aligned_span + "|" + node_path)
			print "NEW ALIGNMENT: ", node_instance, most_aligned_span_words
	return alignments + " " +  " ".join(new_alignments)

def get_span_concept(alignment, root, amr_nx_graph, sentence):
	span_num, graph_fragments = alignment.split("|")
	span_start, span_end = span_num.split("-")
	span = sentence.split()[int(span_start):int(span_end)]
	#Create a concept networkx graph and add all nodes in graph_fragments
	concept_nx_graph = nx.DiGraph()
	for graph_fragment in graph_fragments.split("+"):
		parent, attr_dict = root, amr_nx_graph.node[root]
		for child_num in graph_fragment.split(".")[1:]:
			children = amr_nx_graph.successors(parent)
			for child in children:
				if amr_nx_graph.node[child]['parent'] == parent and amr_nx_graph.node[child]['child_num'] == int(child_num):
					parent, attr_dict = child, amr_nx_graph.node[child]
		concept_nx_graph.add_node(parent, attr_dict)
	#Get all edges between the nodes in graph_fragment and add those to concept_nx_graph
	nodes = concept_nx_graph.nodes()
	for i in range(len(nodes)):
		for j in range(i + 1, len(nodes)):
			if amr_nx_graph.has_edge(nodes[i], nodes[j]):
				concept_nx_graph.add_edge(nodes[i], nodes[j], amr_nx_graph.get_edge_data(nodes[i], nodes[j]))
			if amr_nx_graph.has_edge(nodes[j], nodes[i]):
				concept_nx_graph.add_edge(nodes[j], nodes[i], amr_nx_graph.get_edge_data(nodes[j], nodes[i]))
	return (span_start, [span_end, span, concept_nx_graph])	


def get_training_dataset(amr_nx_graphs):
	training_dataset = {}
	print "######"
	for id, value in amr_nx_graphs.iteritems():
		[root, amr_nx_graph, sentence, alignments] = value
		get_missing_alignment_data(root, amr_nx_graph, alignments, sentence)

	for id, value in amr_nx_graphs.iteritems():
		print id
		span_concept = {}
		[root, amr_nx_graph, sentence, alignments] = value
		alignments = add_missing_alignments(root, amr_nx_graph, alignments, sentence)
		for alignment in alignments.split():
			span, concept = get_span_concept(alignment, root, amr_nx_graph, sentence)
			span_concept[span] = concept
		training_dataset[id] = create_training_data(sentence, span_concept)
	return training_dataset

def main(argv):
	if len(argv) < 1:
		print "usage: python create_concept_dataset.py <amr_nx_graphs.p>"
		return
	amr_nx_graphs_p = argv[0]
	#Format of amr_nx_graphs
	#amr_nx_graphs = {id : [root, amr_nx_graph, sentence, alignment]}
	amr_nx_graphs = pickle.load(open(amr_nx_graphs_p, "rb"))


	training_dataset = get_training_dataset(amr_nx_graphs)
	print_to_file = True
	if print_to_file:
		for id, training_data in training_dataset.iteritems():
			print id
			for data in training_data:
				print data
			print
	pickle.dump(training_dataset, open("concept_dataset.p", "wb"))

if __name__ == "__main__":
	main(sys.argv[1:])
