'''
Script to Download and convert FTB launcher modpacks to be more Multimc compatible*
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
import pathlib

apiurl = "https://api.modpacks.ch/public/modpack/"
fabric = False
forge = False

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

from urllib.parse import urlparse

def files(path):
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			yield file

def download(url, filename): #fancy download
	with open(filename, 'wb') as f:
		response = requests.get(url, stream=True)
		if response.status_code == 404:
			print("Error 404 while downloading: "+ url)
			sys.exit()
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



def apisearch(searchterm):

	req = urllib.request.Request(apiurl+"search?term="+searchterm) # Generate Request

	if urllib.request.urlopen(req).getcode()==404:
		print("Error 404 while accessing API. Please check URL")
		sys.exit()

	apiresults = urllib.request.urlopen(req).read()
	results = json.loads(apiresults)
	return results



def apiparse(packid, verid):
	req = urllib.request.Request(apiurl+packid+"/"+verid) # Generate Request
	reqm = urllib.request.Request(apiurl+packid) # Generate Request
	if urllib.request.urlopen(req).getcode()==404 or urllib.request.urlopen(reqm).getcode()==404:
		print("Error 404 while accessing API. Please check URL")
		sys.exit()

	packinfo = urllib.request.urlopen(req).read()
	packmeta = urllib.request.urlopen(reqm).read()
	pinf = json.loads(packinfo)
	pmeta = json.loads(packmeta)
	return pinf, pmeta

def zipfolder(foldername, target_dir): #def for zipping folders
	zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
	rootlen = len(target_dir) + 1
	for base, dirs, files in os.walk(target_dir):
		for file in files:
			fn = os.path.join(base, file)
			zipobj.write(fn, fn[rootlen:])

#with tempfile.TemporaryDirectory() as tempDir: #create tempDir
if True:
	tempDir = os.path.join(os.curdir,"test")

	packDir = os.path.join(tempDir, "modpack")
	pDir = os.path.join(packDir, "modpack")
	mmcFile = os.path.join(pDir, "mmc-pack.json")
	minecraft = os.path.join(pDir, "minecraft")

	os.makedirs(pDir)
	os.mkdir(minecraft)

	#userurl = input('Enter Pack API URL: ')
	pinf, pmeta = apiparse("31","32")
	#print(pinf)
	for n in pinf["targets"]:
		if n["name"] == "minecraft":
			mcver = n["version"]
			break
		if n["name"] == "forge":
			forge = True
			forgever = n["version"]


	for n in pinf["files"]:
		zipurl = n["url"]
		zname = pathlib.PurePath(minecraft).joinpath(n["path"]).joinpath(n["name"])
		pathlib.Path(minecraft).joinpath(n["path"]).mkdir(parents=True,exist_ok=True)
		print(zname)
		print(zipurl)
		download(zipurl, zname)

	iconUrl=pmeta["art"][0]["url"]

	iconName=iconUrl[iconUrl.rfind("/")+1:].split("?", 1)[0]
	print(iconName)
	download(iconUrl, os.path.join(pDir, iconName))

	if forge and not fabric:
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"},{"cachedName": "Forge","cachedRequires": [{"equals": "'''+mcver+'''","uid": "net.minecraft"}],"cachedVersion": "'''+forgever+'''","uid": "net.minecraftforge","version": "'''+forgever+'''"}],"formatVersion": 1}'''
	#elif not forge and fabric:
	#	mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"},{"cachedName": "Intermediary Mappings","cachedRequires": [{"equals": "'''+mcver+'''","uid": "net.minecraft"}],"cachedVersion": "'''+mcver+'''","cachedVolatile": true,"dependencyOnly": true,"uid": "net.fabricmc.intermediary","version": "'''+mcver+'''"},{"cachedName": "Fabric Loader","cachedRequires": [{"uid": "net.fabricmc.intermediary"}],"cachedVersion": "'''+fabricver+'''","uid": "net.fabricmc.fabric-loader","version": "'''+fabricver+'''"}],"formatVersion": 1}'''
	else:
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"}],"formatVersion": 1}'''

	instancecfg = '''InstanceType=OneSix
	MCLaunchMethod=LauncherPart
	name='''+pmeta["name"]+'''
	notes='''+pmeta["description"]+'''
	iconKey=""'''+iconName.replace(".png", "")


	mmcJson = json.loads(mmcData)

	with open(mmcFile, "w") as mcJson: # dump mmcjson in mmc-pack.json
		json.dump(mmcJson, mcJson)

	with open(os.path.join(pDir,"instance.cfg"), "w+") as instanceFile: # write instancecfg in instance.cfg
		instanceFile.write(instancecfg)
		instanceFile.close()

	zipfolder(pmeta["name"].replace(" ", "_").replace("/", "").replace("\\", ""), packDir) # zip everything up
	print("Output File: "+pmeta["name"].replace(" ", "_").replace("/", "").replace("\\", "")+".zip")