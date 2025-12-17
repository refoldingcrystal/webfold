import shutil
from functions import dir_structure
import os
import yaml
import sys

input_dir = "example"
config_filename = "config.yaml"

input_path = os.path.abspath(input_dir)
if os.path.isdir(input_path):
    config_path = os.path.join(input_path, config_filename)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(e)
                sys.exit(1)
        for required_dir in ["content_dir", "output_dir"]:
            if required_dir not in config:
                print(f"'{required_dir}' not found in config")
                sys.exit(1)
    else:
        print(f"'{config_filename}' is not a file")
else:
    print(f"'{input_dir}' is not a directory")

content_path = os.path.abspath(os.path.join(input_dir, config["content_dir"]))
if not os.path.isdir(content_path):
    print(f"'{config["content_path"]}' is not a directory")
    sys.exit(1)
print(content_path)

structure = dir_structure(content_path)

output_path = os.path.abspath(os.path.join(input_dir, config["output_dir"]))
if os.path.isdir(output_path):
    shutil.rmtree(output_path)
os.makedirs(output_path)