# The entry point of the application. This file creates the main window instance and starts the mainloop()
import tkinter as tk

# colors etc (theme)
import theme

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
frm_enter_name_area = tk.Frame(root, width=800, height=720)
frm_enter_name_area.place(x=0, y=0)
frm_enter_name = tk.Frame(frm_enter_name_area, width=600, height=90, bg="purple")
frm_enter_name.place(x=100, y=300)

frm_notices_area = tk.Frame(root, width=480, height=720, bg="blue")
frm_notices_area.place(x=800, y=0)

# Labels
lbl_enterName = tk.Label(root, text="Enter Name")
lbl_enterName.place(x=300, y=270)

lbl_notices = tk.Label(root, text="Notices")
lbl_notices.place(x=1000, y=100)
# Entry
ent_enter_name = tk.Entry(frm_enter_name)
ent_enter_name.insert(0, "Enter your text")
ent_enter_name.place(x=5, y=5)

# Buttons
btn_admin = tk.Button(frm_enter_name_area, text="Admin", width=20, height=1)
btn_admin.place(x=0, y=0)

# Runs inputs from user
root.mainloop()
