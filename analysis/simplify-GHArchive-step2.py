import json
import glob

import h5py
import numpy as np

out = h5py.File("GHArchive.h5", "w")

######################################

actor_id2name = {}
for filename in glob.glob("*/actor_id_names.json"):
    for id, names in json.load(open(filename)).items():
        if id not in actor_id2name:
            actor_id2name[id] = set()
        for name in names:
            actor_id2name[id].add(name)
    print(filename, flush=True)

actor_name2id = {}
for id, names in actor_id2name.items():
    for name in names:
        if name not in actor_name2id:
            actor_name2id[name] = set()
        actor_name2id[name].add(int(id))

for k, v in actor_id2name.items():
    actor_id2name[k] = sorted(v)
actor_id2name = json.dumps(actor_id2name, separators=(",", ":")).encode("utf-8")
out.create_dataset("actor_id2name_json", (len(actor_id2name),), dtype="u1", compression=1)
out["actor_id2name_json"][:] = np.frombuffer(actor_id2name, dtype="u1")
del actor_id2name

for k, v in actor_name2id.items():
    actor_name2id[k] = sorted(v)
actor_name2id = json.dumps(actor_name2id, separators=(",", ":")).encode("utf-8")
out.create_dataset("actor_name2id_json", (len(actor_name2id),), dtype="u1", compression=1)
out["actor_name2id_json"][:] = np.frombuffer(actor_name2id, dtype="u1")
del actor_name2id

print("wrote actor_id2name_json and actor_name2id_json", flush=True)

######################################

repo_id2name = {}
for filename in glob.glob("*/repo_id_names.json"):
    for id, names in json.load(open(filename)).items():
        if id not in repo_id2name:
            repo_id2name[id] = set()
        for name in names:
            repo_id2name[id].add(name)
    print(filename, flush=True)

repo_name2id = {}
for id, names in repo_id2name.items():
    for name in names:
        if name not in repo_name2id:
            repo_name2id[name] = set()
        repo_name2id[name].add(int(id))

for k, v in repo_id2name.items():
    repo_id2name[k] = sorted(v)
repo_id2name = json.dumps(repo_id2name, separators=(",", ":")).encode("utf-8")
out.create_dataset("repo_id2name_json", (len(repo_id2name),), dtype="u1", compression=1)
out["repo_id2name_json"][:] = np.frombuffer(repo_id2name, dtype="u1")
del repo_id2name

for k, v in repo_name2id.items():
    repo_name2id[k] = sorted(v)
repo_name2id = json.dumps(repo_name2id, separators=(",", ":")).encode("utf-8")
out.create_dataset("repo_name2id_json", (len(repo_name2id),), dtype="u1", compression=1)
out["repo_name2id_json"][:] = np.frombuffer(repo_name2id, dtype="u1")
del repo_name2id

print("wrote repo_id2name_json and repo_name2id_json", flush=True)

######################################

org_id2name = {}
for filename in glob.glob("*/org_id_names.json"):
    for id, names in json.load(open(filename)).items():
        if id not in org_id2name:
            org_id2name[id] = set()
        for name in names:
            org_id2name[id].add(name)
    print(filename, flush=True)

org_name2id = {}
for id, names in org_id2name.items():
    for name in names:
        if name not in org_name2id:
            org_name2id[name] = set()
        org_name2id[name].add(int(id))

for k, v in org_id2name.items():
    org_id2name[k] = sorted(v)
org_id2name = json.dumps(org_id2name, separators=(",", ":")).encode("utf-8")
out.create_dataset("org_id2name_json", (len(org_id2name),), dtype="u1", compression=1)
out["org_id2name_json"][:] = np.frombuffer(org_id2name, dtype="u1")
del org_id2name

for k, v in org_name2id.items():
    org_name2id[k] = sorted(v)
org_name2id = json.dumps(org_name2id, separators=(",", ":")).encode("utf-8")
out.create_dataset("org_name2id_json", (len(org_name2id),), dtype="u1", compression=1)
out["org_name2id_json"][:] = np.frombuffer(org_name2id, dtype="u1")
del org_name2id

print("wrote org_id2name_json and org_name2id_json", flush=True)

######################################

file_timestamp     = [np.memmap(x, dtype="u4") for x in sorted(glob.glob("*/column_timestamp.u4"))]
file_event_type_id = [np.memmap(x, dtype="u1") for x in sorted(glob.glob("*/column_event_type_id.u1"))]
file_event_id      = [np.memmap(x, dtype="u8") for x in sorted(glob.glob("*/column_event_id.u8"))]
file_actor_id      = [np.memmap(x, dtype="u4") for x in sorted(glob.glob("*/column_actor_id.u4"))]
file_repo_id       = [np.memmap(x, dtype="u4") for x in sorted(glob.glob("*/column_repo_id.u4"))]
file_org_id        = [np.memmap(x, dtype="u4") for x in sorted(glob.glob("*/column_org_id.u4"))]

for column in ("timestamp", "event_type_id", "event_id", "actor_id", "repo_id", "org_id"):
    file = eval("file_" + column)
    out.create_dataset(
        column,
        (sum(len(x) for x in file),),
        dtype=file[0].dtype,
        chunks=True,
        compression=1,
    )
    start = stop = 0
    for i, x in enumerate(file):
        stop += len(x)
        out[column][start:stop] = x
        start = stop
        print(i, flush=True)

    print(f"wrote {column}", flush=True)

out.close()

print("DONE", flush=True)
