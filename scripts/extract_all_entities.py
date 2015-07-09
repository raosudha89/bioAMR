import sys, os
import json
import pickle

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: extract_all_entities.py biopax_model_index_cards_dir")
		sys.exit(0)

	biopax_model_index_cards_dir = sys.argv[1]
	entities = []
	for root, directories, filenames in os.walk(biopax_model_index_cards_dir):
		for json_file in filenames:
			index_card = json.loads(open(os.path.join(root, json_file)).read())
			if index_card["extracted_information"]["participant_a"]:
				if "entity_text" in index_card["extracted_information"]["participant_a"]:
					entity = str(index_card["extracted_information"]["participant_a"]["entity_text"])
					if entity not in entities:
						entities.append(entity)
			if index_card["extracted_information"]["participant_b"]:
				if "entity_text" in index_card["extracted_information"]["participant_b"]:
					entity = str(index_card["extracted_information"]["participant_b"]["entity_text"])
					if entity not in entities:
						entities.append(entity)

	for entity in entities:
		print(entity.rstrip("\n"))
	pickle.dump(entities, open("output/entities.p", "wb"))
	
