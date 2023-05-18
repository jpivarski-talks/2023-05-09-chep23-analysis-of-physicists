import json
import gzip
import glob
from datetime import datetime

import numpy as np

# seen = set()
# for filename in sorted(glob.glob("/tmp/testy/*.json.gz"))[::-1]:
#     with gzip.open(filename, "r") as file:
#         for line in file:
#             event = json.loads(line)
#             if event["type"] not in seen:
#                 seen.add(event["type"])
#                 print("========================================================")
#                 print(event["type"])
#                 print()
#                 print(json.dumps(event, indent=2))
#                 print()

# https://docs.github.com/en/webhooks-and-events/events/github-event-types
event_type_to_id = {
    "CommitCommentEvent":             1,
    "CreateEvent":                    2,
    "DeleteEvent":                    3,
    "DownloadEvent":                  4,
    "FollowEvent":                    5,
    "ForkApplyEvent":                 6,
    "ForkEvent":                      7,
    "GistEvent":                      8,
    "GollumEvent":                    9,
    "IssueCommentEvent":             10,
    "IssuesEvent":                   11,
    "MemberEvent":                   12,
    "PublicEvent":                   13,
    "PullRequestEvent":              14,
    "PullRequestReviewCommentEvent": 15,
    "PullRequestReviewEvent":        16,
    "PushEvent":                     17,
    "ReleaseEvent":                  18,
    "TeamAddEvent":                  19,
    "WatchEvent":                    20,
}

file_timestamp     = open("column_timestamp.u4", "wb");     dtype_timestamp     = np.dtype("u4")
file_event_type_id = open("column_event_type_id.u1", "wb"); dtype_event_type_id = np.dtype("u1")
file_event_id      = open("column_event_id.u8", "wb");      dtype_event_id      = np.dtype("u8")
file_actor_id      = open("column_actor_id.u4", "wb");      dtype_actor_id      = np.dtype("u4")
file_repo_id       = open("column_repo_id.u4", "wb");       dtype_repo_id       = np.dtype("u4")
file_org_id        = open("column_org_id.u4", "wb");        dtype_org_id        = np.dtype("u4")

actor_id_names = {}
repo_id_names = {}
org_id_names = {}

for filename in sorted(glob.glob("*.json.gz")):
    with gzip.open(filename, "r") as file:
        for line in file:
            try:
                event = json.loads(line)
	    except json.decoder.JSONDecodeError:
                continue

            try:
                timestamp = int(datetime.fromisoformat(event["created_at"].rstrip("Z")).timestamp())
            except ValueError:
                timestamp = int(datetime.strptime(event["created_at"], "%Y/%m/%d %H:%M:%S %z").timestamp())

            event_type_id = event_type_to_id.get(event["type"], 0)

            # if "id" not in event:
            #     actor_name = event["actor"]
            #     if actor_name is None:
            #         actor_name = ""
            #     if "actor_attributes" not in event:
            #         actor_display = ""
            #     else:
            #         actor_display = event["actor_attributes"].get("name", "")
            #     if event_type_id == 8:  # GistEvent
            #         repo_id = event["payload"]["id"]
            #         repo_name = event["payload"]["name"]
            #     elif "repository" in event:
            #         if "id" not in event["repository"]:
            #             repo_id = 0
            #             repo_name = event["repository"]["owner"] + "/" + event["repository"]["name"]
            #         else:
            #             repo_id = event["repository"]["id"]
            #             repo_name = actor_name + "/" + event["repository"]["name"]
            #     else:
            #         repo_id = 0
            #         repo_name = ""
            # else:

            assert "id" in event   # from 2015-01-01 onward

            event_id = int(event["id"])
            actor_id = event["actor"].get("id", 0)
            repo_id = event["repo"].get("id", 0)

            actor_name = event["actor"].get("login", "")
            # actor_display = event["actor"].get("display_login", "")
            repo_name = event["repo"]["name"]

            org_id = 0
            org_name = ""
            if "org" in event:
                org_id = event["org"]["id"]
                org_name = event["org"]["login"]

            file_timestamp.write(np.array(timestamp, dtype=dtype_timestamp).tobytes())
            file_event_type_id.write(np.array(event_type_id, dtype=dtype_event_type_id).tobytes())
            file_event_id.write(np.array(event_id, dtype=dtype_event_id).tobytes())
            file_actor_id.write(np.array(actor_id, dtype=dtype_actor_id).tobytes())
            file_repo_id.write(np.array(repo_id, dtype=dtype_repo_id).tobytes())
            file_org_id.write(np.array(org_id, dtype=dtype_org_id).tobytes())

            if actor_id not in actor_id_names:
                actor_id_names[actor_id] = set([actor_name])
            else:
                actor_id_names[actor_id].add(actor_name)

            if repo_id not in repo_id_names:
                repo_id_names[repo_id] = set([repo_name])
            else:
                repo_id_names[repo_id].add(repo_name)

            if org_id not in org_id_names:
                org_id_names[org_id] = set([org_name])
            else:
                org_id_names[org_id].add(org_name)

    file_timestamp.flush()
    file_event_type_id.flush()
    file_event_id.flush()
    file_actor_id.flush()
    file_repo_id.flush()
    file_org_id.flush()
    print(filename, flush=True)

file_timestamp.close()
file_event_type_id.close()
file_event_id.close()
file_actor_id.close()
file_repo_id.close()
file_org_id.close()

json.dump({k: sorted(v) for k, v in actor_id_names.items()}, open("actor_id_names.json", "w"), separators=(",", ":"))
json.dump({k: sorted(v) for k, v in repo_id_names.items()}, open("repo_id_names.json", "w"), separators=(",", ":"))
json.dump({k: sorted(v) for k, v in org_id_names.items()}, open("org_id_names.json", "w"), separators=(",", ":"))

print("DONE")
