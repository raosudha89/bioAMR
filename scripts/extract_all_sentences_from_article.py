import sys, os
import xml
from nltk.tokenize import sent_tokenize

def remove_xml_node(root, node_type):
	for node in root.findall(node_type):
		tail = node.tail
		node.clear()
		node.tail = tail

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("usage: python extract_all_sentences_from_article.py article output_dir")
		sys.exit(0)

	article = open(sys.argv[1], 'r')
	output_dir = sys.argv[2]
	output_file = open(os.path.join(output_dir, sys.argv[1] + ".sentences"), 'w')
	
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
			sent = str(sent)
			output_file.write(sent)
			output_file.write("\n")
