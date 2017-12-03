from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return """
Available API endpoints:<br>
GET /containers                     List all containers<br>
GET /containers?state=running       List running containers (only)<br>
GET /containers/<id>                Inspect a specific container<br>
GET /containers/<id>/logs           Dump specific container logs<br>
GET /images                         List all images<br>
POST /images                        Create a new image<br>
POST /containers                    Create a new container<br>
PATCH /containers/<id>              Change a container's state<br>
PATCH /images/<id>                  Change a specific image's attributes<br>
DELETE /containers/<id>             Delete a specific container<br>
DELETE /containers                  Delete all containers (including running)<br>
DELETE /images/<id>                 Delete a specific image<br>
DELETE /images                      Delete all images<br>
"""


@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers

    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool
    """
    if request.args.get('state') == 'running': 
        output = docker('ps')
        resp = json.dumps(docker_ps_to_array(output))
    else:
        output = docker('ps', '-a')
        resp = json.dumps(docker_ps_to_array(output))

    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/images', methods=['GET'])
def images_index():
    """
    List all images
    """
    output = docker('images')
    resp = json.dumps(docker_images_to_array(output))
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
    """
    Inspect specific container
    """
    output = docker('inspect', id)
    resp = json.dumps(output) #could do json.dumps(docker_logs_to_object(id, output)) but not necessary
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
    """
    Dump specific container logs
    """
    output = docker('logs', id)
    resp = json.dumps(docker_ps_to_array(output))
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/services', methods=['GET'])
def servicess_index():
    """
    List all services
    """
    output = docker('service', 'ls')
    resp = json.dumps(docker_services_to_array(output))
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/nodes', methods=['GET'])
def nodes_index():
    """
    List all containers

    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool
    """
    output = docker('node', 'ls')
    resp = json.dumps(docker_nodes_to_array(output))

    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
    """
    Delete a specific image
    """
    docker ('rmi', id)
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")


@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
    """
    Delete a specific container - must be already stopped/killed
    """
    docker('stop', id)
    docker('rm', id)
    resp = '{"id": "%s"}' % id
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
    """
    Force remove all containers - dangrous!
    """
    output = docker('ps', '-a')
    containers = docker_ps_to_array(output)
    containerIDs = []
    for container in containers:
         id = container['id']
         docker('stop', id)
         docker('rm', '-f', id)
         containerIDs.append('{"id" : "%s"}' % id)
    resp = json.dumps(containerIDs)
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/images', methods=['DELETE'])
def images_remove_all():
    """
    Force remove all images - dangrous!
    """
    output = docker('image', 'ls')
    images = docker_images_to_array(output)
    for image in images:
         id = image['id']
         docker('rmi', '-f', id)
    resp = json.dumps(images)
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['POST'])
def containers_create():
    """
    Create container (from existing image using id or name)
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "my-app"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'
    """
    body = request.get_json(force=True)
    image = body['image']
    args = ('run', '-d')

    if 'publish' in body:
         publish = body['publish']
         #docker run -d -p 8080:8080 9e7424e5dbae
         id = docker('run', '-d', '-p', publish, image)
    else:
         #docker run -d test
         id = docker ('run', '-d', image)

    return Response(response='{"id": "%s"}' % id, mimetype="application/json")


@app.route('/images', methods=['POST'])
def images_create():
    """
    Create image (from uploaded Dockerfile)
    curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images
    """
    dockerfile = request.files['file']
    #????????????????????????????????????????????????????????
    # How am I meant to test this? the curl sends a file?   ?
    # What?                                                 ?
    #????????????????????????????????????????????????????????

    output = docker('build', '-t', 'newImage', dockerfile)
    resp = json.dumps(output)
    #resp = ''
    return Response(response=resp, mimetype="application/json")


@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
    """
    Update container attributes (support: state=running|stopped)
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'
    """
    body = request.get_json(force=True)
    try:
        if 'state' in body:
             state = body['state']
             if state == 'running':
                  docker('restart', id)
             if state == 'stopped':
                  docker('stop', id)

        if 'name' in body:
             name = body['name']
             docker('rename', id, name) 
    except:
        pass

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")


@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
    """
    Update image attributes (support: name[:tag])  tag name should be lowercase only
    curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/7f2619ed1768 -d '{"tag": "test:1.0"}'
    """
    body = request.get_json(force=True)
    try:
         if 'tag' in body:
              tag = body['tag']
              docker('tag', id, tag)
    except:
        pass
    resp = '{"id" : "%s"}' % id
    return Response(response=resp, mimetype="application/json")


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith('Error'):
        print 'Error: {0} -> {1}'.format(' '.join(cmd), stderr)
    return stderr + stdout


#
# Docker output parsing helpers
#
#
# Parses the output of a Docker PS command to a python List
#
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['image'] = c[1]
        each['name'] = c[-1]
        each['ports'] = c[-2]
        all.append(each)
    return all


#
# Parses the output of a Docker Services ls command to a python List
#
def docker_services_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['name'] = c[1]
        each['mode'] = c[2]
        each['replicas'] = c[3]
	each['image'] = c[4]
	each['ports'] = c[5]
        all.append(each)
    return all


#
# Parses the output of a Docker Services ls command to a python List
#
def docker_nodes_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
	each = {}
	if len(c) > 4:
             each['id'] = c[0]
	     each['hostname'] = c[2]
             each['status'] = c[3]
             each['availability'] = c[4]
             each['manager_status'] = c[5]
        else:
             each['id'] = c[0]
             each['hostname'] = c[1]
             each['status'] = c[2]
             each['availability'] = c[3]
        all.append(each)
    return all


#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs


#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2]
        each['tag'] = c[1]
        each['name'] = c[0]
        all.append(each)
    return all


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
