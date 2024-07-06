import os


class ConfigGen:
    def __init__(self, cfg: list[(int, int)]):
        self.cfg = cfg

    def create_cfg_file(self):
        cfg = self.cfg
        destination_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
        os.makedirs(destination_dir, exist_ok=True)
        cfgfile = os.path.join(destination_dir, "config.cfg")
        with open(cfgfile, 'w') as file:
            for config in cfg:
                file.write(f'config set {config[0]} {config[1]}\n')
