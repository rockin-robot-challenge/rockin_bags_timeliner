#!/usr/bin/python

import sys, os
import subprocess, yaml
import rosbag
from datetime import datetime


class colors:
	NORMAL = ''
	WARNING = '\033[93m'
	OK = '\033[92m'
	HIGHLIGHT = '\033[96m'
	ERROR = '\a\033[91m'
	END = '\033[0m'

###	Get summary information about a bag file, specified through the bag's posision;
###	bag_pos:	the position of the bag file
def get_bag_info(bag_pos):
	try:
		if bag_pos.endswith((".bag")):
			return yaml.load(subprocess.Popen(['rosbag', 'info', '--yaml', bag_pos], stdout=subprocess.PIPE).communicate()[0])
	except:
		return None


if len(sys.argv) < 2:
	print "The following arguments must be provided: rockin_bags_timeliner.py {bags_directory}+\n\tbags_directory:\ta directory containing bags"
	sys.exit(1)

bags_dir_list = sys.argv[1:]

## find all the bags

bags_pos_list = []
for bags_dir in bags_dir_list:
	bags_pos_list = bags_pos_list + \
		[os.path.join(root, name)
		 for root, dirs, files in os.walk(bags_dir)
		 for name in files
		 if name.endswith((".bag", ".bag.active"))]

print colors.NORMAL + "bags_pos_list:" + colors.END
for e in bags_pos_list:
	if bags_pos_list.count(e)>1:
		print colors.WARNING + "[WARNING: duplicated name] " + e + colors.END
	else:
		print colors.NORMAL + e + colors.END

bags_info_list = []
for bag_pos in bags_pos_list:
	bag_info = get_bag_info(bag_pos)
	if bag_info and 'start' in bag_info.keys(): bags_info_list.append(get_bag_info(bag_pos))
	else: print colors.ERROR + "%s doesn't contain start timestamp" % bag_pos + colors.END

bags_info_list_s = sorted(bags_info_list, key=lambda bag_info: bag_info['start'])

csv = ""
csv = csv + '\t'.join(['start', 'end', 'duration', 'path', 'overlap_list']) + '\n'

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
		if b_i['end'] < b_j['start']:	print colors.ERROR + "WHAAAAAT: b_i['end'] < b_j['start']\n\t bags should be ordered so that b_j['start'] <= b_i['start'] ( <= b_i['end'] )" + colors.END
		if b_j['end'] >= b_i['start']:	overlap_list.append(b_j['path'])
	
	line = '\t'.join([str(b_i['start']), str(b_i['end']), str(b_i['duration']), b_i['path'], str(overlap_list)])
	csv = csv + line + '\n'
	
	if len(overlap_list): color = colors.HIGHLIGHT
	else: color = colors.NORMAL
	print  color + line + colors.END

with open("outs/timeline_"+datetime.now().isoformat()+".csv", 'w') as output_file:
		output_file.write(csv)

# bag_info['topics'] structure
# 'topics': [{'topic': '/rockin/adams/command', 'type': 'std_msgs/String', 'messages': 18}, {'topic': '/rockin/adams/image', 'type': 'sensor_msgs/Image', 'messages': 26}, {'topic': '/rockin/adams/marker_pose', 'type': 'geometry_msgs/PoseStamped', 'messages': 1303}, {'topic': '/rockin/adams/robot_pose', 'type': 'geometry_msgs/PoseStamped', 'messages': 1303}, {'topic': '/rockin/adams/scan_0', 'type': 'sensor_msgs/LaserScan', 'messages': 1303}, {'topic': '/rockin/adams/scan_1', 'type': 'sensor_msgs/LaserScan', 'messages': 1303}, {'topic': '/tf', 'connections': 7, 'messages': 45415, 'type': 'tf/tfMessage'}]


