import tkinter as tk

class Tooltip:
    """
    Simple tooltip for Tkinter widgets. Shows on hover. Styled for Win98 look.
    Usage: Tooltip(widget, text="Help text")
    """
    def __init__(self, widget, text, bg='#FFFFE1', fg='#000000', font=("MS Sans Serif", 9)):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font = font
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 24
        y = y + self.widget.winfo_rooty() + 24
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background=self.bg,
            foreground=self.fg,
            relief='solid',
            borderwidth=1,
            font=self.font,
            padx=6,
            pady=2
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# Small test block
if __name__ == "__main__":
    root = tk.Tk()
    btn = tk.Button(root, text="Hover me")
    btn.pack(padx=40, pady=40)
    Tooltip(btn, text="This is a tooltip!")
    root.mainloop() 