import tkinter as tk
from database import init_db
from login import LoginWindow

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
