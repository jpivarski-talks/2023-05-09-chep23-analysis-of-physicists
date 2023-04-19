import json
import glob

repos = {}


def add_repo(repo_name, repo_data):
    if repo_name is not None and repo_name not in repos:
        repos[repo_name] = repo_data

for filename in sorted(glob.glob("file-ages/file-last-touch*")):
    print(filename)

    with open(filename, "r", encoding="utf-8", errors="surrogateescape") as file:
        repo_name = None
        repo_data = None

        try:
            for line in file:
                if line[:6] == "REPO: ":
                    add_repo(repo_name, repo_data)

                    slash_index = line.index("/")
                    try:
                        int(line[6:slash_index])
                        repo_name = line[slash_index + 1 : -1]
                    except ValueError:
                        repo_name = line[6:-1]

                    repo_data = {}

                else:
                    author_time = line[0:25]
                    committer_time = line[26:51]
                    commit_hash = line[52:92]
                    fname = line[93:-1]
                    repo_data[fname] = [author_time, committer_time, commit_hash]

        except UnicodeDecodeError as err:
            print(f"previous: {line}")
            raise

        add_repo(repo_name, repo_data)

with open("file-ages.json", "w", encoding="utf-8", errors="surrogateescape") as file:
    json.dump(repos, file)
