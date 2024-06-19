from tkinter import Label, simpledialog, Entry, W, ttk, Toplevel, LEFT, SOLID, Button


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


class CustomDialog(simpledialog.Dialog):
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


class TesteConfig(simpledialog.Dialog):

    def __init__(self, root, items, values, description, description_long, units):
        self.root = root
        self.root.title("Config create")
        self.root.geometry("600x400")

        self.tree = ttk.Treeview(root, columns=['Value', 'Unit'], show='tree headings')
        self.tree.pack(fill='both', expand=True)

        self.tree.heading('#0', text='Configurations', anchor='w')
        self.tree.heading('Unit', text='Unit', anchor='w')
        self.tree.heading('Value', text='Value', anchor='w')

        self.description = description
        self.description_long = description_long
        self.create_list(items, values, units)

        self.tooltip = ToolTip(self.tree)

        self.current_item = None

    def create_list(self, list_items, values, units):
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
                x, y, width, height = self.tree.bbox(item_id, column)
                value = self.tree.item(item_id, 'values')[0]

                entry = ttk.Entry(self.tree, width=30)
                entry.insert(0, value)
                entry.place(x=x, y=y, width=width, height=height)
                entry.bind('<Return>', lambda e: self.update_value(entry, item_id))
                entry.focus()

                entry.bind('<Escape>', lambda e: entry.destroy())
            case _:
                pass

    def update_value(self, entry, item_id):
        new_value = entry.get()
        try:
            self.tree.set(item_id, 'Value', int(new_value))
        except ValueError:
            self.tree.set(item_id, 'Value', 0)
        entry.destroy()
        print(f"New value -> {item_id} : {new_value}")
        # TODO config_builder


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
