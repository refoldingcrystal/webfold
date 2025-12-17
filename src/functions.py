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
                if parent_path == "":
                    if basename == "index":
                        structure.append(("page", item_path, parent_path))
                    else:
                        structure.append(("page", item_path, os.path.join(parent_path, basename)))
                else:
                    if basename != "index":
                        structure.append(("post", item_path, os.path.join(parent_path, basename)))
        else:
            structure.extend(dir_structure(item_path, os.path.join(parent_path, item)))
    return structure


def generate_item(origin_path, path, item_type):
    title = os.path.basename(path)
    if title == "": title = "home"
    print(f"generating {item_type} ->", title)
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, "index.html")

    with open(path, "w") as file:
        file.write(f"<h1>{title}</h1>\n\n")
        file.write(f"<a href=../>up</a>\n\n")


def generate_list(origin_path, path):
    title = os.path.basename(path)
    ls = os.listdir(origin_path)
    os.mkdir(path)
    print("generating list ->", title)
    print(ls)
    path = os.path.join(path, "index.html")

    with open(path, "w") as file:
        file.write(f"<h1>{title}</h1>\n\n")
        for name in ls:
            name, ext = os.path.splitext(name)
            if name == "index" or ext != ".md": continue
            file.write(f"<a href={name}>{name}</a>\n\n")
            
