import sys, os
import json
import xml
import pickle
import nltk

def get_the_interaction_term(sent, interaction_terms):
	for term in interaction_terms:
		if term in sent:
			return term
	return None

def word_contains_entity(word, entities):
	for entity in entities:
		if entity in word:
			return True
	return False

def get_the_interacting_entities(sent, entities):
	pos_tags = nltk.pos_tag(nltk.word_tokenize(sent))
	not_in_list = False
	prev_entity = None
	for i in range(len(pos_tags)):
		word, tag = pos_tags[i]
		if word_contains_entity(word, entities):
			if prev_entity and not_in_list:
				return (prev_entity, word)
			prev_entity = word
		else:
			if prev_entity:
				if tag not in ['NN', 'NNS', 'NNP', 'NNPS', 'CC', 'DT', ',', ':', '-NONE-']:
					not_in_list = True
	return (None, None)

def is_very_long(sent):
	if len(sent.split(" ")) > 100:
		return True
	for word in sent.split(" "):
		if len(word) > 100:
			return True
	return False

def remove_xml_node(root, node_type):
	for node in root.findall(node_type):
		tail = node.tail
		node.clear()
		#root.remove(node)
		node.tail = tail

def update_training_examples(article, entities, interaction_terms, training_examples):
	e = xml.etree.ElementTree.parse(article).getroot()
	for para in e.iter('p'):
		#print(str(xml.etree.ElementTree.tostring(para, encoding='utf8', method='xml')))
		remove_xml_node(para, 'xref')
		remove_xml_node(para, 'sup')
		remove_xml_node(para, 'sub')
		remove_xml_node(para, 'table')
		remove_xml_node(para, 'table-wrap')
		remove_xml_node(para, 'tabel-wrap-foot')
		#print("AFTER REMOVAL")
		#print(str(xml.etree.ElementTree.tostring(para, encoding='utf8', method='xml')))
		#print("")

		paragraph = xml.etree.ElementTree.tostring(para, encoding='utf8', method='text')
		paragraph = str(paragraph.decode())
		#print(paragraph)
		#print("")
		sents = nltk.tokenize.sent_tokenize(paragraph)
		for sent in sents:
			sent = sent.replace("\n", " ")
			sent = str(sent)
			if is_very_long(sent):
				continue
			interaction_term = get_the_interaction_term(sent, interaction_terms)
			if not interaction_term:
				continue
			entity_A, entity_B = get_the_interacting_entities(sent, entities)
			if not entity_A and not entity_B:
				continue
			else:
				k = (entity_A, entity_B, interaction_term)
				if k not in training_examples:
					training_examples[k] = []
				training_examples[k].append(sent)
				#print(article)
				#print(sent)

if __name__ == "__main__":
	if len(sys.argv) < 6:
		print("usage: extract_training_examples_using_interaction_terms.py pubmed_articles_dir entites_file interaction_terms_file start_letter output_dir")
		sys.exit(0)

	pubmed_articles_dir = sys.argv[1]
	#entities = pickle.load(open(sys.argv[2], 'rb'))
	entities_file = open(sys.argv[2], 'r')
	interaction_terms_file = open(sys.argv[3], 'r')
	start_letter = sys.argv[4]
	output_dir = sys.argv[5]
	training_examples_out_file = open(os.path.join(output_dir, "training_examples." + start_letter), 'w')
	interaction_terms = []
	for line in interaction_terms_file.readlines():
		line = line.strip("\n").strip()
		if line:
			interaction_terms.append(line)
	entities = []
	for line in entities_file.readlines():
		line = line.strip("\n").strip()
		if line:
			entities.append(line)
	training_examples = {}
	for (root, directories, filenames) in os.walk(pubmed_articles_dir):
		for filename in filenames:
			article = os.path.join(root, filename)
			if article.endswith('xml'):
				update_training_examples(article, entities, interaction_terms, training_examples)

	for (k, vs) in training_examples.items():
		if not vs:
			continue
		training_examples_out_file.write(str(k))
		training_examples_out_file.write("\n")
		for v in vs:
			training_examples_out_file.write(str(v))
			training_examples_out_file.write("\n")
		training_examples_out_file.write("\n")
	
	pickle.dump(training_examples, open(os.path.join(output_dir, "training_examples." + start_letter + ".p"), "wb"), protocol=0)
