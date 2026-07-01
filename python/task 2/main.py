import tkinter as tk
from gui import BMICalculatorApp

def main():
    # Attempt to enable High-DPI scaling awareness on Windows for sharp fonts
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        # Gracefully pass if not on Windows or shell has restrictions
        pass

    root = tk.Tk()
    
    # Create the application logic
    app = BMICalculatorApp(root)
    
    # Run the window main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
