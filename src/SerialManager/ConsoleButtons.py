from tkinter import Tk, Text, Button, END


class ConsoleButtons:
    def __init__(self,
                 root: Tk,
                 title: str,
                 button_width: int = 15,
                 button_height: int = 2,
                 font: (str, int) = ('Arial',  12)):

        self.root = root
        self.console = Text(self.root, wrap="word")
        self.console.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.root.title(title)
        self.root.geometry('800x600')
        self.root.configure(padx=10, pady=10)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=4)
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=2)

        self.fg = 'black'
        self.width = button_width
        self.height = button_height
        self.font = font

    def button1(self,
                text: str,
                bg: str,
                command):
        (Button(self.root,
                text=text,
                bg=bg,
                fg=self.fg,
                width=self.width,
                height=self.height,
                font=self.font,
                command=lambda: command())
         .grid(row=0, column=0, padx=5, pady=5, sticky="nsew"))

        return self

    def button2(self,
                text: str,
                bg: str,
                command):
        (Button(self.root,
                text=text,
                bg=bg,
                width=self.width,
                height=self.height,
                font=self.font,
                command=lambda: command())
         .grid(row=0, column=1, padx=5, pady=5, sticky="nsew"))

        return self

    def button3(self,
                text: str,
                bg: str,
                command):
        (Button(self.root,
                text=text,
                bg=bg,
                width=self.width,
                height=self.height,
                font=self.font,
                command=lambda: command())
         .grid(row=1, column=0, padx=5, pady=5, sticky="nsew"))

        return self

    def button4(self,
                text: str,
                bg: str,
                command):
        (Button(self.root,
                text=text,
                bg=bg,
                width=self.width,
                height=self.height,
                font=self.font,
                command=lambda: command())
         .grid(row=1, column=1, padx=5, pady=5, sticky="nsew"))

        return self

    def write_to_console(self, text) -> None:
        self.console.insert(END, f'{text}\n')
        self.console.update()

    def clear_console(self) -> None:
        self.console.delete(1.0, END)

    def read_console(self) -> str:
        self.console.update()
        return self.console.get(1.0, END)

    def mainloop(self) -> None:
        """
        Hacky way to make the button declaration easier
        while giving control to when to call the mainloop function
        """
        self.root.mainloop()
