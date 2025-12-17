import os


def dir_structure(dir_path, parent_path=""):
    ls = os.listdir(dir_path)
    structure = [("list", dir_path, parent_path)]
    for item in ls:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            basename, ext = os.path.splitext(item_path)
            basename = os.path.basename(basename)
            if ext == ".md":
                structure.append(("page", item_path, os.path.join(parent_path, basename)))
        else:
            structure.extend(dir_structure(item_path, os.path.join(parent_path, item)))
    return structure