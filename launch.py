import wx
from scedasticity import MainFrame


class MyApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'Ranked data analysis ( B. Aoun et al )')
        frame.Show(True)
        return True

app = MyApp(0)
app.MainLoop() 



