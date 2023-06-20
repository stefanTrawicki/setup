import subprocess, json, os, sys

class Runnable():
    def run(self, dry_run=False):
        if dry_run:
            print(self.command)
        else:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, shell=True)
            (output, err) = process.communicate()
            status = process.wait()
            print(f"o: {str(output, 'utf-8')}")

class BrewPackage(Runnable):
    def __init__(self, package:str, cask:bool=False):
        self.manager:str = "brew"
        self.command:str = f"brew install {package} {'--cask' if cask else ''}"

class AptPackage(Runnable):
    def __init__(self, package:str):
        self.manager:str = "apt"
        self.command:str = f"sudo apt-get install {package}"

class SnapPackage(Runnable):
    def __init__(self, package:str, flag:str):
        self.manager:str = "snap"
        self.command:str = f"sudo snap install {package} {flag}"
    
class AptRepo(Runnable):
    def __init__(self, repo:str):
        self.manager:str = "apt"
        self.command:str = f"sudo add-apt-repository {repo} -y"

class MacShellCommand(Runnable):
    def __init__(self, command:str):
        self.manager:str = "macshell"
        self.command:str = command

    def run(self, dry_run=False):
        if "#home" in self.command:
            self.command = self.command.replace("#home", home)
        Runnable.run(self, dry_run)

class LinuxShellCommand(MacShellCommand):
    def __init__(self, command:str):
        self.manager:str = "shell"
        self.command:str = command

ref = {
    "shell": LinuxShellCommand,
    "macshell": MacShellCommand,
    "brew": BrewPackage,
    "apt": AptPackage,
    "snap": SnapPackage,
    "apt-repo": AptRepo
}

home = os.path.expanduser('~')
operating_system = sys.platform
valid_managers = ["brew", "macshell"] if "darwin" in operating_system else ["apt", "apt-repo", "snap"]
runnables:list = []

with open("packages.json") as packages:
    for package in json.load(packages):
        for candidate in package["candidates"]:
            if candidate["manager"] in valid_managers:
                runnables.append((package["name"], ref[candidate["manager"]](**candidate["contents"])))

for name, runnable in runnables:
    runnable.run(dry_run=False)