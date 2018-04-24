############ HOW TO RUN ##############
# type:
#..\..\AppData\Local\Programs\Python\Python36-32\python.exe .\ReceiveData.py
# in Powershell inside pylsl-master folder (for personal use)
# Written by James and Kevin



from pylsl import StreamInlet, resolve_stream
import sys
import math
import requests
import os

# first resolve an EEG stream on the lab network
print("looking for an NIRS stream...")
streams = resolve_stream('type', 'NIRS')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])


############## TESTING FUNCTIONS #################
def sensor_average(hemoglobin_values):
	print("\nTimestamp: " + str(hemoglobin_values[0][0]))
	sum_deoxy = float(hemoglobin_values[0][1]) + float(hemoglobin_values[0][3]) +float(hemoglobin_values[0][5]) + float(hemoglobin_values[0][7]) + float(hemoglobin_values[0][9]) + float(hemoglobin_values[0][11]) + float(hemoglobin_values[0][13]) + float(hemoglobin_values[0][15]) +float(hemoglobin_values[0][17])
	sum_oxy = float(hemoglobin_values[0][2]) + float(hemoglobin_values[0][4]) +float(hemoglobin_values[0][6]) + float(hemoglobin_values[0][8]) + float(hemoglobin_values[0][10]) + float(hemoglobin_values[0][12]) + float(hemoglobin_values[0][14]) + float(hemoglobin_values[0][16]) + float(hemoglobin_values[0][18])
	return (sum_deoxy/8), (sum_oxy/8)

def time_average(hemoglobin_values, secs):
	deoxy = 0
	oxy = 0
	for x in range(secs):
			temp1, temp2 = sensor_average(hemoglobin_values)
			deoxy += temp1
			oxy += temp2
	print("DEOXY: "+ str(deoxy/secs) + "\n" + "OXY: "+ str(oxy/secs) + "\n")

# CURERENTLY USING test_print FOR -p parameter
def test_print(hemoglobin_values):
	print ("Timestamp: " + str(hemoglobin_values[1]))
	# Commented out unused channels
	print (str(hemoglobin_values[0][1]) + "\t" + str(hemoglobin_values[0][2]))# + "\t" + str(hemoglobin_values[0][3]) + "\t" + str(hemoglobin_values[0][4]))
	#print (str(hemoglobin_values[0][5]) + "\t" + str(hemoglobin_values[0][6]) + "\t" + str(hemoglobin_values[0][7]) + "\t" + str(hemoglobin_values[0][8]))
	#print (str(hemoglobin_values[0][9]) + "\t" + str(hemoglobin_values[0][10]) + "\t" + str(hemoglobin_values[0][11]) + "\t" + str(hemoglobin_values[0][12]))
	#print (str(hemoglobin_values[0][13]) + "\t" + str(hemoglobin_values[0][14]) + "\t" + str(hemoglobin_values[0][15]) + "\t" + str(hemoglobin_values[0][16]))
	#print (str(hemoglobin_values[0][17]) + "\t" + str(hemoglobin_values[0][18]) + "\t" + str(hemoglobin_values[0][19]) + "\t" + str(hemoglobin_values[0][20]))
	#print (str(hemoglobin_values[0][21]) + "\t" + str(hemoglobin_values[0][22]) + "\t" + str(hemoglobin_values[0][23]) + "\t" + str(hemoglobin_values[0][24]))
	print ("\n")

################# SLOPE ALGORITHM ######################

#Try to get certain amount of readings in 1 sec based on sampling rate
def mean_slope(sample_arr):
	final_arr = [0] * len(sample_arr)
	for x in range (len(sample_arr)):
		for y in range (int(x) + 1):
			final_arr[x] += sample_arr[y]
			sum = final_arr[x]
		final_arr[x] /= x+1

	return avg_mean_slope(final_arr)

def avg_mean_slope(mean_arr):
	sum = 0
	length = len(mean_arr)
	for x in range(length):
		sum += mean_arr[x]
	return sum / length


############### CONFIGURATION FUNCTION ###################
def configuration(filename):
	start = True
	Agg_arr = []
	arr = []
	slope = 0
	max_slope = 0
	first = True
	curr_time = 0
	first_time = 0
	prev_time = 0
	extra_val = False

	try:
		myfile = open(filename, "a")
	except IOError:
		print("\nERROR:\n\tFile does not exist or cannot be opened\n")
		exit()
	try:
		while start:
			# Pull streaming data
			sample = inlet.pull_sample()
		    ######################################
		    ##### GET ARRAY OF SAMPLE VALUES #####
		    ######################################

			print(str(sample[0][1]))
			prev_time = curr_time
			curr_time = (int(sample[1]))
			if first == True:
				first_time = (int(sample[1]))
				first = False
			if first_time == curr_time:
				print("NOT CALCULATING")
			if first_time != curr_time:
				arr.append(sample[0][1])
				if len(arr) == 8:
					if prev_time == curr_time:
						extra_val = False
						pass
					elif prev_time == curr_time - 1:
						extra_val = True
						temp_data = arr[7]
						arr.pop(7)
					Agg_arr.append(mean_slope(arr))
					print ("Timestamp: " + str(sample[1]))
					print("Mean slope value: " + str(mean_slope(arr)) + "\n")

					if len(Agg_arr) > 9:
						Agg_arr.sort()
						print(Agg_arr)
						slope = (Agg_arr[9] - Agg_arr[0]) / 2
						if max_slope < slope:
							max_slope = slope
							print("MAX SLOPE HAS CHANGED TO: " + str(max_slope) + "\n")
						else:
							print("NO CHANGE, SLOPE WAS: " + str(slope) + "\n")
						Agg_arr = []
					arr = []
					if extra_val == True:
						arr.append(temp_data)
	except KeyboardInterrupt:
		# Have a user input to end config and add max slope to file
		print("Program ending...\n\n")
		myfile.write(str(max_slope) + "\n")
		myfile.close()
		print("Program ended successfully!\n\n")
		exit()

	



################## EXEPERIMENT FUNCTION ####################
def experiment(filename):
# Slope calculations: every 10s
	start = True
	Agg_arr = []
	arr = []
	file_arr = []
	slope = 0
	max_slope = 0
	first = True
	curr_time = 0
	first_time = 0
	prev_time = 0
	extra_val = False

	#### SET THRESHOLD ####
	try:
		myfile = open(filename, "r")
	except IOError:
		print("\nERROR:\n\tFile does not exist or cannot be opened\n")
		exit()
	with myfile:
		myfile_read = myfile.readlines()
		for x in myfile_read:
			file_arr.append(float(x))
		file_arr.sort()
		threshold_slope = file_arr[0]
		print("\nSLOPE THRESHOLD: " + str(threshold_slope) + "\n")

	try:
		while start:
			# Pull streaming data
			sample = inlet.pull_sample()

		    ######################################
		    ##### GET ARRAY OF SAMPLE VALUES #####
		    ######################################

			print(str(sample[0][1]))
			prev_time = curr_time
			curr_time = (int(sample[1]))
			if first == True:
				first_time = (int(sample[1]))
				first = False
			if first_time == curr_time:
				print("NOT CALCULATING")
			if first_time != curr_time:
					arr.append(sample[0][1])
					if len(arr) == 8:
						if prev_time == curr_time:
							extra_val = False
							pass
						elif prev_time == curr_time - 1:
							extra_val = True
							temp_data = arr[7]
							arr.pop(7)
						Agg_arr.append(mean_slope(arr))
						print ("Timestamp: " + str(sample[1]))
						print("Mean slope value: " + str(mean_slope(arr)) + "\n")
						
						if len(Agg_arr) > 9:
							Agg_arr.sort()
							print(Agg_arr)
							slope = (Agg_arr[9] - Agg_arr[0]) / 2
							if max_slope < slope:
								max_slope = slope
								print("MAX SLOPE HAS CHANGED TO: " + str(max_slope) + "\n")
							else:
								print("NO CHANGE, SLOPE WAS: " + str(slope) + "\n")
							Agg_arr = []
						arr = []
						if extra_val == True:
							arr.append(temp_data)

					################### send server activation ##################
					if threshold_slope < max_slope:
						r = requests.post(os.environ.get('URL'), data = {'signal': 1})
						print("\n\nACTIVATION!")
						start = False
						exit()
	except KeyboardInterrupt:
		# Have a user input to end config and add max slope to file
		print("Program ending...\n\n")
		myfile.close()
		print("Program ended successfully!\n\n")
		exit()


		

			
			

	#except KeyboardInterrupt:
	#	# Have a user input to end config and add max slope to file
	#	print("Program ending...\n\n")
	#	myfile.write(str(max_slope))
	#	myfile.close()
	#	print("Program ended successfully!\n\n")
	#	exit()

###################### MAIN FUNCTION ######################
# First input is always the script
# 3 inputs for configuration
#		second input: c (configuration) (writing)
#		third input: a txt file that contains one slope threshold value
#
#		second input: e (experiment) (reading)
#		third input: a txt file that contains one slope threshold value
#		
# 2 inputs
#		second input: p (print data) (for testing purposes)
#		

total = len(sys.argv)
time = 0;
if total == 2:
	if sys.argv[1] != "-p":
		print("\nUSAGE: \n\t[-p] for priting\n\t[-c] [file] for config \n\t[-e] [file] for experiment\n")
		exit()
	else:
		first = True;
		while True:
			sample = inlet.pull_sample()
			test_print(sample)
elif total == 3:
	if sys.argv[1] != "-c" and sys.argv[1]!= "-e":
		print("\nUSAGE: \n\t[-p] for priting\n\t[-c] [file] for config \n\t[-e] [file] for experiment\n")
		exit()
	else:
		if sys.argv[1] == "-c":
			configuration(sys.argv[2])

		else:
			experiment(sys.argv[2])
else: 
	print("\nUSAGE: \n\t[-p] for priting\n\t[-c] [file] for config \n\t[-e] [file] for experiment\n")
	exit()

print("\nDONE!\n")


