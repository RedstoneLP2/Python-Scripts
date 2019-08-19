#!/usr/bin/env python3
'''
Script to Download and convert Technic launcher modpacks to be more Multimc compatible*
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

def download(url, filename): #fancy download
	with open(filename, 'wb') as f:
		response = requests.get(url, stream=True)
		if response.status_code == 404:
			print("Error 404 while donwloading: "+ url)
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

def apiparse(apiurl):
	apiurl = apiurl + "?build=407"
	req = urllib.request.Request(apiurl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"}) # tell the api you're techniclauncher
	packinfo = urllib.request.urlopen(req).read()
	pinf = json.loads(packinfo)
	return pinf

def zipfolder(foldername, target_dir): #def for zipping folders
	zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
	rootlen = len(target_dir) + 1
	for base, dirs, files in os.walk(target_dir):
		for file in files:
			fn = os.path.join(base, file)
			zipobj.write(fn, fn[rootlen:])

def solderdl(pinf, zipDir):
		soapiurl = pinf["solder"]
		pname = pinf["name"]
			# connect to solder to find recommended version
		soinfourl = soapiurl+"modpack/"+pname
		req = urllib.request.Request(soinfourl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"})
		sopackinf = urllib.request.urlopen(req).read()
		sopackinfjson = json.loads(sopackinf)
		packver = sopackinfjson["recommended"]

			# connect to solder to get modlist w/ urls
		sopackurl = soapiurl+"modpack/"+pname+"/"+packver
		req = urllib.request.Request(sopackurl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"})
		soinf = urllib.request.urlopen(req).read()
		painf = json.loads(soinf)
		mcver = painf["minecraft"]
			# Download mods
		for l in painf["mods"]:
			mod = l["url"]
			filename = urlparse(mod)
			filename = os.path.basename(str(filename))
			filename = filename.replace("', params='', query='', fragment='')", "")
			file = os.path.join(zipDir, filename)
			print(filename)
			download(mod, file)

def detectloader(tempDir):
	modpackjar = os.path.join(tempDir, "bin", "Modpack.jar")
	if os.path.exists(modpackjar):
		pass
	elif os.path.exists(modpackjar.lower()):
		modpackjar = modpackjar.lower()
	else:
		modpackjar = None
	if modpackjar is not None:
		try: # try to extract version.json from modpack.jar
			zipfile.ZipFile(modpackjar, "r").extract("version.json", os.path.join(tempDir, "bin")) # assuming only forge has version.json in modpack.jar
			versionjson = json.load(open(os.path.join(tempDir,"bin","version.json")))
			forge = True
			fabric = False
			pass
		except KeyError as e:
			print("version.json not found, using modpack.jar as jarmod (may not work correctly)")
			forge = False
			fabric = False
			pass
	elif os.path.exists(os.path.join(tempDir, "bin", "version.json")):
		versionjson = json.load(open(os.path.join(tempDir, "bin", "version.json")))
		if ("fabric" in versionjson["libraries"][0]["name"]):
			forge = False
			fabric = True
		elif ("forge" in versionjson["libraries"][0]["name"]):
			forge = True
			fabric = False
	else:
		forge = False
		fabric = False
	return forge, fabric, modpackjar, versionjson

def getforgever(mcver, tempDir):
	forgeHeader = versionjson["libraries"][0]["name"]
	forgeHeader = forgeHeader.replace("net.minecraftforge:forge:", "")
	forgeHeader = forgeHeader.replace("net.minecraftforge:minecraftforge:", "")
	forgeHeader = forgeHeader.replace(mcver, "")
	forgever = forgeHeader.replace("-", "")
	return forgever

def createpatchfile(pDir, modpackjar):
	patches = os.path.join(pDir, "patches")
	jarmodDir = os.path.join(pDir, "jarmods")
	os.mkdir(jarmodDir)
	os.mkdir(patches)
	patchFile = os.path.join(patches, "org.multimc.jarmod.6d6f647061636b.json")
	shutil.move(modpackjar, jarmodDir)
	patchData = '''{"formatVersion": 1,"jarMods": [	{"MMC-displayname": "'''+os.path.basename(modpackjar)+'''","MMC-filename": "'''+os.path.basename(modpackjar)+'''","MMC-hint": "local","name": "org.multimc.jarmods:6d6f647061636b:1"}],"name": "6d6f647061636b.jar","uid": "org.multimc.jarmod.6d6f647061636b"}'''
	patchJson = json.loads(patchData)
	with open(patchFile, "w") as PatchF: # dump patchjson in patch.json
		json.dump(patchJson, PatchF)

with tempfile.TemporaryDirectory() as tempDir: #create tempDir
	packDir = os.path.join(tempDir, "modpack")
	zipDir = os.path.join(tempDir, "zipdir")
	binDir = os.path.join(zipDir, "bin")
	pDir = os.path.join(packDir, "modpack")
	mmcFile = os.path.join(pDir, "mmc-pack.json")
	minecraft = os.path.join(pDir, "minecraft")

	os.makedirs(pDir)
	os.mkdir(minecraft)
	os.mkdir(zipDir)

	userurl = input('Enter Pack API URL: ')
	pinf = apiparse(userurl)
	mcver = pinf["minecraft"]

	if pinf["solder"] is None:
		zipurl = pinf["url"]
		zname = os.path.join(zipDir, "modpack.zip")
		download(zipurl, zname)
	else:
		solderdl(pinf, zipDir)

	for file in files(zipDir): # extract all files and delete them
		filepath = os.path.join(zipDir, file)
		zipfile.ZipFile(filepath, "r").extractall(zipDir)
		os.remove(filepath)
	
	shutil.move(binDir, tempDir) # move bin somewhere else
	forge, fabric, modpackjar, versionjson = detectloader(tempDir)


	if forge:
		if any(ver in mcver for ver in ("1.13.", "1.14.")):
			print("1.13 and above modpacks using Forge may not work correctly") # a friendly reminder that forge 1.13 and up is not supported in multimc
		forgever = getforgever(mcver, tempDir)
	elif fabric:
		fabricHeader = versionjson["libraries"][0]["name"]
		fabricver = fabricHeader.replace("net.fabricmc:fabric-loader:", "")

	for dir in os.listdir(zipDir):
		shutil.move(os.path.join(zipDir, dir), minecraft)

	iconUrl=pinf["icon"]["url"]
	if iconUrl == "":
		iconUrl = "https://theme.zdassets.com/theme_assets/646263/b26a053b1a803ec41d3aa316adb534b82442757f.png"
	iconName=iconUrl[iconUrl.rfind("/")+1:].split("?", 1)[0]
	print(iconName)
	download(iconUrl, os.path.join(pDir, iconName))

	if modpackjar != None and not forge and not fabric:
		createpatchfile(pDir, modpackjar)
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"},{"cachedName": "modpack.jar","uid": "org.multimc.jarmod.6d6f647061636b"}],"formatVersion": 1}'''
	elif forge and not fabric:
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"},{"cachedName": "Forge","cachedRequires": [{"equals": "'''+mcver+'''","uid": "net.minecraft"}],"cachedVersion": "'''+forgever+'''","uid": "net.minecraftforge","version": "'''+forgever+'''"}],"formatVersion": 1}'''
	elif not forge and fabric:
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"},{"cachedName": "Intermediary Mappings","cachedRequires": [{"equals": "'''+mcver+'''","uid": "net.minecraft"}],"cachedVersion": "'''+mcver+'''","cachedVolatile": true,"dependencyOnly": true,"uid": "net.fabricmc.intermediary","version": "'''+mcver+'''"},{"cachedName": "Fabric Loader","cachedRequires": [{"uid": "net.fabricmc.intermediary"}],"cachedVersion": "'''+fabricver+'''","uid": "net.fabricmc.fabric-loader","version": "'''+fabricver+'''"}],"formatVersion": 1}'''
	else:
		mmcData = '''{"components": [{"cachedName": "Minecraft","cachedRequires": [],"cachedVersion": "'''+mcver+'''","important": true,"uid": "net.minecraft","version": "'''+mcver+'''"}],"formatVersion": 1}'''

	instancecfg = '''InstanceType=OneSix
	MCLaunchMethod=LauncherPart
	name='''+pinf["displayName"]+'''
	notes='''+pinf["description"]+'''
	iconKey='''+iconName.replace(".png", "")


	mmcJson = json.loads(mmcData)

	with open(mmcFile, "w") as mcJson: # dump mmcjson in mmc-pack.json
		json.dump(mmcJson, mcJson)

	with open(os.path.join(pDir,"instance.cfg"), "w+") as instanceFile: # write instancecfg in instance.cfg
		instanceFile.write(instancecfg)
		instanceFile.close()

	zipfolder(pinf["displayName"].replace(" ", "_").replace("/", "").replace("\\", ""), packDir) # zip everything up
	print("Output File: "+pinf["displayName"].replace(" ", "_").replace("/", "").replace("\\", "")+".zip")