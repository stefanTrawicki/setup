import subprocess, json, os, sys

# {
#         "name": "HomeBrew package manager",
#         "candidates": [
#             {
#                 "manager": "macshell",
#                 "contents": {
#                     "command": "curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash"
#                 }
#             }
#         ]
#     },

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColorPrint(object):
    def __init__(self, col=bcolors.OKGREEN):
        self.col = col

    def __enter__(self):
        print(self.col)

    def __exit__(self, *args):
        print(bcolors.ENDC)

strip = lambda x : str('=' * x)
default_strip_len = 16

class Runnable():
    def run(self, dry_run=False):
        if dry_run:
            print(self.command)
        else:
            process = subprocess.run(self.command, capture_output=True, shell=True)
            # (output, err) = process.communicate()
            # status = process.wait()
            # print(f"o: {str(output, 'utf-8')}")
            clean = lambda x : str(x, 'utf-8').replace("\n", "\n\t")
            o = clean(process.stdout)
            e = clean(process.stderr)
            with ColorPrint(bcolors.HEADER):
                print(f"Command: {strip(default_strip_len)}\n\t{self.command}")
            if len(o) > 0:
                with ColorPrint(bcolors.OKGREEN):
                    print(f"Output: {strip(default_strip_len)}\n\t{o}")
            if len(e) > 0:
                with ColorPrint(bcolors.WARNING):
                    print(f"Warnings: {strip(default_strip_len)}\n\t{e}")

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