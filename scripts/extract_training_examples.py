import sys, os
import json
import xml
from nltk.tokenize import sent_tokenize
import pickle

def remove_xml_node(root, node_type):
	for node in root.findall(node_type):
		tail = node.tail
		node.clear()
		node.tail = tail

def update_training_set(article, training_examples):
	e = xml.etree.ElementTree.parse(article).getroot()
	for para in e.iter('p'):
		remove_xml_node(para, 'xref')
		remove_xml_node(para, 'sup')
		remove_xml_node(para, 'sub')
		remove_xml_node(para, 'table')
		remove_xml_node(para, 'table-wrap')
		remove_xml_node(para, 'tabel-wrap-foot')
		paragraph = xml.etree.ElementTree.tostring(para, encoding='utf8', method='text')
		paragraph = str(paragraph.decode())
		sents = sent_tokenize(paragraph)
		for sent in sents:
			sent = sent.replace("\n", " ")
			#print(sent)
			sent = str(sent)
			for (a_text, b_text, interaction) in training_examples.keys():
				if a_text in sent and b_text in sent:
					#print("Found!")
					#print(a_text, b_text)
					#print("")
					#print(sent)
					training_examples[(a_text, b_text, interaction)].append(sent)
if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("usage: extract_training_examples.py pubmed_articles_dir biopax_model_json_dir start_letter_of_pubmed_article output_dir")
		sys.exit(0)

	pubmed_articles_dir = sys.argv[1]
	biopax_model_json_dir = sys.argv[2]
	start_letter = sys.argv[3]
	output_dir = sys.argv[4]
	output_file = open(os.path.join(output_dir, "training_examples." + start_letter), 'w')
	training_examples = {}
	for root, directories, filenames in os.walk(biopax_model_json_dir):
		for json_file in filenames:
			a_text = ""
			b_text = ""
			index_card = json.loads(open(os.path.join(root, json_file)).read())
			if index_card["extracted_information"]["participant_a"]:
				if "entity_text" in index_card["extracted_information"]["participant_a"]:
					a_text = str(index_card["extracted_information"]["participant_a"]["entity_text"])
			if index_card["extracted_information"]["participant_b"]:
				if "entity_text" in index_card["extracted_information"]["participant_b"]:
					b_text = str(index_card["extracted_information"]["participant_b"]["entity_text"])
			if a_text == "" or b_text == "":
				continue
			if a_text == b_text:
				continue
			interaction = str(index_card["extracted_information"]["interaction_type"])
			training_examples[(a_text, b_text, interaction)] = []

	for (root, directories, filenames) in os.walk(pubmed_articles_dir):
		for filename in filenames:
			if not filename.startswith(start_letter):
				continue
			article = os.path.join(root, filename)
			if article.endswith('xml'):
				update_training_set(article, training_examples)

	for (k, vs) in training_examples.items():
		if not vs:
			continue
		output_file.write(str(k))
		output_file.write("\n")
		for v in vs:
			output_file.write(str(v))
			output_file.write("\n")
		output_file.write("\n")
	
	pickle.dump(training_examples, open(os.path.join(output_dir, "training_examples." + start_letter + ".p"), "wb"))
	
