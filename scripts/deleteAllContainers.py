import requests
import sys
import json


########### EXAMPLE ARGUEMENTS ######################
#                                                   #
#       python3 DeleteAllImages.py [IP]             #
#       python3 deleteAllImages.py 104.199.100.76   #
#                                                   #
#####################################################

def main(args):
	print(args)
	url = 'http://' + args[1] + '/'
	r = requests.delete(url + 'containers')
	print(r.text)

if __name__ == "__main__":
	main(sys.argv)
