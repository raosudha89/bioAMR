import sys, os
import json
import xml
from nltk.tokenize import sent_tokenize

def update_training_set(article, training_examples):
	e = xml.etree.ElementTree.parse(article).getroot()	
	for para in e.iter('p'):
		try:
			sents = sent_tokenize(para.text)
		except:
			continue
		for sent in sents:
			try:
				sent = str(sent)
				for (a_text, b_text, interaction) in training_examples.keys():
					if a_text in sent and b_text in sent:
						#print "Found!"
						#print sent
						#print a_text, b_text
						#print
						training_examples[(a_text, b_text, interaction)].append(sent)
			except:
				continue
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "usage: create_training_examples.py pubmed_articles_dir biopax_model_json_dir"
		sys.exit(0)

	pubmed_articles_dir = sys.argv[1]
	biopax_model_json_dir = sys.argv[2]
	training_examples = {}
	for json_file in os.listdir(biopax_model_json_dir):
		a_text = ""
		b_text = ""
		index_card = json.loads(open(os.path.join(biopax_model_json_dir, json_file)).read())
		if index_card["extracted_information"]["participant_a"]:
			if "entity_text" in index_card["extracted_information"]["participant_a"]:
				a_text = str(index_card["extracted_information"]["participant_a"]["entity_text"])
		if index_card["extracted_information"]["participant_b"]:
			if "entity_text" in index_card["extracted_information"]["participant_b"]:
				b_text = str(index_card["extracted_information"]["participant_b"]["entity_text"])
		if a_text == "" and b_text == "":
			continue
		interaction = str(index_card["extracted_information"]["interaction_type"])
		training_examples[(a_text, b_text, interaction)] = []

	max_count = 1000000
	count = 0
	for (root, directories, filenames) in os.walk(pubmed_articles_dir):
		for filename in filenames:
			article = os.path.join(root, filename)
			if article.endswith('xml'):
				update_training_set(article, training_examples)
				count += 1
				if count > max_count:
					break
		if count > max_count:
			break
	print article
	for (k, vs) in training_examples.iteritems():
		if not vs:
			continue
		print k
		for v in vs:
			print v
		print

			

