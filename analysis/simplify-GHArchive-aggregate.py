import h5py
import numpy as np
import numba as nb


@nb.njit
def aggregate_after_sorting(repo_id, actor_id, event_type_id):
    count = np.zeros(len(repo_id), dtype=np.uint32)
    last_i = -1
    last_r = last_a = last_e = 0
    for i in range(len(count)):
        if last_i != -1 and repo_id[i] == last_r and actor_id[i] == last_a and event_type_id[i] == last_e:
            count[last_i] += 1
        else:
            last_i = i
            last_r = repo_id[i]
            last_a = actor_id[i]
            last_e = event_type_id[i]
            count[last_i] = 1
    return count


mask_repo_id       = np.uint64(0b1111111111111111111111111111111000000000000000000000000000000000)
mask_actor_id      = np.uint64(0b0000000000000000000000000000000111111111111111111111111111100000)
mask_event_type_id = np.uint64(0b0000000000000000000000000000000000000000000000000000000000011111)

for year in ["2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015"]:
    with h5py.File(f"GHArchive-{year}.h5", "r") as input_file:
        repo_id = np.asarray(input_file["repo_id"], dtype=np.uint64)
        actor_id = np.asarray(input_file["actor_id"], dtype=np.uint64)
        event_type_id = np.asarray(input_file["event_type_id"], dtype=np.uint64)

    print(f"read from GHArchive-{year}.h5")

    packed_into_64bit = np.zeros(len(repo_id), dtype=np.uint64)
    packed_into_64bit |= (repo_id << np.uint64(28 + 5))
    packed_into_64bit |= (actor_id << np.uint64(5))
    packed_into_64bit |= (event_type_id)

    # Make sure we haven't stomped on any bits.
    # (The maximum repo_id known to exist is 634695661, maximum actor_id is 132236732.)
    assert np.array_equal((packed_into_64bit & mask_repo_id) >> np.uint64(28 + 5), repo_id)
    assert np.array_equal((packed_into_64bit & mask_actor_id) >> np.uint64(5), actor_id)
    assert np.array_equal((packed_into_64bit & mask_event_type_id), event_type_id)

    print("packed_into_64bit")

    # After sorting, we can identify "same combination" sequentially without exploding memory use.
    order = np.argsort(packed_into_64bit)

    print("sorted")

    repo_id = repo_id[order]
    actor_id = actor_id[order]
    event_type_id = event_type_id[order]

    count = aggregate_after_sorting(repo_id, actor_id, event_type_id)
    uniques = (count != 0)
    num_uniques = np.count_nonzero(uniques)

    print("aggregated")

    with h5py.File(f"GHArchive-{year}-aggregated.h5", "w") as output_file:
        output_file.create_dataset("count", (num_uniques,), dtype=np.uint32, chunks=True, compression=1)
        output_file["count"][:] = count[uniques]

        output_file.create_dataset("repo_id", (num_uniques,), dtype=np.uint32, chunks=True, compression=1)
        output_file["repo_id"][:] = repo_id[uniques]

        output_file.create_dataset("actor_id", (num_uniques,), dtype=np.uint32, chunks=True, compression=1)
        output_file["actor_id"][:] = actor_id[uniques]

        output_file.create_dataset("event_type_id", (num_uniques,), dtype=np.uint32, chunks=True, compression=1)
        output_file["event_type_id"][:] = event_type_id[uniques]

    print(f"wrote to GHArchive-{year}-aggregated.h5")
