import wx
import pygame
import sys
import os
from os.path import join

import config  # Your config.py

# Load and tile background using Pygame, then convert for wxPython
def get_tiled_bg(width, height, bg_filename="Purple.png"):
    pygame.init()
    path = join("assets", "Background", bg_filename)
    bg_img = pygame.image.load(path)
    bg_width, bg_height = bg_img.get_size()
    surface = pygame.Surface((width, height))
    for x in range(0, width, bg_width):
        for y in range(0, height, bg_height):
            surface.blit(bg_img, (x, y))
    arr = pygame.image.tostring(surface, "RGB")
    # Convert to wx.Bitmap for wxPython
    bitmap = wx.Bitmap.FromBuffer(width, height, arr)
    pygame.quit()
    return bitmap

class MenuPanel(wx.Panel):
    def __init__(self, parent, width, height):
        super().__init__(parent, size=(width, height))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.bg_bitmap = get_tiled_bg(width, height)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.AddButtons()
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def AddButtons(self):
        # Add stretch to center buttons vertically
        self.sizer.AddStretchSpacer(1)
        btn_play = wx.Button(self, label="Play", size=(200, 50))
        btn_load = wx.Button(self, label="Load Level", size=(200, 50))
        btn_load.Enable(True)
        btn_load.Bind(wx.EVT_BUTTON, self.OnLoadLevel)
        btn_settings = wx.Button(self, label="Settings", size=(200, 50))
        btn_quit = wx.Button(self, label="Quit", size=(200, 50))
        for btn in [btn_play, btn_load, btn_settings, btn_quit]:
            self.sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.sizer.AddStretchSpacer(1)

        btn_play.Bind(wx.EVT_BUTTON, self.OnPlay)
        btn_settings.Bind(wx.EVT_BUTTON, self.OnSettings)
        btn_quit.Bind(wx.EVT_BUTTON, self.OnQuit)

    def OnLoadLevel(self, event):
        with wx.FileDialog(self, "Open CSV Level", wildcard="CSV files (*.csv)|*.csv",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            path = fileDialog.GetPath()
            self.GetParent().Hide()
            # Call main.py with level file as argument
            os.system(f"{sys.executable} main.py \"{path}\"")
            self.GetParent().Close()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self.bg_bitmap, 0, 0)

    def OnPlay(self, event):
        # Close the menu and start the game
        self.GetParent().Hide()
        os.system(f"{sys.executable} main.py")
        self.GetParent().Close()

    def OnSettings(self, event):
        # Simple settings dialog for resolution
        choices = ["640x480", "800x600", "1024x768", "1280x720", "1920x1080"]
        dlg = wx.SingleChoiceDialog(self, "Choose resolution:", "Settings", choices)
        if dlg.ShowModal() == wx.ID_OK:
            val = dlg.GetStringSelection()
            width, height = map(int, val.split('x'))
            # Update config.py (overwriting WIDTH and HEIGHT)
            self.update_config_resolution(width, height)
            wx.MessageBox(f"Resolution set to {width}x{height}.\nRestarting menu...", "Settings", wx.OK | wx.ICON_INFORMATION)
            # Restart menu to apply new resolution
            python = sys.executable
            os.execl(python, python, * sys.argv)
        dlg.Destroy()

    def update_config_resolution(self, width, height):
        lines = []
        with open("config.py", "r") as f:
            for line in f:
                if line.startswith("WIDTH"):
                    lines.append(f"WIDTH = {width}\n")
                elif line.startswith("HEIGHT"):
                    lines.append(f"HEIGHT = {height}\n")
                else:
                    lines.append(line)
        with open("config.py", "w") as f:
            f.writelines(lines)

    def OnQuit(self, event):
        self.GetParent().Close()

class MenuFrame(wx.Frame):
    def __init__(self):
        width, height = config.WIDTH, config.HEIGHT
        super().__init__(None, title="Platformer Menu", size=(width, height),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = MenuPanel(self, width, height)
        self.Center()

def run_menu():
    app = wx.App(False)
    frame = MenuFrame()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    run_menu()