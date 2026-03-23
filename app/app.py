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
frmEnterNameArea = tk.Frame(root, width=800, height=720)
frmEnterName = tk.Frame(frmEnterNameArea, width=600, height=90, bg="purple")

frmNoticesArea = tk.Frame(root, width=480, height=720, bg="blue")

# Labels
lblEnterName = tk.Label(root, text="Enter Name")
lblNotices = tk.Label(root, text="Notices")

# Buttons
btnAdmin = tk.Button(frmEnterNameArea, text="Admin", width=20, height=1)

# # Asigned Widgets
# Frames
frmEnterNameArea.place(x=0, y=0)
frmEnterName.place(x=100, y=300)

frmNoticesArea.place(x=800, y=0)

# Labels
lblEnterName.place(x=300, y=270)

lblNotices.place(x=1000, y=100)

# Button
btnAdmin.place(x=0, y=0)

# Runs inputs from user
root.mainloop()
