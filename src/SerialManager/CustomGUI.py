from tkinter import Label, simpledialog, Entry, W, ttk, Toplevel, LEFT, SOLID, Button, Listbox, BOTH, END, \
    messagebox, MULTIPLE, Tk


class HidePassword(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.password_entry = None
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        Label(master, text="Insert password:").grid(row=0)
        self.password_entry = Entry(master, show="*")
        self.password_entry.grid(row=0, column=1)
        return self.password_entry

    def apply(self):
        self.result = self.password_entry.get()


class CustomDialog:
    def __init__(self, parent, title=None):
        self.num_entry = None
        self.name_entry = None
        self.name = None
        self.starting_num = None
        super().__init__(parent, title=title)

    def body(self, master):
        Label(master, text="Name:").grid(row=0, column=0, sticky=W)
        self.name_entry = Entry(master)
        self.name_entry.grid(row=0, column=1)

        Label(master, text="Number:").grid(row=1, column=0, sticky=W)
        self.num_entry = Entry(master)
        self.num_entry.grid(row=1, column=1)

        return self.name_entry  # initial focus

    def apply(self):
        self.name = self.name_entry.get()
        try:
            self.starting_num = int(self.num_entry.get())
        except ValueError:
            self.starting_num = None


class ConfigGUI:

    def __init__(self,
                 root,
                 items,
                 parameters,
                 values,
                 description,
                 description_long,
                 units,
                 select_list,
                 list_flag,
                 rangehl: list[(int, int), None],
                 disabled: list[int, None]):
        self.root = root
        self.root.title("Config create")
        self.root.geometry("600x400")

        self.tree = ttk.Treeview(root, columns=['Value', 'Unit'], show='tree headings')
        self.tree.pack(fill='both', expand=True)

        self.tree.heading('#0', text='Configurations', anchor='w')
        self.tree.heading('Unit', text='Unit', anchor='w')
        self.tree.heading('Value', text='Value', anchor='w')

        self.disabled: list[int, None] = disabled
        self.rangehl: list[(int, int), None] = rangehl
        self.description = description
        self.description_long = description_long
        self.select_list = select_list
        self.list_flag = list_flag
        self.create_gui_list(items, values, units)

        self.ok_button = Button(self.root, text="OK", command=lambda: self.on_ok())
        self.ok_button.pack(pady=10)
        self.cfg: list[(int, int)] = []
        self.parameters = parameters

        self.initial_cfg(parameters, values)

        self.tooltip = ToolTip(self.tree)

        self.current_item = None
        
    def initial_cfg(self, parameters: list[int], values: list[int]) -> None:
        cfg = self.cfg
        for param, val in zip(parameters, values):
            cfg.append((param, val))

    def create_select_list(self, select_list):
        popup = Toplevel(self.root)
        popup.title("Select Items")
        popup.geometry("300x300")

        listbox = Listbox(popup)
        listbox.pack(padx=10, pady=10, expand=True, fill=BOTH)

        selected_item = ()

        def get_selected_items():
            nonlocal selected_item
            selected_item = listbox.curselection()
            popup.destroy()

        for field in select_list:
            listbox.insert(END, field)

        btn_select = Button(popup, text="Select", command=get_selected_items)
        btn_select.pack(pady=10)
        btn_select.wait_window()

        if selected_item == ():
            messagebox.showwarning("No Selection",
                                   "Please select at least 1.")
            return
        else:
            return selected_item[0]

    def create_bit_list(self, select_list):
        popup = Toplevel(self.root)
        popup.title("Select Items")
        popup.geometry("300x300")

        listbox = Listbox(popup, selectmode=MULTIPLE)
        listbox.pack(padx=10, pady=10, expand=True, fill=BOTH)

        dec = 0

        def get_selected_items():
            selected_indices = listbox.curselection()
            nonlocal dec
            dec = int(''.join(['1' if bit in selected_indices else '0' for bit in [*range(0, len(select_list))]]), 2)
            popup.destroy()

        for choice in reversed(select_list):
            listbox.insert(END, choice)

        btn_select = Button(popup, text="Select", command=get_selected_items)
        btn_select.pack(pady=10)
        btn_select.wait_window()

        if dec == 0:
            messagebox.showwarning("No Selection",
                                   "Please select at least 1 application.")
            return 0
        else:
            return dec

    @staticmethod
    def create_button_list(select_list):
        root2 = Tk()
        button = ButtonConfig(root=root2, select_list=select_list)
        root2.wait_window()

        return button.values

    def create_gui_list(self, list_items, values, units):
        for item, value, unit in zip(list_items, values, units):
            parent = self.tree.insert('', 'end', text=item, values=(value,))
            self.tree.set(parent, 'Value', value)
            self.tree.set(parent, 'Unit', unit)

        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Motion>', self.on_mouse_hover)
        self.tree.bind('<Leave>', self.on_mouse_leave)

    def on_mouse_hover(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id != self.current_item:
            self.tooltip.hidetip()
            self.current_item = item_id
            if item_id:
                item_index = self.tree.index(item_id)
                if item_index < len(self.description):
                    self.tooltip.showtip(self.description[item_index], event.x, event.y)

    def on_mouse_leave(self, _event):
        self.tooltip.hidetip()
        self.current_item = None

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        description_long = self.description_long[self.tree.index(item_id)]
        select_list = self.select_list[self.tree.index(item_id)]
        list_flag = self.list_flag[self.tree.index(item_id)]
        index = (int(self.tree.identify_row(y=event.y).removeprefix('I'), 16))-1

        match column:
            case '#0':
                if description_long:
                    top = Toplevel(self.root)
                    top.title('')
                    text_label = Label(top, text=description_long)
                    text_label.pack(padx=20, pady=20)
                    ok_button = Button(top, text="OK", command=top.destroy)
                    ok_button.pack(pady=10)
            case '#1':
                match list_flag:
                    case 0:
                        value = self.create_select_list(select_list=select_list)
                        param = list(self.cfg[index])[0]
                        self.cfg[index] = (param, value)

                        self.tree.set(value=value,
                                      item=item_id,
                                      column='Value')
                    case 1:
                        value = self.create_bit_list(select_list=select_list)
                        param = list(self.cfg[index])[0]
                        self.cfg[index] = (param, value)

                        self.tree.set(value=value,
                                      item=item_id,
                                      column='Value')
                    case 2:
                        value = self.create_button_list(select_list=select_list)
                        param = list(self.cfg[index])[0]
                        self.cfg[index] = (param, value)

                        self.tree.set(value=value,
                                      item=item_id,
                                      column='Value')
                    case None:
                        x, y, width, height = self.tree.bbox(item_id, column)
                        value = self.tree.item(item_id, 'values')[0]

                        entry = ttk.Entry(self.tree, width=30)
                        entry.insert(0, value)
                        entry.place(x=x, y=y, width=width, height=height)
                        entry.bind('<Return>', lambda e: self.update_value(entry, item_id, index))
                        entry.focus()

                        entry.bind('<Escape>', lambda e: entry.destroy())

    def update_value(self, entry, item_id, index):
        new_value = entry.get()
        intval: int = int(new_value)
        rangehl: (int, int) = (self.rangehl[index][0], self.rangehl[index][1])
        disabled: int | None = self.disabled[index]
        try:
            if rangehl[0] is not None and intval < rangehl[0]:
                if disabled is not None:
                    ask = messagebox.askyesno(title="Warning",
                                              message="Value is lower than minimum, disable parameter?")
                    if ask:
                        intval = disabled
                    else:
                        intval = rangehl[0]
                else:
                    intval = rangehl[0]
            elif rangehl[1] is not None and intval > rangehl[1]:
                if disabled is not None:
                    ask = messagebox.askyesno(title="Warning",
                                              message="Value is higher than maximum, disable parameter?")
                    if ask:
                        intval = disabled
                    else:
                        intval = rangehl[1]
                else:
                    intval = rangehl[1]
            self.tree.set(item_id, 'Value', intval)
            param = list(self.cfg[index])[0]
            self.cfg[index] = (param, intval)

        except ValueError:
            self.tree.set(item_id, 'Value', 0)
        entry.destroy()

    def on_ok(self):
        self.root.destroy()


class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None

    def showtip(self, text, x, y):
        if self.tipwindow or not text:
            return
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class ButtonConfig:
    def __init__(self, root, select_list: list[dict[str: list[str]]]):
        self.root = root
        self.select_list = select_list

        self.root.title("Config create")
        self.root.geometry("600x400")

        self.tree = ttk.Treeview(root, columns=['Action'], show='tree headings')
        self.tree.pack(fill='both', expand=True)

        self.tree.heading('#0', text='Button', anchor='w')
        self.tree.heading('Action', text='Mapping', anchor='w')

        self.create_gui_list(select_list=select_list)

        self.ok_button = Button(self.root, text="OK", command=lambda: self.on_ok())
        self.ok_button.pack(pady=10)

        self.values: list[str] = ['0001', '0010', '0100', '0001', '0000']

    def create_gui_list(self, select_list):
        for dicts in select_list:  # lol
            for keys in dicts.keys():
                parent = self.tree.insert('', 'end', text=keys, values=(0,))
                self.tree.set(parent, 'Action', dicts[keys][0])

        self.tree.bind('<Double-1>', self.on_double_click)

    def create_bit_list(self, select_list, index) -> str:
        popup = Toplevel(self.root)
        popup.title("Select Items")
        popup.geometry("300x300")

        listbox = Listbox(popup)
        listbox.pack(padx=10, pady=10, expand=True, fill=BOTH)

        selected_item = ()

        def get_selected_items():
            nonlocal selected_item
            selected_item = listbox.curselection()
            popup.destroy()

        for dicts in list(select_list[index].values())[0]:
            listbox.insert(END, dicts)

        btn_select = Button(popup, text="Select", command=get_selected_items)
        btn_select.pack(pady=10)
        btn_select.wait_window()

        self.values[index] = f'{selected_item[0]:04b}'
        if selected_item == ():
            messagebox.showwarning("No Selection",
                                   "Please select at least 1.")
            return '0000'
        else:
            return self.values[index]

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        row = int(self.tree.identify_row(y=event.y).removeprefix('I'))

        match row:
            case 5:
                self.tree.set(value=self.create_bit_list(select_list=self.select_list, index=row - 1),
                              item=item_id,
                              column='Action')
            case _:
                self.tree.set(value=self.create_bit_list(select_list=self.select_list, index=row - 1),
                              item=item_id,
                              column='Action')

    def on_ok(self):
        self.values = int(''.join(iter(self.values)), 2)
        self.root.destroy()
