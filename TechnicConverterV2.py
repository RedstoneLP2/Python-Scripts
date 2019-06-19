'''
Script to Download and convert Technic launcher modpacks to be Multimc compatible
by RedstoneLP2
'''

import zipfile
import urllib.request
import os
import requests
import shutil
import tempfile
import json
import sys
from urllib.parse import urlparse

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def download(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                sys.stdout.flush()
    sys.stdout.write('\n')

def zipfolder(foldername, target_dir):            
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])

with tempfile.TemporaryDirectory() as tempDir:
	packDir = os.path.join(tempDir, "modpack")
	zipDir = os.path.join(tempDir, "zipdir")
	overrides = os.path.join(packDir, "overrides")
	binDir = os.path.join(zipDir, "bin")
	manifestFile = os.path.join(packDir, "manifest.json")
	modpackjar = os.path.join(tempDir, "bin", "modpack.jar")
	versionJson = os.path.join(tempDir, "bin", "version.json")
	os.mkdir(packDir)
	os.mkdir(overrides)
	os.mkdir(zipDir)

	userurl = input('Enter Pack API URL: ')
	apiurl = userurl + "?build=407"
	req = urllib.request.Request(apiurl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"})
	packinfo = urllib.request.urlopen(req).read()
	pinf = json.loads(packinfo)
	mcver = pinf["minecraft"]

	if pinf["solder"] is None:
		zipurl = pinf["url"]
		solder = False
	else:
		solder = True
		soapiurl = pinf["solder"]

	if solder:
		packver = pinf["version"]
		pname = pinf["name"]
		sopackurl = soapiurl+"modpack/"+pname+"/"+packver
		req = urllib.request.Request(sopackurl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"})
		soinf = urllib.request.urlopen(req).read()
		painf = json.loads(soinf)
		mcver = painf["minecraft"]
		for l in painf["mods"]:
			mod = l["url"]
			filename = urlparse(mod)
			filename = os.path.basename(str(filename))
			filename = filename.replace("', params='', query='', fragment='')", "")
			filename = os.path.join(zipDir, filename)
			print(filename)
			download(mod, filename)
	else:
		zname = os.path.join(zipDir, "modpack.zip")
		download(zipurl, zname)
	
	for file in files(zipDir):
		filepath = os.path.join(zipDir, file)
		zipfile.ZipFile(filepath, "r").extractall(zipDir)
		os.remove(filepath)
	
	shutil.move(binDir, tempDir)

	for dir in os.listdir(zipDir):
		shutil.move(os.path.join(zipDir, dir), overrides)

	try:
		zipfile.ZipFile(modpackjar, "r").extract("version.json", os.path.join(tempDir, "bin"))
		forge = 1
		pass
	except KeyError as e:
		print("Forge not found")
		pass

	if forge == 1:
		with open(versionJson) as versionjson:
			data = json.load(versionjson)
	forgeHeader = data["libraries"][0]["name"]
	forgeHeader = forgeHeader.replace("net.minecraftforge:forge:", "")
	forgever = forgeHeader.replace(mcver, "")

	if forgever[-1:] == "-":
		forgever = forgever[:-1]
	manifestData = '{"minecraft": {"version": "'+mcver+'", "modLoaders": [{"id": "forge'+forgever+'", "primary": true}]}, "manifestType": "minecraftModpack", "manifestVersion": 1, "files": [], "overrides": "overrides"}'
	manifestJson = json.loads(manifestData)

	with open(manifestFile, "w") as maniJson:
		json.dump(manifestJson, maniJson)

	zipfolder(pinf["displayName"].replace(" ", "_"), packDir)
