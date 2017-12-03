import requests
import sys
import json


########### EXAMPLE ARGUEMENTS ##########
#					#
#	python3 run.py [IP]		#
#	python3 run.py 104.199.100.76	#
#					#
#########################################

def main(args):
	print(args)
	url = 'http://' + args[1] + '/'
	containerInspectID = input('Inspect Container ID: ')
	containerLogsID = input('Logs Container ID: ')
	containerCreateImageID = input('Image ID for Create Container: ')
	containerCreateImageName = input('Image Name for Creae Container: ')
	containerCreatePort = input('Port for Create Container: ')
	containerPatchID = input('Container ID to update: ')
	imagePatchID = input('Image ID to update: ')


	index(url)
	containers(url)
	containersState(url, '?state=running')
	images(url)
	nodes(url)
	services(url)
	containerInspect(url, containerInspectID)
	containerLogs(url, containerLogsID)
	createContainer(url, '{"image" : "%s"}' % containerCreateImageID)
	createContainer(url, '{"image" : "%s"}' % containerCreateImageName)
	createContainer(url, '{"image" : "%s", "publish" : "%s"}' % (containerCreateImageName,containerCreatePort) )
	containerPatch(url, containerPatchID, '{"state": "stopped"}')
	containerPatch(url, containerPatchID, '{"state": "running", "name" : "ThisIsTheName"}')	
	imagePatch(url, imagePatchID, '{"tag" : "%s:0.0.1"}' %containerCreateImageName)

# @app.route('/')
def index(url):
	print("****INDEX****")
	r = requests.get(url)
	print(r.text, end='\n\n')

# @app.route('/containers', methods=['GET'])
def containers(url):
	print("****CONTAINERS****")
	r = requests.get(url + 'containers')
	print(r.json(), end='\n\n')

# @app.route('/nodes', methods=['GET'])
def nodes(url):
        print("****NODES****")
        r = requests.get(url + 'nodes')
        print(r.json(), end='\n\n')

# @app.route('/containers', methods=['GET'])
def services(url):
        print("****SERVICES****")
        r = requests.get(url + 'services')
        print(r.json(), end='\n\n')

# @app.route('/containers?state=running', methods=['GET'])
def containersState(url, state):
	print("****RUNNING CONTAINERS****")
	r = requests.get(url + 'containers' + state)
	print(r.json(), end='\n\n')

# @app.route('/images', methods=['GET'])
def images(url):
	print("****IMAGES****")
	r = requests.get(url + 'images')
	print(r.json(), end='\n\n')

# @app.route('/containers/<id>', methods=['GET'])
def containerInspect(url, id):
	print("****CONTAINER BY ID****")
	r = requests.get(url + 'containers/' + id)
	print(r.json(), end='\n\n')

# @app.route('/containers/<id>/logs', methods=['GET'])
def containerLogs(url, id):
	print("****CONTAINER LOGS BY ID****")
	r = requests.get(url + 'containers/' + id + '/logs')
	print(r.text, end='\n\n')

# @app.route('/containers', methods=['POST'])
def createContainer(url, obj):
	print("****CREATE CONTAINER****")
	print("data being sent: " + obj)
	r = requests.post(url + 'containers', data=obj)
	print(r.text, end='\n\n')

# @app.route('/containers', methods=['PATCH'])
def containerPatch(url, id, obj):
	print("****UPDATE CONTAINER****")
	print("data being sent: " + obj)
	r = requests.patch(url + 'containers/' + id, data=obj)
	print(r.text, end='\n\n')

# @app.route('/containers', methods=['PATCH'])
def imagePatch(url, id, obj):
        print("****UPDATE IMAGE****")
        print("data being sent: " + obj)
        r = requests.patch(url + 'images/' + id, data=obj)
        print(r.text, end='\n\n')

if __name__ == "__main__":
	main(sys.argv)
