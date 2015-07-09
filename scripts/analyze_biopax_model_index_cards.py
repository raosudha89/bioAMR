import sys, os
import json

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: python3 analyze_biopax_model_index_cards.py biopax_model_index_cards_dir")
		sys.exit(0)
	index_cards_dir = sys.argv[1]
	no_of_cards = 0
	entities = []
	entity_pairs = []
	entity_pairs_directional = []
	interaction_types = []
	interactions = []
	for root, directories, filenames in os.walk(index_cards_dir):
		for filename in filenames:
			index_card = json.loads(open(os.path.join(root, filename)).read())
			no_of_cards += 1
			if index_card["extracted_information"]["participant_a"]:
				if "entity_text" in index_card["extracted_information"]["participant_a"]:
					entity_a = str(index_card["extracted_information"]["participant_a"]["entity_text"])
			if index_card["extracted_information"]["participant_b"]:
				if "entity_text" in index_card["extracted_information"]["participant_b"]:
					entity_b = str(index_card["extracted_information"]["participant_b"]["entity_text"])

			if entity_a not in entities:
				entities.append(entity_a)
			if entity_b not in entities:
				entities.append(entity_b)
			if (entity_a, entity_b) not in entity_pairs and (entity_b, entity_a) not in entity_pairs:
				entity_pairs.append((entity_a, entity_b))
			if (entity_a, entity_b) not in entity_pairs_directional:
				entity_pairs_directional.append((entity_a, entity_b))

			interaction_type = str(index_card["extracted_information"]["interaction_type"])
			if interaction_type not in interaction_types:
				interaction_types.append(interaction_type)

			interaction = (entity_a, entity_b, interaction_type)
			if interaction not in interactions:
				interactions.append(interaction)

	print("Total number of index cards %d" % no_of_cards)
	print("Total number of entities %d" % len(entities))
	print("Number of unique entity pairs %d" % len(entity_pairs))
	print("Number of unique directional entity pairs %d" % len(entity_pairs_directional))
	print("Kinds of interactions")
	print(interaction_types)
	print("Number of unique interactions %d" % len(interactions))
