from tkinter import Label, simpledialog, Entry, W


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
