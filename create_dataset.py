import os
dataset_file = "normalized.txt"
dataset1 = 1000000
dataset2 = 2000000
input_dataset = 1000000
if __name__ == "__main__":
	path = os.getcwd() + os.sep + dataset_file
	with open(path, "r") as f:
		lines = f.readlines()
		print "creating dataset1..."
		with open("dataset1", "w") as f_d1:
			f_d1.writelines("".join(lines[:dataset1]))
		print "creating dataset2..."
		with open("dataset2", "w") as f_d2:
			f_d2.writelines("".join(lines[:dataset2]))
		print "creating input dataset..."
		with open("input", "w") as f_i:
			f_i.writelines("".join(lines[len(lines) - input_dataset:]))
		print "all done :)"