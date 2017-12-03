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
	containerId = input('Container id to delete: ')
	imageId = input('Image id to delete: ')
	url = 'http://' + args[1] + '/'

	print('****DELETEING CONTAINER****')
	r = requests.delete(url + 'containers/'+ containerId)
	print(r.text)

	print('****DELETEING IMAGE****')
	r = requests.delete(url + 'images/'+ imageId)
	print(r.text)

if __name__ == "__main__":
        main(sys.argv)
