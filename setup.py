import subprocess, json, os

def is_line_in_file(file, pattern):
    with open(file, "r") as f:
        return any(pattern in x for x in f)

print("Configurations loaded")

commands:list = []

shell = os.environ["SHELL"]
user = os.environ["USER"]
rc = f"/home/{user}/"
rc += ".bashrc" if ("bash" in shell) else ".zshrc"

base_apt = " apt-get"
base_snap = " snap"
base_apt_repository = " add-apt-repository"
update = base_apt + " update"
upgrade = base_apt + " upgrade"
snap_install_template = base_snap + " install {}"
apt_install_template = base_apt + " install {} -y"
apt_repo_template = base_apt_repository + " {} -y"
append_template = "echo >> {}" + """{} | tee -a {}"""
alias_template = append_template.format(rc, "alias {}='{}'", rc)

sudo_command = "sudo"

with open("repos.json", "r") as repos_json:
    for r in json.load(repos_json):
        c = sudo_command + apt_repo_template.format(r["repo"])
        commands.append(c)
        print(f"\tQueued Repo: {r['name']} ({r['repo']})")
        print(f"\t\t{c}")

with open("packages.json", "r") as package_json:
    for p in json.load(package_json):
        c = ""
        if p["manager"] == "apt":
            c = sudo_command + apt_install_template.format(p["package"])
        else:
            c = sudo_command + snap_install_template.format(p["package"])
        commands.append(c)
        print(f"\tQueued Package: {p['name']} ({p['package']}, {p['manager']})")
        print(f"\t\t{c}")

with open("commands.json", "r") as commands_json:
    for config in json.load(commands_json):
        commands.append(config["command"])
        print(f"\tQueued Command: {c}")

for c in commands:
    print(f"Command: {c}")
    process = subprocess.Popen(c, stdout=subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    status = process.wait()
    print(f"o: {str(output, 'utf-8')}")

with open("file_additions.json", "r") as file_additions_json:
    for addition in json.load(file_additions_json):
        dest = addition["dest"]
        if addition["dest"] == "#rc":
            dest = rc
        if is_line_in_file(dest, addition["text"]):
            continue
        with open(dest, "a") as file:
            file.write("\n")
            file.write(addition["text"] + '\n')
        print(f"\tFile Addition: {addition['name']}")

with open("ssh.json", "r") as ssh_json:
    for ssh in json.load(ssh_json):
        dest = f"/home/{user}/.ssh/config"
        port = 22
        s = f"""
        Host {ssh["name"]}
        \tHostName {ssh["hostname"]}
        \tUser {ssh["user"]}
        \tPort {ssh["port"] if "port" in ssh else port}
        """
        if is_line_in_file(dest, f"Host {ssh['name']}"):
            continue
        with open(dest, "a") as file:
            file.write("\n")
            file.write(s + "\n")
        print(f"\tSSH Config Addition: {ssh['name']}")