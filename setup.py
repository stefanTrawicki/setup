import subprocess, json, os

print("Configurations loaded")

commands:list = []

shell = os.environ["SHELL"]
rc = "~/"
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

with open("configurations.json", "r") as configurations_json:
    for config in json.load(configurations_json):
        c = ""
        if config["type"] == "command":
            c = config["command"]
        if config["type"] == "alias":
            c = alias_template.format(config["alias"], config["alias_command"])
        if config["type"] == "append":
            dest = rc if config["destination"] == "rc" else config["destination"]
            c = append_template.format(dest, config["line"], dest)
        commands.append(c)
        print(f"\tQueued Command: {c}")

with open("ssh.json", "r") as ssh_json:
    for ssh in json.load(ssh_json):
        dest = "/home/s/.ssh/config"
        config = f"Host {ssh['name']}\n\tHostName {ssh['hostname']}\n\tUser {ssh['user']}"
        if "port" in ssh:
            config += f"\tPort {json['port']}"
        c = append_template.format(dest, config, dest)
        commands.append(c)
        print(f"\tQueued Command: {c}")

for c in commands:
    print(f"Command: {c}")
    process = subprocess.Popen(c, stdout=subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    status = process.wait()
    print(f"o: {str(output, 'utf-8')}")