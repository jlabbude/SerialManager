import os
import tkinter as tk
from dataclasses import dataclass, field

import yaml

from SerialManager.CreateConfigGUI import CreateConfigGui


@dataclass
class ConfigStruct:
    values: list[int] = field(default_factory=list)
    parameter: list[int] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    description_long: list[str] = field(default_factory=list)
    units: list[str] = field(default_factory=list)
    select_list: list[str | dict[str: list[str]]] = field(default_factory=list)
    list_flags: list[bool | None] = field(default_factory=list)
    range: list[(int, int), None] = field(default_factory=list)
    disabled: list[int, str, None] = field(default_factory=list)


class YaMLFile:

    def __init__(self, root: tk.Tk):
        gui_display_config = ConfigStruct()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'abeeway-config-template.yaml'), 'r') as yamlfile:
            config_data: dict[dict] = yaml.safe_load(yamlfile).get('config', [{}])
        param_names = [value for value in config_data]
        for name in param_names:
            gui_display_config.values.append(config_data.get(name).get('value'))
            gui_display_config.description.append(config_data.get(name).get('description'))
            gui_display_config.description_long.append(config_data.get(name).get('description-long'))
            gui_display_config.units.append(config_data.get(name).get('unit'))
            gui_display_config.select_list.append(config_data.get(name).get('list'))
            gui_display_config.list_flags.append(config_data.get(name).get('list-type'))
            gui_display_config.parameter.append(config_data.get(name).get('parameter'))
            if config_data.get(name).get('disabled') is not None:
                gui_display_config.disabled.append(int(config_data.get(name).get('disabled')))

            else:
                gui_display_config.disabled.append(None)
            if (config_data.get(name).get('range-high') is not None
                    or config_data.get(name).get('range-low') is not None):
                if config_data.get(name).get('range-high') is str or config_data.get(name).get('range-low') is str:
                    gui_display_config.range.append(((int(config_data.get(name).get('range-low')), 16),
                                                     (int(config_data.get(name).get('range-high')), 16)))
                else:
                    gui_display_config.range.append((config_data.get(name).get('range-low'),
                                                     (config_data.get(name).get('range-high'))))
            else:
                gui_display_config.range.append(None)
        CreateConfigGui(root=root,
                        items=param_names,
                        values=gui_display_config.values,
                        description=gui_display_config.description,
                        description_long=gui_display_config.description_long,
                        units=gui_display_config.units,
                        select_list=gui_display_config.select_list,
                        list_flag=gui_display_config.list_flags,
                        parameters=gui_display_config.parameter,
                        rangehl=gui_display_config.range,
                        disabled=gui_display_config.disabled)  # <- Type seems to be wrong, but it's on puporse,
                                                               # as all None values are erased before getting here
        root.mainloop()

        exit()
