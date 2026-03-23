# The entry point of the application. This file creates the main window instance and starts the mainloop()
import tkinter as tk

# Runs the window (Root has to be run before anything else)
root = tk.Tk()

# Window properties
root.title("ASA Sign-in System")
root.configure(background="white")
root.minsize(720, 1280)
root.geometry("300x300+50+50")

# Widgets
# Images

# Labels
lblEnterName = tk.Label(root, text="Enter Name")
lblNotices = tk.Label(root, text="Notices")

# Asigned Widgets
# Images

# Labels
lblEnterName.pack()
lblNotices.pack()

# Runs inputs from user
root.mainloop()
