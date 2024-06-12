from tkinter import Label, simpledialog, Entry, W, ttk


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

    def __init__(self, root, list_items):
        self.root = root
        self.root.title("Dropdown List App")
        self.tree = ttk.Treeview(root)
        self.tree.pack(fill='both', expand=True)

        self.tree.heading('#0', text='Configurations', anchor='w')

        self.create_list(list_items)

    def create_list(self, list_items):
        for key, value in list_items:
            parent = self.tree.insert('', 'end', text=key)
            for sub_key, sub_value in value.items():
                self.create_value_entry(parent, sub_key)

    def create_value_entry(self, parent, sub_key):
        frame = ttk.Frame(self.root)
        self.tree.insert(parent, 'end', text=sub_key, open=True, values=(frame,))

        # Bind click event to open the dialog
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        item_text = self.tree.item(item_id, "text")

        if self.tree.parent(item_id):  # Check if it is a child node
            value = simpledialog.askinteger("Input", f"Enter value for {item_text}:")
            if value is not None:
                print(f"Entered value for {item_text}: {value}")

    @staticmethod
    def on_submit(value, sub_key):
        print(f"Value entered for {sub_key}: {value}")
