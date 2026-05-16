import os
import json
import subprocess

from pathlib import Path

HOME = os.environ["HOME"]
CONFIG_DIR = f'{HOME}/.config/Red-DiscordBot'
CONFIG_PATH = f'{CONFIG_DIR}/config.json'

DATA_PATH = f'{HOME}/.local/share/Red-DiscordBot/data/devon'
COG_PATH = f'{DATA_PATH}/cogs/CogManager/cogs'

devon_conf = {
    "DATA_PATH": DATA_PATH,
    "COG_PATH_APPEND": "cogs",
    "CORE_PATH_APPEND": "core",
    "STORAGE_TYPE": "JSON",
    "STORAGE_DETAILS": {}
}

def handle_conf_file():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.isfile(CONFIG_PATH):
        full_conf = { 'devon': devon_conf }
        with open(CONFIG_PATH, 'w') as f:
            f.write(json.dumps(full_conf, indent=2))

    with open(CONFIG_PATH, 'r') as f:
        conf = json.loads(f.read())

    if conf.get('devon', {}) != devon_conf:
        conf['devon'] = devon_conf
        with open(CONFIG_PATH, 'w') as f:
            f.write(json.dumps(conf, indent=2))

def handle_cog_links():
    os.makedirs(COG_PATH, exist_ok=True)

    for item in Path(COG_PATH).iterdir():
        if item.is_symlink() and item.is_dir():
            item.unlink()

    for file in os.listdir("."):
        if (os.path.isdir(file) and
            os.path.isfile(f'{file}/__init__.py') and
            os.path.isfile(f'{file}/info.json')):
            os.symlink(os.path.abspath(file), f'{COG_PATH}/{file}')

def main():
    handle_conf_file()
    handle_cog_links()

    try:
        subprocess.run(['redbot', 'devon'])
    except KeyboardInterrupt:
        print('CTRL+C pressed, stopping...')

if __name__ == "__main__":
    main()
