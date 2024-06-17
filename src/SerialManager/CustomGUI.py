from tkinter import Label, simpledialog, Entry, W, ttk, messagebox


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

    def __init__(self, root, items, values, description):
        self.root = root
        self.root.title("Config create")
        self.tree = ttk.Treeview(root, columns='Value', show='tree headings')
        self.tree.pack(fill='both', expand=True)

        self.tree.heading('#0', text='Configurations', anchor='w')
        self.tree.heading('Value', text='Value', anchor='w')

        self.description = description

        self.create_list(items, values)

    def create_list(self, list_items, values):
        for item, value in zip(list_items, values):
            parent = self.tree.insert('', 'end', text=item, values=(value,))
            self.tree.set(parent, 'Value', value)

        self.tree.bind('<Double-1>', self.on_double_click)

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)

        match column:
            case '#0':
                messagebox.showinfo(title='', message=self.description[self.tree.index(item=str(item_id))])
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
                exit()  # Never happens

    def update_value(self, entry, item_id):
        new_value = entry.get()
        try:
            self.tree.set(item_id, 'Value', int(new_value))
        except ValueError:
            self.tree.set(item_id, 'Value', 0)
        entry.destroy()
        print(f"New value -> {item_id} : {new_value}")
        # TODO config_builder
