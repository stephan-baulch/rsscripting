import tkinter
import customtkinter


def default_app():
    customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = customtkinter.CTk()
    app.geometry("400x780")
    app.title("user_interface.py")

    return app


def default_frame(app):
    frame = customtkinter.CTkFrame(master=app)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    return frame


def default_form(frame, placeholder, callback):
    entry = customtkinter.CTkEntry(master=frame, placeholder_text=placeholder)
    entry.pack(pady=10, padx=10)

    button = customtkinter.CTkButton(master=frame, text="Submit", command=callback)
    button.pack(pady=10, padx=10)


def simple_ui(placeholder, callback):
    app = default_app()
    frame = default_frame(app)
    default_form(frame, placeholder, callback)
    return app


def dialog_input(labelMessage):
    dialog = customtkinter.CTkInputDialog(text=labelMessage)
    return dialog.get_input()

# app.mainloop() must run after setting it up
