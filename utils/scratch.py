import re
from pathlib import Path


def get_available_sample_maps():
    data_path = Path("static/sample_data")
    available_maps = []
    for child in data_path.iterdir():
        if child.suffix == ".json":
            available_maps.append(child.stem)
    return available_maps


if __name__ == "__main__":
    maps = get_available_sample_maps()
    pattern = re.compile("(.+)_l_(\d+)_ppl_(\d+)")
    titles = []
    levels = []
    ppls = []
    json_files = []

    for map in maps:
        print(str(map))
        results = pattern.split(str(map))
        titles.append(results[1].replace("_", " "))
        levels.append(results[2])
        ppls.append(results[3])
        file_name = map + ".json"
        json_files.append(file_name)

    print(titles)
    print(levels)
    print(ppls)
    print(json_files)
