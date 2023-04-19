import tarfile
import glob
import json

file_ages = json.load(open("file-ages.json"))

for repo_tgz in glob.glob("GitHub-CMSSW-user-nonfork-raw-data-1Mcut/*/*.tgz"):
    repo_name = repo_tgz[41:-4]

    repo_file_ages = file_ages[repo_name]

    bad = 0
    total = 0

    with tarfile.open(repo_tgz) as tfile:
        for tinfo in tfile.getmembers():
            if not tinfo.isdir():
                info = repo_file_ages.get(tinfo.name[len(repo_name) + 1:])
                if info is None:
                    bad += 1
                total += 1

    if bad > 0:
        print(f"{round(bad / total * 100):3d}% ({bad}) {repo_name}")
