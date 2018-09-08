import subprocess
import re
from distutils.version import LooseVersion

def function_FindKeywordListOfList(list, keyword):
    regex = re.compile(".*("+keyword+").*")

    for row in list:
        return filter(regex.match, row)
    return None

def function_FindKeywordList(list, keyword):
    regex = re.compile(r".*("+keyword+").*")

    return filter(regex.match, list)

def function_FindKeywordListNotEmpty(list, keyword):
    regex = re.compile(r".*("+keyword+").*")

    return True if len(filter(regex.match, list))>0 else False


def function_CheckInitial():
    vgatype = (subprocess.check_output(["lspci", "-nnk"])).split("\n")
    vgalist = []
    regex = re.compile(r"\[(.*?)\]")

    for line in vgatype:
        if "VGA" in line:
            vgalist.append(regex.findall(line))
    return vgalist

def function_FindInstalledDrivers():
    devlist = function_CheckInitial()
    regexp = re.compile(r"Mesa(.*)\.")    
    gpus = []
    gpubrands = []
    driverversion = ""
    nvidia = False
    
    #intel
    if len(function_FindKeywordListOfList(devlist, "8008"))>0:
        gpus.append("Intel")
    #amd
    if len(function_FindKeywordListOfList(devlist, "1002"))>0:
        driver = (subprocess.check_output(["bash","-c","lspci -nnk -d"+function_FindKeywordListOfList(devlist, "1002")[0]])).split("\n")
        gpubrands = driver[0]
        driverInUse = function_FindKeywordList(driver, "Kernel driver in use")
        if function_FindKeywordListNotEmpty(driverInUse, "amd"):
            gpus.append("AMD")
        elif function_FindKeywordListNotEmpty(driverInUse, "radeon"):
            gpus.append("AMD-no vulkan")
        elif function_FindKeywordListNotEmpty(driverInUse, "pci-stub"):
            gpus.append("pci-stub")
        elif function_FindKeywordListNotEmpty(driverInUse, "vfio"):
            gpus.append("vfio")
    #nvidia
    if len(function_FindKeywordListOfList(devlist, "10de"))>0:
        driver = (subprocess.check_output(["bash","-c","lspci -nnk -d"+function_FindKeywordListOfList(devlist, "10de")[0]])).split("\n")
        gpubrands = driver[0]
        driverInUse = function_FindKeywordList(driver, "Kernel driver in use")
        if function_FindKeywordListNotEmpty(driverInUse, "nvidia"):
            gpus.append("Nvidia")
        elif function_FindKeywordListNotEmpty(driverInUse, "noveau"):
            print("[WARN] It is not recommended using Nvidia open source driver!")
            gpus.append("Nvidia-noveau")
        elif function_FindKeywordListNotEmpty(driverInUse, "pci-stub"):
            gpus.append("pci-stub")
        elif function_FindKeywordListNotEmpty(driverInUse, "vfio"):
            gpus.append("vfio")

    if len(gpus)>1:
        if function_FindKeywordListNotEmpty(gpus, "AMD") and  function_FindKeywordListNotEmpty(gpus, "Intel"):
            driverversion = [s for s in (subprocess.check_output(["bash","-c","DRI_PRIME=1 glxinfo"])).split("\n") if "OpenGL version string" in s][0]
        elif function_FindKeywordListNotEmpty(gpus, "AMD") and function_FindKeywordListNotEmpty(gpus, "Nvidia"):
            print("[WARN] I don't know how to handle AMD and Nvidia GPU, assuming to use DRI_PRIME=1")
            driverversion = [s for s in (subprocess.check_output(["bash","-c","DRI_PRIME=1 glxinfo"])).split("\n") if "OpenGL version string" in s][0]
    else:
        driverversion = [s for s in (subprocess.check_output(["bash","-c","DRI_PRIME=1 glxinfo"])).split("\n") if "OpenGL version string" in s][0]
    
    regexp = re.compile(r"Mesa(.*)")  

    if len(gpus)>1 :
        print("[WARN] Multiple GPU detected: " + str(gpus) + ". This may can cause gameplay freeze.") 
    if len(gpus)>=1 and function_FindKeywordListNotEmpty(gpus, "Nvidia"):
        regexp = re.compile(r"NVIDIA(.*)")  
        nvidia = True
    #print(driverversion)
    return [regexp.search(driverversion).group(1).split("-")[0], gpubrands, nvidia]  #process string into manageable one.

def function_CheckKernel():
    regexp = re.compile(r"version(.*)\.[0-9]")    
    version = subprocess.check_output(["bash","-c","cat /proc/version"])

    return regexp.search(version).group(1).strip().split("-")[0]

def function_CheckVulkanLib():
    vulkanver = (subprocess.check_output(["lspci", "-nnk"])).split("\n")

def function_CheckLLVM():
    return None

x = function_FindInstalledDrivers()
print("Your GPU: \n" + x[1])
if not x[2]:
    print("Mesa" + " Driver version: " + str(x[0])) 
else:
    print("Nvidia propertiary driver" + "Driver version: " + str(x[0]))

print("Kernel Version: " + str(function_CheckKernel()))
print("LLVM version:"+function_CheckLLVM())
