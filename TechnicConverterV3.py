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

def zipfolder(foldername, target_dir): #def for zipping folders
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])

with tempfile.TemporaryDirectory() as tempDir: #create tempdir
	packDir = os.path.join(tempDir, "modpack")
	zipDir = os.path.join(tempDir, "zipdir")
	modpackjar = os.path.join(tempDir, "bin", "modpack.jar")
	binDir = os.path.join(zipDir, "bin")
	pDir = os.path.join(packDir, "modpack")
	os.makedirs(pDir)
	os.mkdir(zipDir)

	userurl = input('Enter Pack API URL: ')
	apiurl = userurl + "?build=407"
	req = urllib.request.Request(apiurl, headers={'User-Agent' : "Mozilla/5.0 (Java) TechnicLauncher/4.407"}) #tell the api you're techniclauncher
	packinfo = urllib.request.urlopen(req).read()
	pinf = json.loads(packinfo)
	mcver = pinf["minecraft"]

	if pinf["solder"] is None:
		zipurl = pinf["url"]
		solder = False
	else:
		solder = True
		soapiurl = pinf["solder"]

	if solder: # if pack is solder
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
	
	else: # else download modpack.zip
		zname = os.path.join(zipDir, "modpack.zip")
		download(zipurl, zname)
		# extract all files and delete them
	for file in files(zipDir):
		filepath = os.path.join(zipDir, file)
		zipfile.ZipFile(filepath, "r").extractall(zipDir)
		os.remove(filepath)
	
	shutil.move(binDir, tempDir) # move bin somewhere else


	mmcFile = os.path.join(pDir, "mmc-pack.json")
	jarmodDir = os.path.join(pDir, "jarmods")
	patches = os.path.join(pDir, "patches")
	patchFile = os.path.join(patches, "org.multimc.jarmod.6d6f647061636b.json")
	minecraft = os.path.join(pDir, "minecraft")

	os.mkdir(minecraft)
	os.mkdir(patches)
	os.mkdir(jarmodDir)

	shutil.move(modpackjar, jarmodDir)

	for dir in os.listdir(zipDir):
		shutil.move(os.path.join(zipDir, dir), minecraft)
		
	mmcData = '''{
    "components": [
        {
            "cachedName": "Minecraft",
            "cachedRequires": [
                {
                    "suggests": "2.9.4-nightly-20150209",
                    "uid": "org.lwjgl"
                }
            ],
            "cachedVersion": "'''+mcver+'''",
            "important": true,
            "uid": "net.minecraft",
            "version": "'''+mcver+'''"
        },
        {
            "cachedName": "modpack.jar",
            "uid": "org.multimc.jarmod.6d6f647061636b"
        }
    ],
    "formatVersion": 1
}'''

	instancecfg = '''InstanceType=OneSix
	MCLaunchMethod=LauncherPart
	name='''+pinf["displayName"]+'''
	notes='''+pinf["description"]

	patchData = '''{
    "formatVersion": 1,
    "jarMods": [
        {
            "MMC-displayname": "modpack.jar",
            "MMC-filename": "modpack.jar",
            "MMC-hint": "local",
            "name": "org.multimc.jarmods:6d6f647061636b:1"
        }
    ],
    "name": "6d6f647061636b.jar",
    "uid": "org.multimc.jarmod.6d6f647061636b"
}'''

	patchJson = json.loads(patchData)

	mmcJson = json.loads(mmcData)

	with open(mmcFile, "w") as mcJson: # dump mmcjson in mmc-pack.json
		json.dump(mmcJson, mcJson)

	with open(patchFile, "w") as PatchF: # dump patchjson in patch.json
		json.dump(patchJson, PatchF)

	with open(os.path.join(pDir,"instance.cfg"), "w+") as instanceFile: # write instancecfg in instance.cfg
		instanceFile.write(instancecfg)
		instanceFile.close()

	zipfolder(pinf["displayName"].replace(" ", "_"), packDir) # zip everything up