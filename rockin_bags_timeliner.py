#!/usr/bin/python

import sys, os
import subprocess, yaml
import rosbag
from datetime import datetime


class colors:
	NORMAL = ''
	WARNING = '\033[93m'
	OK = '\033[92m'
	HIGHLIGHT = '\033[94m\033[1m'
	ERROR = '\a\033[91m'
	END = '\033[0m'


if len(sys.argv) < 2:
	print "The following arguments must be provided: rockin_bags_timeliner.py {bags_directory}+\n\tbags_directory:\ta directory containing bags"
	sys.exit(1)

bags_dir_list = sys.argv[1:]

## find all the bags

print colors.NORMAL + "\tSelecting bags..." + colors.END
bags_pos_list = []
for bags_dir in bags_dir_list:
	bags_pos_list = bags_pos_list + \
		[os.path.join(root, name)
		 for root, dirs, files in os.walk(bags_dir)
		 for name in files
		 if name.endswith((".bag", ".bag.active"))]

print colors.NORMAL + "\tBags selected:" + colors.END
for e in bags_pos_list:
	if bags_pos_list.count(e)>1:
		print colors.WARNING + "[WARNING: duplicated name] " + e + colors.END
	else:
		print colors.NORMAL + e + colors.END


print colors.NORMAL + "\tObtaining bags' info..." + colors.END
bags_stdout_info_list = subprocess.Popen(['rosbag', 'info', '--yaml']+bags_pos_list, stdout=subprocess.PIPE).communicate()[0].split("\n\n---\n")

bags_info_list = []
for bag_stdout_info in bags_stdout_info_list:
	bag_info = yaml.load(bag_stdout_info)
	if not 'start' in bag_info.keys():
		print colors.ERROR + "%s doesn't contain start timestamp" % bag_pos + colors.END
	else:
		bags_info_list.append(bag_info)

print colors.NORMAL + "\tObtained  bags' info" + colors.END

#bags_info_list = []
#for bag_pos in bags_pos_list:
#	bag_info = get_bag_info(bag_pos)
#	if bag_info and 'start' in bag_info.keys(): bags_info_list.append(get_bag_info(bag_pos))
#	else: print colors.ERROR + "%s doesn't contain start timestamp" % bag_pos + colors.END

print colors.NORMAL + "\tSorting bags' info..." + colors.END
bags_info_list_s = sorted(bags_info_list, key=lambda bag_info: bag_info['start'])
print colors.NORMAL + "\tSorted  bags' info" + colors.END


print colors.NORMAL + "\tChecking overlaps..." + colors.END
csv = ""
csv = csv + ';'.join(['%20s'%'start', '%20s'%'end', '%12s'%'duration', 'path', 'overlap_list']) + '\n'

print colors.NORMAL + '\n\n' + '\t'.join(['start', 'end', 'duration', 'path', 'overlap_list']) + colors.END

for i in range(0, len(bags_info_list_s)):
	b_i = bags_info_list_s[i]
	
#	if i>0:
#		overlap_prev = b['start'] <= bags_info_list_s[i-1]['end']
#	else: overlap_prev = False
#	if i<len(bags_info_list_s)-1:
#		overlap_next =  b['end'] >= bags_info_list_s[i+1]['start']
#	else: overlap_next = False
#	overlap = overlap_prev or overlap_next
#	line = '\t'.join([str(b['start']), str(b['end']), str(b['duration']), b['path'], str(overlap_prev), str(overlap_next)])
	
	overlap_list = []
	for j in range(0, i):
		b_j = bags_info_list_s[j]
		if b_i['end'] < b_j['start']:	print colors.ERROR + "[WHAAAAAT] b_i['end'] < b_j['start']\n\t bags should be ordered so that b_j['start'] <= b_i['start'] ( <= b_i['end'] )" + colors.END
		if b_j['end'] >= b_i['start']:	overlap_list.append(b_j['path'])
	
	line = ';'.join(['%16.3f'%b_i['start'], '%16.3f'%b_i['end'], '%8.3f'%b_i['duration'], '   '+b_i['path'], str(overlap_list)])
	csv = csv + line + '\n'
	
	if len(overlap_list): color = colors.HIGHLIGHT
	else: color = colors.NORMAL
	print  color + line + colors.END

print colors.NORMAL + "\tChecked  overlaps..." + colors.END

filename = "bags_timeline_"+datetime.now().isoformat()+".csv"
with open(filename, 'w') as output_file:
		output_file.write(csv)
		print colors.HIGHLIGHT + "Result dumped in "+filename + colors.END

# bag_info['topics'] structure
# 'topics': [{'topic': '/rockin/adams/command', 'type': 'std_msgs/String', 'messages': 18}, {'topic': '/rockin/adams/image', 'type': 'sensor_msgs/Image', 'messages': 26}, {'topic': '/rockin/adams/marker_pose', 'type': 'geometry_msgs/PoseStamped', 'messages': 1303}, {'topic': '/rockin/adams/robot_pose', 'type': 'geometry_msgs/PoseStamped', 'messages': 1303}, {'topic': '/rockin/adams/scan_0', 'type': 'sensor_msgs/LaserScan', 'messages': 1303}, {'topic': '/rockin/adams/scan_1', 'type': 'sensor_msgs/LaserScan', 'messages': 1303}, {'topic': '/tf', 'connections': 7, 'messages': 45415, 'type': 'tf/tfMessage'}]


