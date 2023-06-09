import json

import h5py
import numpy as np

for lookup in [
    "repo", "actor", "org"
]:
    lines = set()

    for filename in [
        "GHArchive-2023.h5",
        "GHArchive-2022.h5",
        "GHArchive-2021.h5",
        "GHArchive-2020.h5",
        "GHArchive-2019.h5",
        "GHArchive-2018.h5",
        "GHArchive-2017.h5",
        "GHArchive-2016.h5",
        "GHArchive-2015.h5",
    ]:
        with h5py.File(filename, "r") as file:
            for name, ids in json.loads(np.asarray(file[lookup + "_name2id_json"]).tobytes()).items():
                for x in ids:
                    lines.add(f"{x}\t{name}\n")
        print(filename, len(lines))

    with open(lookup + "_id_name.txt", "w") as file:
        for line in lines:
            file.write(line)

    print(lookup)

print("DONE")
