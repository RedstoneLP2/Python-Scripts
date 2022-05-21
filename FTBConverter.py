#==================================================#
#       Script to convert FTB launcher             #
#     modpacks to a multimc compatible* format     #
#            by RedstoneLP2                        #
#==================================================#


import zipfile
import os
import requests
import tempfile
import json
import sys
import hashlib
import shutil

forge = False

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def files(path):
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			yield file

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download(url, filename): #fancy download
	with open(filename, 'wb') as f:
		response = requests.get(url, stream=True)
		if response.status_code == 404:
			print("Error 404 while downloading: "+ url)
			sys.exit(1)
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

with tempfile.TemporaryDirectory() as tempDir: #create tempDir

	packpath = input('Please Enter Path to FTB Instance folder: ')
	pinf = json.load(open(os.path.join(packpath,"instance.json"),"r"))

	packDir = os.path.join(tempDir, "modpack")
	pDir = os.path.join(packDir, "modpack")
	mmcFile = os.path.join(pDir, "mmc-pack.json")
	minecraft = os.path.join(pDir, "minecraft")

	os.makedirs(pDir)
	#os.mkdir(minecraft)

	mcver = pinf["mcVersion"]
	if "forge" in pinf["modLoader"].lower():
		forge = True
		loaderver = pinf["modLoader"].split("-")[2]
	elif "fabric" in pinf["modLoader"].lower():
		fabric = True
		loaderver = pinf["modLoader"].split("-")[3]
	
	print("Copying files")
	shutil.copytree(packpath,minecraft)

	print("Downloading artwork")
	artUrl=pinf["artUrl"]
	iconFileName=os.path.join(pDir,artUrl[artUrl.rfind("/")+1:].split("?", 1)[0])
	download(artUrl,iconFileName)
	iconName=md5(iconFileName)+"."+iconFileName.split(".")[-1]
	os.rename(iconFileName, os.path.join(pDir,iconName))
	print(iconName)


	print("Generating mmc-pack.json")
	mmcData = {"components": [{"cachedName": "Minecraft", "cachedRequires": [], "cachedVersion": mcver, "important": True, "uid": "net.minecraft", "version": mcver}], "formatVersion": 1}
	if forge:
	    mmcData["components"].append({"cachedName": "Forge","cachedRequires": [{"equals": mcver, "uid": "net.minecraft"}]})
	elif fabric:
	    mmcData["components"].append({"cachedName": "Intermediary Mappings", "cachedRequires": [{"equals": mcver, "uid": "net.minecraft"}], "cachedVersion": mcver, "cachedVolatile": True, "DependencyOnly": True, "uid": "net.fabricmc.intermediary", "version": mcver})
	    mmcData["components"].append({"cachedName": "Fabric Loader", "cachedRequires": [{"uid": "net.fabricmc.intermediary"}], "cachedVersion": loaderver, "uid": "net.fabricmc.fabric-loader", "version": loaderver})


	instancecfg = '''InstanceType=OneSix
	MCLaunchMethod=LauncherPart
	name='''+pinf["name"]+" "+pinf["version"]+'''
	notes='''+pinf["description"]+'''
	iconKey='''+iconName.replace(".png", "")


	mmcJson = mmcData #json.loads(mmcData)

	with open(mmcFile, "w") as mcJson: # dump mmcjson in mmc-pack.json
		json.dump(mmcJson, mcJson)

	with open(os.path.join(pDir,"instance.cfg"), "w+") as instanceFile: # write instancecfg in instance.cfg
		instanceFile.write(instancecfg)
		instanceFile.close()
	outputFileName=pinf["name"].replace(" ", "_").replace("/", "").replace("\\", "")+"-"+pinf["version"]
	print("Zipping up")
	zipfolder(outputFileName, packDir) # zip everything up
	print("Output File: "+outputFileName+".zip")
