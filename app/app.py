# The entry point of the application. This file creates the main window instance and starts the mainloop()
import tkinter as tk

# Runs the window (Root has to be run before anything else)
root = tk.Tk()

# Window properties
root.title("ASA Sign-in System")
root.configure(bg="white")
root.minsize(1280, 720)
root.geometry("300x300+50+50")

# makes the window full screen borderless
# root.attributes("-fullscreen", True)
# root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
# Will have to test this
# width = root.winfo_screenwidth()
# height = root.winfo_screenheight()
# root.geometry(f"{width}x{height}+0+0")


# # Widgets

# Frames
frmEnterName = tk.Frame(root, width=800, height=720)
frmNotices = tk.Frame(root, width=480, height=720, bg="blue")

# Labels
lblEnterName = tk.Label(root, text="Enter Name")
lblNotices = tk.Label(root, text="Notices")

# # Asigned Widgets
# Frames
frmEnterName.place(x=0, y=0)
frmNotices.place(x=800, y=0)

# Labels

# Runs inputs from user
root.mainloop()
