import sys

amr_out_file = open(sys.argv[1])
amr_formatted_out_file = open(sys.argv[2], 'w')

def get_formatted_lines(line):
	formatted_lines = []
	parts = line.split(":")
	tabs_dict = {}
	curr_tab_count = 0
	formatted_lines.append(parts[0])
	for i in range(1, len(parts)):
		if parts[i-1].strip()[-1] != ")":
			curr_tab_count += 1
			if curr_tab_count <= 0:
				curr_tab_count = 1
			formatted_lines.append("\t"*curr_tab_count + ":" + parts[i])
		else:
			if curr_tab_count <= 1:
				curr_tab_count += 1
			s = parts[i-1].strip()
			while s[-1] == ")":
				curr_tab_count -= 1
				s = s[:-1].strip()
			if curr_tab_count <= 0:
				curr_tab_count = 1
			formatted_lines.append("\t"*curr_tab_count + ":" + parts[i])
	return formatted_lines

for line in amr_out_file.readlines():
	if line.startswith("("):
		formatted_lines = get_formatted_lines(line)
		for formatted_line in formatted_lines:
			amr_formatted_out_file.write(formatted_line + "\n")
	else:
		amr_formatted_out_file.write(line)
	
