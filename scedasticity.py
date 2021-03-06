# python standard libraries imports
import os
import sys
import warnings

# import numpy
try:
    import numpy as np
    from numpy.linalg import norm
except:
    raise Exception("numpy library is not installed.")
# import wx
try:
    import wx
    #import wx.lib.agw.supertooltip as STT
except:
    raise Exception("wx library is not installed")
# import matplotlib
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    from matplotlib.backends.backend_wx import NavigationToolbar2Wx, _load_bitmap
    from matplotlib.figure import Figure
except:
    raise Exception("matplotlib library is not installed")
 
# import parameters
try:
    from parameters import parameters as PARAMETERS
except:
    raise Exception("scedasticity 'parameters.py' is missing")


# set default dir
DEFAULT_DIR = os.path.abspath(PARAMETERS["defaultdir"])
if not os.path.isdir(DEFAULT_DIR) or not os.path.exists(DEFAULT_DIR):
    DEFAULT_DIR = os.path.expanduser("~")


def SET_GENERAL_PARAMETERS(**kwargs):
    params = globals()["PARAMETERS"]
    for k,v in kwargs.items():
        if params.has_key(k):
            params[k] = v
    # open for writing
    try:
        fd = open("parameters.py", 'w')
    except:
        dlg = wx.MessageDialog(self, "Can't open 'parameters.py file, maybe access is not granted.",
                               "Can't access file", wx.OK|wx.ICON_WARNING)
        result = dlg.ShowModal()
        dlg.Destroy()
        return
    fd.write("# python imports\n")
    fd.write("import os\n\n")
    fd.write("parameters = {}\n")
    for k,v in params.items():
        fd.write("parameters['%s'] = %s\n"%(str(k),str(v)))
    fd.close()
    

def GET_INDEX_RANGE_FROM_STRING(valStr):
    valStr = str(valStr)
    if not len(valStr.strip()):
        return "",None
    # if range wit : given
    if ":" in valStr:
        val = valStr.split(":")
        if len(val)!=3:
            return False, False
        try:
            val = [int(v) for v in val]
        except:
            return False, False
        for v in val:
            if v <0:
                return False, False
            if val[0]>=val[1]:
                return False, False 
            if val[2]==0:
                return False, False 
        newStr = "%i : %i : %i"%(val[0], val[1], val[2])
        val    = range(val[0], val[1], val[2])
        return newStr, val
    # if numbers wit : given
    else:
        val = valStr.split(",")
        try:
            val = [int(v) for v in val if v.strip()]
        except:
            return False, False 
        for v in val:
            if v <0:
                return False, False 
        val    = sorted(set(val))
        newStr = ""
        for v in val:
            newStr += "%i, "%v
        return newStr, val 
    
def GET_PARAGRAPH_FORMATED(paragraph, nchar = 50):    
    para      = paragraph.split()
    paragraph = ""
    sentence  = ""
    for word in para:
        if len(sentence) >= nchar:
            paragraph += sentence + "\n"
            sentence = ""
        sentence += " "+word
    paragraph += sentence
    return paragraph
        
               
class Widget(wx.BoxSizer):
    def __init__(self, parent, title, widget, help=""):
        # check parent
        assert isinstance(parent, wx.Window), "parent is normally the panel of the created wx.Window"
        # check widget
        assert isinstance(widget, (wx.Window,wx.Sizer) ),"widget must be a wx.Window or wx.Sizer for multiple widgets"
        # check help
        assert isinstance(help, str),"help must be a string"
        # initialize variables
        widgetSiserKwargs = {"proportion":1, "flag":wx.ALL|wx.EXPAND, "border":2}
        labelSiserKwargs  = {"proportion":0, "flag":wx.ALL|wx.ALIGN_CENTER_VERTICAL, "border":2}
        spacer            = 10
        orient            = wx.HORIZONTAL
        # initialize
        wx.BoxSizer.__init__(self,orient)
        # construct widget
        title = str(title)
        if len(title):
            title = wx.StaticText(parent=parent, id=-1, label=title, style=wx.ALIGN_LEFT)
            par = GET_PARAGRAPH_FORMATED("%s"%(help), 50)
            title.SetToolTip( wx.ToolTip(par) )
            #ttp = STT.SuperToolTip(par, footer=" ")
            #ttp.SetTarget(title)
            #ttp.SetDrawHeaderLine(True)
            #ttp.SetHeader("Help")
            #ttp.ApplyStyle("Office 2007 Blue")
            #ttp.SetStartDelay(0.5)
            self.Add( title, **labelSiserKwargs)
            self.AddSpacer(spacer)
        else:
            title = None
            par = GET_PARAGRAPH_FORMATED("%s"%(help))
            #ttp = STT.SuperToolTip(par, footer=" ")
            #ttp.SetTarget(title)
            #ttp.SetDrawHeaderLine(True)
            #ttp.SetHeader("Help")
            #ttp.ApplyStyle("Office 2007 Blue")
            #ttp.SetStartDelay(0.5)
        #self.__ttp = ttp
        # add widget to self
        #title.Bind(wx.EVT_LEAVE_WINDOW, self._on_focus)
        self.Add( widget, **widgetSiserKwargs)
    
    def _on_focus(self, event):
        if event.GetEventObject() is self.__ttp.GetTarget():
            self.__ttp.DoHideNow()



class FloatSlider(wx.Slider):
    def __init__(self, parent, id=-1, value=0, minval=-1, maxval=1, res=1e-2,
                 size=wx.DefaultSize, style=wx.SL_HORIZONTAL,
                 name='floatslider'):
        self._value = value
        self._min = minval
        self._max = maxval
        self._res = res
        ival, imin, imax = [round(v/res) for v in (value, minval, maxval)]
        self._islider = super(FloatSlider, self)
        self._islider.__init__(parent, id, ival, imin, imax, size=size, style=style, name=name)
        self.Bind(wx.EVT_SCROLL, self._OnScroll)

    def _OnScroll(self, event):
        ival = self._islider.GetValue()
        imin = self._islider.GetMin()
        imax = self._islider.GetMax()
        if ival == imin:
            self._value = self._min
        elif ival == imax:
            self._value = self._max
        else:
            self._value = ival * self._res
        event.Skip()
        #print 'OnScroll: value=%f, ival=%d' % (self._value, ival)

    def GetValue(self):
        return self._value

    def GetMin(self):
        return self._min

    def GetMax(self):
        return self._max

    def GetRes(self):
        return self._res

    def SetValue(self, value):
        self._islider.SetValue(round(value/self._res))
        self._value = value

    def SetMin(self, minval):
        self._islider.SetMin(round(minval/self._res))
        self._min = minval

    def SetMax(self, maxval):
        self._islider.SetMax(round(maxval/self._res))
        self._max = maxval

    def SetRes(self, res):
        self._islider.SetRange(round(self._min/res), round(self._max/res))
        self._islider.SetValue(round(self._value/res))
        self._res = res

    def SetRange(self, minval, maxval):
        self._islider.SetRange(round(minval/self._res), round(maxval/self._res))
        self._min = minval
        self._max = maxval

        
class PlotFigure(wx.Dialog):
    def __init__(self, parent=None, title="plot", plotTitle='', mapOptions=False, compareOptions=False):
        wx.Dialog.__init__(self, parent=parent, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        toolbarSizer = wx.BoxSizer(wx.HORIZONTAL)
        # set background color
        self.SetBackgroundColour(wx.WHITE)
        # slider settings
        self.__sliderMax = 1000
        # initialize data
        self.__allData  = None
        self.__usedData = None
        self.__image    = None
        self.__vector   = None 
        # offset variables
        self.__labels        = []
        self.__offsetMaximum = 1
        self.__offsetPercent = 0
        # create figure, axes and canvas
        self.__figure = Figure(facecolor='white')
        self.__axes = self.__figure.add_subplot(111)
        self.__axes.set_title(str(plotTitle))
        self.__canvas = FigureCanvas(self, -1, self.__figure)
        self.__canvas.draw = self.draw
        self.__toolbar = NavigationToolbar2Wx(self.__canvas)
        #self.__toolbar.DeleteToolByPos(0) 
        # reset plot
        #replot = wx.Button(self, -1, label="Re-plot")
        #self.Bind(wx.EVT_BUTTON, self.on_replot, replot)
        # export data button
        self.__exportColumnWiseWid = wx.CheckBox(self, -1, label="Export column wise")
        self.__exportColumnWiseWid.SetValue(False)
        exportData = wx.Button(self, -1, label="Export data")
        self.Bind(wx.EVT_BUTTON, self.on_export_data, exportData)
        # add figure to sizer
        toolbarSizer
        self.__sizer.Add(self.__canvas, proportion=1, flag=wx.ALL|wx.EXPAND, border=2)
        toolbarSizer.Add(self.__toolbar, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        toolbarSizer.AddSpacer(20)
        #toolbarSizer.Add(replot, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        toolbarSizer.Add(exportData, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        toolbarSizer.Add(self.__exportColumnWiseWid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.__sizer.Add(toolbarSizer,  proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        # add map options
        if mapOptions:
            self.create_map_panel()
        # add compare options
        if compareOptions:
            self.create_compare_panel()
        # set sizer 
        self.SetSizer(self.__sizer)
        self.Fit()
    
    def create_map_panel(self):
        vSizer = wx.BoxSizer(wx.VERTICAL)   
        # add colormap
        maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
        self.__cmps = wx.Choice(self, id=-1, choices=maps)
        wid = Widget(parent=self, title="Colormap", widget=self.__cmps, help = "Set the image colormap")
        vSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2) 
        # min value
        self.__minValueSlider = wx.Slider(self, id=-1, value=0, minValue=0, maxValue=self.__sliderMax ,style=wx.SL_HORIZONTAL)
        wid = Widget(parent=self, title="Minimum value", widget=self.__minValueSlider, help = "Set the minimum clipping value of data.")
        vSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        # max value
        self.__maxValueSlider =  wx.Slider(self, id=-1, value=self.__sliderMax, minValue=0, maxValue=self.__sliderMax ,style=wx.SL_HORIZONTAL)
        wid = Widget(parent=self, title="Maximum value", widget=self.__maxValueSlider, help = "Set the maximum clipping value of data.")
        vSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        # events
        self.Bind(wx.EVT_SCROLL, self.on_min_value_slider, self.__minValueSlider)
        self.Bind(wx.EVT_SCROLL, self.on_max_value_slider, self.__maxValueSlider)
        self.Bind(wx.EVT_CHOICE, self.on_colormap, self.__cmps)
        # add to sizer
        self.__sizer.Add(vSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
    
    def create_compare_panel(self):
        vSizer = wx.BoxSizer(wx.VERTICAL) 
        # max value
        self.__offsetMaximumWid= wx.TextCtrl(self, id=-1, value=str(self.__offsetMaximum))
        wid = Widget(parent=self, title="Offset maximum", widget=self.__offsetMaximumWid, help = "Set the maximum offset allowed.")
        vSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.__offsetPercentWid =  wx.Slider(self, id=-1, value=self.__offsetPercent, minValue=0, maxValue=self.__sliderMax ,style=wx.SL_HORIZONTAL)
        wid = Widget(parent=self, title="Maximum value", widget=self.__offsetPercentWid, help = "Set the maximum clipping value of data.")
        vSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)     
        # events
        self.Bind(wx.EVT_TEXT, self.on_maximum_offset, self.__offsetMaximumWid)
        self.Bind(wx.EVT_SCROLL, self.on_offset_slider_percent, self.__offsetPercentWid)
        # add to sizer
        self.__sizer.Add(vSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        
    def draw(self, drawDC=None):
        FigureCanvas.draw(self.__canvas, drawDC=drawDC)
        xlimits = [int(l) for l in self.__axes.get_xlim()]
        ylimits = [int(l) for l in self.__axes.get_ylim()]
        self.__limits = [ylimits[0],ylimits[1],xlimits[0],xlimits[1]]
       
    def on_export_data(self, event):
        dialog = wx.FileDialog(parent=self, 
                               message="Save Data", 
                               defaultDir="", 
                               defaultFile="", 
                               style= wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        returned = dialog.ShowModal() 
        globals()["DEFAULT_DIR"] = dialog.GetDirectory()
        dialog.Destroy()        
        if returned == wx.ID_CANCEL:
            return 
        # get and format fname
        fname = dialog.GetPath()
        # export data
        if self.__exportColumnWiseWid.IsChecked():
            data = np.transpose(self.__usedData)
        else:
            data = self.__usedData
        np.savetxt(fname, data, fmt='%.8e', delimiter='  ', 
                   newline='\n', 
                   header="B. Aoun et al; Journal of Power Sources 279 (2015) 246-251", 
                   footer='', 
                   comments='# ')
        
    def plot_vector(self, data,
                          axis='on',
                          xLabel="number or files", yLabel="correlation",
                          ticksDirection="out"):
        self.__usedData = data
        while self.__axes.lines:
            self.__axes.lines.pop(0)
        self.__vector   = self.__axes.plot(data)
        self.__axes.axis(axis)
        self.__axes.set_xlabel(xLabel)
        self.__axes.set_ylabel(yLabel)
        self.__axes.get_yaxis().set_tick_params(direction=ticksDirection)
        self.__axes.get_xaxis().set_tick_params(direction=ticksDirection)
    
    def compare_vectors(self, data, labels,
                              axis='on',  
                              xLabel="number or points", yLabel="intensity",
                              ticksDirection="out"):
        self.__usedData = data
        self.__labels   = labels
        while self.__axes.lines:
            self.__axes.lines.pop(0)
        for idx in range(len(self.__usedData)):
            d = self.__usedData[idx]+ idx*(self.__offsetMaximum*self.__offsetPercent/100.) 
            self.__axes.plot(d, label=self.__labels[idx])
        self.__axes.axis(axis)
        self.__axes.set_xlabel(xLabel)
        self.__axes.set_ylabel(yLabel)
        self.__axes.get_yaxis().set_tick_params(direction=ticksDirection)
        self.__axes.get_xaxis().set_tick_params(direction=ticksDirection)
        self.__axes.legend(ncol = int(len(self.__labels)/10.)+1, frameon=False)
        
    def plot_image(self, data, extent=(0,100,0,100), colormap="jet",
                         axis='on', origin="lower",
                         xLabel="number or points", yLabel="number of files",
                         ticksDirection="out"):
        # normalize data
        self.__usedData = data
        self.__dMin = float(np.nanmin(self.__usedData))
        self.__dMax = float(np.nanmax(self.__usedData))
        # plot image
        self.__image = self.__axes.imshow( (self.__usedData-self.__dMin)/(self.__dMax-self.__dMin), 
                                            aspect="auto", origin=origin)
        #self.__image.set_extent(extent)
        self.__axes.axis(axis)
        self.__axes.set_xlabel(xLabel)
        self.__axes.set_ylabel(yLabel)
        self.__axes.get_yaxis().set_tick_params(direction=ticksDirection)
        self.__axes.get_xaxis().set_tick_params(direction=ticksDirection)
        # set colormap
        self.set_cmap(colormap)
        # set limits
        #self.__limits = [0,self.__usedData.shape[0],0,self.__usedData.shape[1]]
         
    def set_cmap(self, colormap):
        idx = self.__cmps.FindString(colormap)
        if idx == -1:
            idx = 0
        self.__cmps.SetSelection(idx)   
        self.set_colormap(colormap)
        
    def set_colormap(self, colormap):
        if self.__image is None: return
        self.__image.set_cmap(colormap)
        #FigureCanvasBase.draw(self.__canvas)
        self.__canvas.draw()

    def on_maximum_offset(self, event):
        try:
            val = event.GetEventObject().GetValue()
            val = float(val) 
        except:
            val = None            
        if val<0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__offsetMaximum))   
        else:            
            self.__offsetMaximum = val
        # compare data
        self.compare_vectors(self.__usedData, labels=self.__labels )
        self.__canvas.draw()
    
    def on_offset_slider_percent(self, event):
        self.__offsetPercent = float(self.__offsetPercentWid.GetValue())
        self.compare_vectors(self.__usedData, labels=self.__labels )
        self.__canvas.draw()
             
    def on_colormap(self, event):
        cmap = self.__cmps.GetString(self.__cmps.GetSelection())
        self.set_colormap( cmap )
        
    def on_min_value_slider(self, event):
        # get data
        data = np.copy(self.__usedData)
        # bring data to positive values
        dmin = np.nanmin(self.__usedData[self.__limits[0]:self.__limits[1],self.__limits[2]:self.__limits[3]])
        dmax = np.nanmax(self.__usedData[self.__limits[0]:self.__limits[1],self.__limits[2]:self.__limits[3]])-dmin
        data -= dmin
        # get min and max
        minValue = self.__minValueSlider.GetValue()
        maxValue = self.__maxValueSlider.GetValue()
        if minValue>=maxValue:
            self.__minValueSlider.SetValue(maxValue-1)
            minValue = maxValue-1 
        minValue = dmax*float(minValue)/float(self.__sliderMax)
        maxValue = dmax*float(maxValue)/float(self.__sliderMax)
        # clip values
        data =  np.clip(data, minValue, maxValue)  
        # get min and max
        dmin = np.nanmin(data)
        dmax = np.nanmax(data)
        # plot
        self.__axes.images[0].set_data( (data-dmin)/(dmax-dmin) )
        # set axis
        self.__axes.set_xlim(self.__limits[2],self.__limits[3])
        self.__axes.set_ylim(self.__limits[0],self.__limits[1])
        # redraw
        self.__canvas.draw()
        
    def on_max_value_slider(self, event):
        # get data
        data = np.copy(self.__usedData)
        # bring data to positive values
        dmin = np.nanmin(self.__usedData[self.__limits[0]:self.__limits[1],self.__limits[2]:self.__limits[3]])
        dmax = np.nanmax(self.__usedData[self.__limits[0]:self.__limits[1],self.__limits[2]:self.__limits[3]])-dmin
        data -= dmin
        # get min and max
        minValue = self.__minValueSlider.GetValue()
        maxValue = self.__maxValueSlider.GetValue()
        if minValue>=maxValue:
            self.__maxValueSlider.SetValue(minValue+1)
            maxValue = minValue+1 
        minValue = dmax*float(minValue)/float(self.__sliderMax)
        maxValue = dmax*float(maxValue)/float(self.__sliderMax)
        # clip values
        data =  np.clip(data, minValue, maxValue)  
        # get min and max
        dmin = np.nanmin(data)
        dmax = np.nanmax(data)
        # plot
        self.__axes.images[0].set_data( (data-dmin)/(dmax-dmin) )
        # set axis
        self.__axes.set_xlim(self.__limits[2],self.__limits[3])
        self.__axes.set_ylim(self.__limits[0],self.__limits[1])
        # redraw
        self.__canvas.draw()
        
    
    
class About(wx.Dialog):
    def __init__(self, title="About"):
        wx.Dialog.__init__(self, None, -1, title=title, size=(750,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.CenterOnScreen(wx.BOTH)
        # set background color
        self.SetBackgroundColour(wx.WHITE)
        # create paper text
        paper = "B. Aoun et al; Journal of Power Sources 279 (2015) 246-251"
        paper = wx.StaticText(self, -1, paper, (30,15), style=wx.ALIGN_CENTRE)
        paperfont = wx.Font(10, wx.MODERN, wx.ITALIC, wx.BOLD)
        paper.SetFont(paperfont)
        # create correlation formula image
        correlationIm = wx.StaticBitmap(self)
        correlationIm.SetBitmap(wx.Bitmap('correlation_formula.PNG'))
        # create scedasticity formula image
        scedasticityIm = wx.StaticBitmap(self)
        scedasticityIm.SetBitmap(wx.Bitmap('scedasticity_formula.PNG'))
        description = "This software is about a generalized method used to extract \
critical information from series of ranked correlated data. \
The method is generally applicable to all types of spectra evolving \
as a function of any arbitrary parameter. This approach is based on \
correlation functions and statistical scedasticity formalism."
        description = GET_PARAGRAPH_FORMATED(description)
        description = wx.StaticText(self, -1, description,(30,15), style=wx.ALIGN_CENTRE) 
        descriptionFont = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        description.SetFont(descriptionFont) 
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(description, 1, wx.ALIGN_CENTER|wx.BOTTOM, 2)
        vbox.AddSpacer(20)
        vbox.Add(correlationIm, 0,wx.ALIGN_CENTER|wx.BOTTOM, 2)
        vbox.Add(scedasticityIm, 0,wx.ALIGN_CENTER|wx.BOTTOM, 2)
        vbox.AddSpacer(20)
        vbox.Add(paper, 0, wx.ALIGN_CENTER|wx.TOP, 2)
        self.SetSizer(vbox)
        
    
        
        
class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(900, 500))
        self.SetIcon(wx.Icon('scedasticity16X16.PNG',wx.BITMAP_TYPE_PNG, 16,16))
        # initialize variables
        self.__files      = []
        self.__matrixFile = None
        # initialize data
        self.__allData  = []
        self.__usedData = []
        # initialize analysis data
        self.initialize_analysis_data()
        # analysis variable
        self.__filesInterval          = 1
        self.__scedasticityWindowSize = 25
        # initialize read parameters
        self.__comment        = "#"
        self.__delimiter      = " "
        self.__headerLines    = 0
        self.__footerLines    = 0
        self.__useColumn      = 0
        self.__readColumnWise = False
        # create main panel
        self.__panel = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        # create menubar
        self.build_menu_bar()
        # create notebook
        self.__notebook = wx.Notebook(self.__panel)
        # create main sizer
        self.__mainSizer   = wx.BoxSizer(wx.VERTICAL)
        # create files list control
        filesListPage = self.build_read_data_page()
        self.__notebook.AddPage(filesListPage, "Read data")
        # create data manipulation
        dataManipulationPage = self.build_data_manipulation_page()
        self.__notebook.AddPage(dataManipulationPage, "Data manipulation")
        # create variables widgets
        analysisParametersPage = self.build_analysis_parameters_page()
        self.__notebook.AddPage(analysisParametersPage, "Analysis parameters")
        # create loading variables
        actionButtonsSizer = self.create_action_buttons()
        # create progress bar
        self.__progressBar = wx.Gauge(self.__panel, range=100)
        # add to main sizer
        self.__mainSizer.Add(self.__notebook, 1, wx.ALL|wx.EXPAND, 5)
        self.__mainSizer.Add(actionButtonsSizer, proportion=0, flag=wx.ALL|wx.ALIGN_RIGHT, border=2)
        self.__mainSizer.Add(self.__progressBar, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        # set sizer
        self.__panel.SetSizerAndFit(self.__mainSizer) 
        # initialize files reading
        self.on_chi_file_parameter(None)
        # data manipulation variables
        self.initialize_data_manipulation()
         
    def initialize_analysis_data(self):
        self.__correlation  = None
        self.__scedasticity = None
    
    def initialize_data_manipulation(self):
        self.__useFiles              = {"":None}
        self.__ignoreFiles           = {"":None}
        self.__useDataPoints         = {"":None}
        self.__ignoreDataPoints      = {"":None}
        self.__manipulateDataFormula = ""
        self.__useFilesWid.ChangeValue("")
        self.__ignoreFilesWid.ChangeValue("")
        self.__useDataPointsWid.ChangeValue("")
        self.__ignoreDataPointsWid.ChangeValue("")
        self.__manipulateDataFormulaWid.ChangeValue("")
        
    def create_action_buttons(self):    
        # create bozSizer
        sb = wx.StaticBox(self.__panel, label="Available actions")
        horizontalSizer = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        # create actions
        self.__plotSelectedDataBut = wx.Button(self.__panel, -1, label="Plot selected files")
        self.Bind(wx.EVT_BUTTON, self.on_plot_selected_data, self.__plotSelectedDataBut)
        self.__plotSelectedDataBut.SetToolTip( wx.ToolTip("Plot an image of selected files.") )
        self.__plotAllDataBut = wx.Button(self.__panel, -1, label="Plot all data")
        self.Bind(wx.EVT_BUTTON, self.on_plot_data, self.__plotAllDataBut)
        self.__plotAllDataBut.SetToolTip( wx.ToolTip("Plot an image of all files.") )
        self.__compareSelectedDataBut = wx.Button(self.__panel, -1, label="Compare selected files")
        self.Bind(wx.EVT_BUTTON, self.on_compare_selected_data, self.__compareSelectedDataBut)
        self.__compareSelectedDataBut.SetToolTip( wx.ToolTip("Plot selected files as lines.") )
        correlation = wx.Button(self.__panel, -1, label="Correlation")
        correlation.SetToolTip( wx.ToolTip("Compute correlation.") )
        self.Bind(wx.EVT_BUTTON, self.on_compute_correlation, correlation)
        scedasticity = wx.Button(self.__panel, -1, label="Scedasticity")
        scedasticity.SetToolTip( wx.ToolTip("Compute scedasticity.") )
        self.Bind(wx.EVT_BUTTON, self.on_compute_scedasticity, scedasticity)
        horizontalSizer.Add(self.__plotSelectedDataBut, proportion=0, flag=wx.ALL, border=2)
        horizontalSizer.Add(self.__compareSelectedDataBut, proportion=0, flag=wx.ALL, border=2)
        horizontalSizer.Add(self.__plotAllDataBut, proportion=0, flag=wx.ALL, border=2)
        horizontalSizer.Add(correlation, proportion=0, flag=wx.ALL, border=2)
        horizontalSizer.Add(scedasticity, proportion=0, flag=wx.ALL, border=2)
        # add to sizer
        return horizontalSizer
        
    def build_read_data_page(self):
        panel     = wx.Panel(self.__notebook, id=wx.ID_ANY)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        ########################  files list control  ########################
        sb = wx.StaticBox(panel, label="Files are read from top to bottom")
        listCtrlSizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        listCtrlButtSizer = wx.BoxSizer(wx.HORIZONTAL)
        # create list control
        self.__filesWid = wx.ListBox(panel, -1, style=wx.LB_ALWAYS_SB|wx.LB_HSCROLL|wx.LB_EXTENDED)
        listCtrlSizer.Add(self.__filesWid, proportion=1, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_LISTBOX, self.on_files_selection, self.__filesWid)
        # create actions
        self.__moveUpWid = wx.Button(panel, -1, label="Move up")
        self.Bind(wx.EVT_BUTTON, self.on_move_up, self.__moveUpWid)
        self.__moveDownWid = wx.Button(panel, -1, label="Move down")
        self.Bind(wx.EVT_BUTTON, self.on_move_down, self.__moveDownWid)
        self.__invertFilesWid = wx.Button(panel, -1, label="Invert")
        self.Bind(wx.EVT_BUTTON, self.on_invert_order, self.__invertFilesWid)
        self.__discardFileWid = wx.Button(panel, -1, label="Discard")
        self.Bind(wx.EVT_BUTTON, self.on_discard_down, self.__discardFileWid)
        #listCtrlButtSizer.AddSpacer(10)
        self.__LoadData = wx.Button(panel, -1, label="Load")
        self.Bind(wx.EVT_BUTTON, self.on_load_data, self.__LoadData)
        # add to listCtrlButtSizer
        listCtrlButtSizer.Add(self.__moveUpWid, proportion=1, flag=wx.ALL, border=2)
        listCtrlButtSizer.Add(self.__moveDownWid, proportion=1, flag=wx.ALL, border=2)
        listCtrlButtSizer.Add(self.__invertFilesWid, proportion=1, flag=wx.ALL, border=2)
        listCtrlButtSizer.Add(self.__discardFileWid, proportion=1, flag=wx.ALL, border=2)
        listCtrlButtSizer.Add(self.__LoadData, proportion=1, flag=wx.ALL, border=2)
        # add listCtrlButtSizer
        listCtrlSizer.Add(listCtrlButtSizer, proportion=0, flag=wx.ALL|wx.ALIGN_RIGHT, border=2)
        # dis-activate all buttons
        self.__moveUpWid.Enable(False)
        self.__moveDownWid.Enable(False)
        self.__invertFilesWid.Enable(False)
        self.__discardFileWid.Enable(False)
        self.__LoadData.Enable(False)
        # set help
        self.__moveUpWid.SetToolTip( wx.ToolTip("Move UP selected files in the list.") )
        self.__moveDownWid.SetToolTip( wx.ToolTip("Move DOWN selected files in the list.") )
        self.__invertFilesWid.SetToolTip( wx.ToolTip("Invert up side down all files order in the list regardless of selection.") )
        self.__discardFileWid.SetToolTip( wx.ToolTip("Remove file from list.") )
        self.__LoadData.SetToolTip( wx.ToolTip("Load all files in list regardless of selection.") )
        ########################  reading parameters  ########################
        sb = wx.StaticBox(panel, label="Read files parameters")
        loadBoxSizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        # create comment
        self.__commentWid = wx.TextCtrl(panel, value=self.__comment)
        wid = Widget(parent=panel, title="Comment", widget=self.__commentWid, help = "The character used to indicate the start of a comment.")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_comment, self.__commentWid)
        # create delimiter
        self.__delimiterWid = wx.TextCtrl(panel, value=self.__delimiter)
        wid = Widget(parent=panel, title="Delimiter", widget=self.__delimiterWid, help = "The string used to separate values. By default, no delimiter is given which means any consecutive whitespaces act as delimiter.")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_delimiter, self.__delimiterWid)
        # create header lines
        self.__headerLinesWid = wx.TextCtrl(panel, value=str(self.__headerLines))
        wid = Widget(parent=panel, title="Header", widget=self.__headerLinesWid, help = "Skip the first lines consider as header.")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_header_lines, self.__headerLinesWid)
        # create footer lines
        self.__footerLinesWid = wx.TextCtrl(panel, value=str(self.__footerLines))
        wid = Widget(parent=panel, title="Footer", widget=self.__footerLinesWid, help = "Skip the last lines consider as footer.")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_footer_lines, self.__footerLinesWid)
        # create use column
        self.__useColumnWid = wx.TextCtrl(panel, value=str(self.__useColumn))
        wid = Widget(parent=panel, title="Data column", widget=self.__useColumnWid, help = "Select the data column to use. FIRST COLUMN IS 0")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_use_column, self.__useColumnWid)
        # create use column
        self.__readColumnWiseWid = wx.CheckBox(panel)
        self.__readColumnWiseWid.SetValue(self.__readColumnWise)
        wid = Widget(parent=panel, title="Column wise", widget=self.__readColumnWiseWid, help = "Set whether to read matrix column or row wise. When checked column wise is activated, which means every column of matrix data file will be considered as a data file.")
        loadBoxSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_CHECKBOX, self.on_read_column_wise, self.__readColumnWiseWid)
        ########################  add all to mainSizer  ########################
        mainSizer.Add(listCtrlSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=2)
        mainSizer.Add(loadBoxSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        panel.SetSizer(mainSizer)
        ########################  return panel  ########################
        return panel
        
    def build_analysis_parameters_page(self):
        panel     = wx.Panel(self.__notebook, id=wx.ID_ANY)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        ########################  analysis control  ########################        
        # create filesIntervalWid
        self.__filesIntervalWid = wx.TextCtrl(panel, value=str(self.__filesInterval ) )
        wid = Widget(parent=panel, title="Interval", widget=self.__filesIntervalWid, 
                     help = "Set the computation files interval. It must be a positive non-zero integer.\
The computation will be performed  between every 'interval' files. For instance, when interval is '1',\
correlation and scedasticity will be computed between successive files,\
When interval is '2' correlation and scedasticity will be computed between every other file, etc.")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_files_interval, self.__filesIntervalWid)
        # create scedasticityWindowSize
        self.__scedasticityWindowSizeWid = wx.TextCtrl(panel, value=str(self.__scedasticityWindowSize) )
        wid = Widget(parent=panel, title="Scedasticity window Size", widget=self.__scedasticityWindowSizeWid, help = "Set the window size (delta theta in formula) to compute scedasticity. It must be an odd positive integer")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT, self.on_scedasticity_window_size, self.__scedasticityWindowSizeWid)
        ########################  add all to mainSizer  ########################
        panel.SetSizer(mainSizer)
        ########################  return panel  ########################
        return panel
    
    def build_data_manipulation_page(self):
        panel     = wx.Panel(self.__notebook, id=wx.ID_ANY)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        ########################  analysis control  ########################        
        # create useFilesWid
        self.__useFilesWid = wx.TextCtrl(panel, value=str(""), style=wx.TE_PROCESS_ENTER)
        wid = Widget(parent=panel, title="Use files", widget=self.__useFilesWid, 
                     help = "Set the data files range to use. \
By default, an empty field means all data files are used. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201). \
HIT ENTER TO VALIDATE")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_use_data_files, self.__useFilesWid)
        # create ignoreFilesWid
        self.__ignoreFilesWid = wx.TextCtrl(panel, value=str("") , style=wx.TE_PROCESS_ENTER)
        wid = Widget(parent=panel, title="Ignore files", widget=self.__ignoreFilesWid, 
                     help = "Set the data files range to ignore. \
By default, an empty field means no data files are ignored. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201). \
HIT ENTER TO VALIDATE")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_ignore_data_files, self.__ignoreFilesWid)
        # create useDataPointsWid
        self.__useDataPointsWid = wx.TextCtrl(panel, value=str(""), style=wx.TE_PROCESS_ENTER)
        wid = Widget(parent=panel, title="Use data points", widget=self.__useDataPointsWid, 
                     help = "Set the data points range to use. \
By default, an empty field means all data points are used. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201). \
HIT ENTER TO VALIDATE")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_use_data_points, self.__useDataPointsWid)
        # create ignoreDataPoints
        self.__ignoreDataPointsWid = wx.TextCtrl(panel, value=str("") , style=wx.TE_PROCESS_ENTER)
        wid = Widget(parent=panel, title="Ignore data points", widget=self.__ignoreDataPointsWid, 
                     help = "Set the data points range to ignore. \
By default, an empty field means no data points are ignored. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201). \
HIT ENTER TO VALIDATE")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_ignore_data_points, self.__ignoreDataPointsWid)
        # create manipulateDataFormula
        self.__manipulateDataFormulaWid = wx.TextCtrl(panel, value=str("") , style=wx.TE_PROCESS_ENTER)
        wid = Widget(parent=panel, title="Manipulate", widget=self.__manipulateDataFormulaWid, 
                     help = "Use formula to manipulate all used data. \
The given formula will be applied on every data file. \
Keyword 'dataFile' is used to designate the variable in the formula. \
All numpy functions are allowed and can be called as np.functionName. \
By default, an empty field means data are used as is.\n \
e.g. np.log10(dataFile) # computes the normal log of all data.\n \
e.g. np.sin(dataFile) # computes the sin function of all data.\n \
HIT ENTER TO VALIDATE")
        mainSizer.Add(wid, proportion=0, flag=wx.ALL|wx.EXPAND, border=2)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_manipulate_data, self.__manipulateDataFormulaWid)
        ########################  add all to mainSizer  ########################
        panel.SetSizer(mainSizer)
        ########################  return panel  ########################
        return panel
    
    def build_menu_bar(self):
        # create menus
        self.__menubar = wx.MenuBar()
        file = wx.Menu()
        #about = wx.Menu()
        browseFiles = file.Append(-1, '&Browse files', 'Browse data files.')
        browseMatrix = file.Append(-1, '&Browse matrix', 'Browse matrix file containing N rows and M columns.')
        file.AppendSeparator()
        filesParameters = wx.Menu()
        file.AppendMenu(-1, '&Files parameters', filesParameters)
        chiParams = filesParameters.Append(-1, '&chi', 'chi files parameters')
        grParams  = filesParameters.Append(-1, '&gr', 'gr files parameters')
        sqParams  = filesParameters.Append(-1, '&sq', 'sq files parameters')
        file.AppendSeparator()
        about  = file.Append(-1, 'About', 'About')
        file.AppendSeparator()
        quit = wx.MenuItem(file, -1, '&Quit\tCtrl+Q', 'Quit the Application')
        file.AppendItem(quit)
        self.__menubar.Append(file, '&File')
        # create parameters menu
        params = wx.Menu()
        defDir = params.Append(-1, 'Set default directory', 'Set default directory')
        self.__menubar.Append(params, '&Parameters')
        # set menubar
        self.SetMenuBar(self.__menubar)
        self.CreateStatusBar()
        # bind menus
        self.Bind(wx.EVT_MENU, self.on_browse_files, browseFiles)
        self.Bind(wx.EVT_MENU, self.on_browse_matrix, browseMatrix)
        self.Bind(wx.EVT_MENU, self.on_quit, quit) 
        self.Bind(wx.EVT_MENU, self.on_chi_file_parameter, chiParams)      
        self.Bind(wx.EVT_MENU, self.on_gr_file_parameter, grParams)   
        self.Bind(wx.EVT_MENU, self.on_sq_file_parameter, sqParams)  
        self.Bind(wx.EVT_MENU, self.on_about, about) 
        self.Bind(wx.EVT_MENU, self.on_default_dir, defDir)         
    
    def on_use_data_files(self, event):
        newStr, val = GET_INDEX_RANGE_FROM_STRING(self.__useFilesWid.GetValue())
        if newStr is False:
            newStr = self.__useFiles.keys()[0]
        else:
            self.__useFiles = {}
            self.__useFiles[newStr] = val
        self.__useFilesWid.ChangeValue(newStr)
        if val is not False:
            self.__set_used_data()
        else:
            dlg = wx.MessageDialog(self, "Set the data files range to use. \
By default, an empty field means all data files are used. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201)", 
            "Wrong range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
        
    def on_ignore_data_files(self, event):
        newStr, val = GET_INDEX_RANGE_FROM_STRING(self.__ignoreFilesWid.GetValue())
        if newStr is False:
            newStr = self.__ignoreFiles.keys()[0]
        else:
            self.__ignoreFiles = {}
            self.__ignoreFiles[newStr] = val
        self.__ignoreFilesWid.ChangeValue(newStr)
        if val is not False:
            self.__set_used_data()
        else:
            dlg = wx.MessageDialog(self, "Set the data files range to ignore. \
By default, an empty field means no data files are ignored. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201).", 
            "Wrong range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            
    def on_use_data_points(self, event):
        newStr, val = GET_INDEX_RANGE_FROM_STRING(self.__useDataPointsWid.GetValue())
        if newStr is False:
            newStr = self.__useDataPoints.keys()[0]
        else:
            self.__useDataPoints = {}
            self.__useDataPoints[newStr] = val
        self.__useDataPointsWid.ChangeValue(newStr)
        if val is not False:
            self.__set_used_data()
        else:
            dlg = wx.MessageDialog(self, "Set the data points range to use. \
By default, an empty field means all data points are used. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201).", 
            "Wrong range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            
    def on_ignore_data_points(self, event):
        newStr, val = GET_INDEX_RANGE_FROM_STRING(self.__ignoreDataPointsWid.GetValue())
        if newStr is False:
            newStr = self.__ignoreDataPoints.keys()[0]
        else:
            self.__ignoreDataPoints = {}
            self.__ignoreDataPoints[newStr] = val
        self.__ignoreDataPointsWid.ChangeValue(newStr)
        if val is not False:
            self.__set_used_data()
        else:
            dlg = wx.MessageDialog(self, "Set the data points range to ignore. \
By default, an empty field means no data points are ignored. \
Entry can be a real range such as from:to:step (e.g. 0:100:1), \
or comma separated data indexes (e.g. 0,1,2,100,200,201).",
            "Wrong range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            
    def on_manipulate_data(self, event):
        formula = str( self.__manipulateDataFormulaWid.GetValue() ).strip()
        if not len(formula):
            self.__manipulateDataFormula = formula    
            self.__set_used_data()
        elif "dataFile" not in formula:
            self.__manipulateDataFormulaWid.ChangeValue(str(self.__manipulateDataFormula))
            dlg = wx.MessageDialog(self, "Use formula to manipulate all used data. \
The given formula will be applied on every data file. \
Keyword 'dataFile' is used to designate the variable in the formula. \
All numpy functions are allowed and can be called as np.functionName. \
By default, an empty field means data are used as is.\n \
e.g. np.log10(dataFile) # computes the normal log of all data.\n \
e.g. np.sin(dataFile) # computes the sin function of all data.", 
            "dataFile keyword not found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
        else:
            dataFile = np.arange(0,10,0.1)
            try:
                res = eval(formula)
                assert res.shape == dataFile.shape
            except:
                self.__manipulateDataFormulaWid.ChangeValue(str(self.__manipulateDataFormula))
            else:
                self.__manipulateDataFormula = formula    
                self.__set_used_data()
            
    def __set_used_data(self):
        self.initialize_analysis_data()
        if not len(self.__allData):
            self.__usedData = []
            return
        # set dataUsed
        npoints = len(self.__allData[0])
        ndata   = len(self.__allData)
        # get used data
        if self.__useFiles.values()[0] is None:
            useFiles = set(range(ndata))
        else:
            useFiles = set(self.__useFiles.values()[0])
        if self.__ignoreFiles.values()[0] is None:
            ignoreFiles = set([])
        else:
            ignoreFiles = set(self.__ignoreFiles.values()[0])
        useFiles = sorted(useFiles-ignoreFiles)
        data = [self.__allData[idx] for idx in useFiles if idx<ndata]
        # get used points
        if self.__useDataPoints.values()[0] is None:
            usePoints = set(range(npoints))
        else:
            usePoints = set(self.__useDataPoints.values()[0])
        if self.__ignoreDataPoints.values()[0] is None:
            ignorePoints = set([])
        else:
            ignorePoints = set(self.__ignoreDataPoints.values()[0])
        useFiles = np.array([idx for idx in sorted(usePoints-ignorePoints) if idx < npoints], dtype=np.int)
        # apply formula
        if len(self.__manipulateDataFormula):
            self.__usedData = []
            for dataFile in data:
                self.__usedData.append( eval(self.__manipulateDataFormula) )  
        else:
            self.__usedData = [d[useFiles] for d in data]  
        
    def on_default_dir(self, event):
        dialog = wx.DirDialog (None, 
                               message = "Choose default directory",
                               defaultPath=DEFAULT_DIR, 
                               style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        returned = dialog.ShowModal() 
        if returned == wx.ID_OK:
            p = os.path.abspath(dialog.GetPath())
            # ensure double backslashes on windows
            if sys.platform.startswith('win'):
                p = p.replace("\\","\\"+"\\")
            s = os.path.split(dialog.GetPath()) 
            os.path.join(s[0], s[1])
            globals()["DEFAULT_DIR"] = p
            SET_GENERAL_PARAMETERS(defaultdir = '"'+p+'"')
        else:
            return
            
    def on_about(self, event):
        About().ShowModal()
    
    def on_browse_matrix(self, event):
        # create browsing dialog
        wildcard = "All files (*.*)|*.*|"+\
                   "data files (*.dat)|*.dat|"+\
                   "text files (*.txt)|*.txt"           
        dialog = wx.FileDialog(None, message="Browse files", 
                                     defaultDir=DEFAULT_DIR, 
                                     defaultFile="", 
                                     wildcard=wildcard,
                                     style=wx.OPEN)
        returned = dialog.ShowModal() 
        globals()["DEFAULT_DIR"] = dialog.GetDirectory()
        dialog.Destroy()
        if returned == wx.ID_OK:
            files = [os.path.normpath(str(p)) for p in dialog.GetPaths()]
        else:
            return
        # set matrixFile flag
        self.__matrixFile = True
        # update widget
        self.populate_files(files)
        # Set active
        self.__commentWid.Enable(True)
        self.__delimiterWid.Enable(True)
        self.__headerLinesWid.Enable(True)
        self.__footerLinesWid.Enable(True)
        self.__useColumnWid.Enable(False)
        self.__readColumnWiseWid.Enable(True)
        # set plot options enabled
        #self.__compareSelectedDataBut.Enable(not self.__matrixFile)
        #self.__plotSelectedDataBut.Enable(not self.__matrixFile)
            
    def on_browse_files(self, event):
        # create browsing dialog
        wildcard = "All files (*.*)|*.*|"+\
                   "Chi files (*.chi)|*.chi|"+\
                   "gr files (*.gr)|*.gr|"+\
                   "sq files (*.sq)|*.sq|"+\
                   "data files (*.dat)|*.dat|"+\
                   "text files (*.txt)|*.txt"           
        dialog = wx.FileDialog(None, message="Browse files", 
                                     defaultDir=DEFAULT_DIR, 
                                     defaultFile="", 
                                     wildcard=wildcard,
                                     style=wx.OPEN|wx.FD_MULTIPLE)
        returned = dialog.ShowModal() 
        globals()["DEFAULT_DIR"] = dialog.GetDirectory()
        dialog.Destroy()
        if returned == wx.ID_OK:
            files = [os.path.normpath(str(p)) for p in dialog.GetPaths()]
        else:
            return
        # set matrixFile flag
        self.__matrixFile = False
        # update widget
        self.populate_files(files)
        # Set active
        self.__commentWid.Enable(True)
        self.__delimiterWid.Enable(True)
        self.__headerLinesWid.Enable(True)
        self.__footerLinesWid.Enable(True)
        self.__useColumnWid.Enable(True)
        self.__readColumnWiseWid.Enable(False)
        # set plot options enabled
        #self.__compareSelectedDataBut.Enable(not self.__matrixFile)
        #self.__plotSelectedDataBut.Enable(not self.__matrixFile)
    
    def populate_files(self, files):
        # check files
        self.__files = [f for f in files if os.path.isfile(f) and os.access(f, os.R_OK)]
        # update widget
        self.__filesWid.Clear()
        # update files
        [self.__filesWid.Insert("%i --> "%idx+str(self.__files[idx]), idx) for idx in range(len(self.__files))]
        # enable buttons
        self.__LoadData.Enable(len(self.__files))
        self.__invertFilesWid.Enable(len(self.__files) and not self.__matrixFile)
        
    def on_files_selection(self, event):
        # get selection
        selected = sorted( self.__filesWid.GetSelections() )
        # enable buttons
        self.__discardFileWid.Enable(len(selected) and not self.__matrixFile)
        if not len(selected) or self.__matrixFile:
            self.__moveUpWid.Enable(False)
            self.__moveDownWid.Enable(False)
        else:
            self.__moveUpWid.Enable(selected[0]>0)
            self.__moveDownWid.Enable(selected[-1]<len(self.__files)-1)
                
    def on_quit(self, event):
        exit()
        
    def on_comment(self, event):
        self.__comment = str(event.GetEventObject().GetValue())

    def on_delimiter(self, event):
        self.__delimiter = str(event.GetEventObject().GetValue())
        
    def on_header_lines(self,event):
        try:
            val = event.GetEventObject().GetValue()
            val = int(val) 
        except:
            val = None            
        if val<0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__headerLines))   
        else:            
            self.__headerLines = val
    
    def on_footer_lines(self, event):
        try:
            val = event.GetEventObject().GetValue()
            val = int(val) 
        except:
            val = None            
        if val<0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__footerLines))   
        else:            
            self.__footerLines = val
            
    def on_use_column(self,event):
        try:
            val = event.GetEventObject().GetValue()
            val = int(val)  
        except:
            val = None           
        if val<0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__useColumn))      
        else:            
            self.__useColumn = val
    
    def on_read_column_wise(self, event):
        self.__readColumnWise = self.__readColumnWiseWid.GetValue()
        
    def on_scedasticity_window_size(self, event):
        try:
            val = event.GetEventObject().GetValue()
            val = int(val)  
        except:
            val = None           
        if val<=0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__scedasticityWindowSize))      
        elif val % 2 == 0:
            val -= 1
            event.GetEventObject().ChangeValue(str(val))  
            self.__scedasticityWindowSize = val  
            # reset calculations
            self.initialize_analysis_data()            
        else:            
            self.__scedasticityWindowSize = val
            # reset calculations
            self.initialize_analysis_data()

    def on_files_interval(self, event):
        try:
            val = event.GetEventObject().GetValue()
            val = int(val)  
        except:
            val = None           
        if val<=0:
            val = None
        if val is None:
            event.GetEventObject().ChangeValue(str(self.__filesInterval))      
        else:
            self.__filesInterval = val
            # reset calculations
            self.initialize_analysis_data()
            
    def on_move_down(self, event):
        selected = self.__filesWid.GetSelections()
        if not len(selected):
            return
        if selected[0] == 0:
            self.__moveUpWid.Enable(False)
        else:
            self.__moveUpWid.Enable(True)
        if selected[-1] == len(self.__files)-1:
            self.__moveDownWid.Enable(False)
            return
        # move selected
        newSelection = []
        for idx in reversed(selected):
            filePath = self.__files.pop(idx)
            #self.__filesWid.Delete(idx)
            self.__files.insert(idx+1, filePath)
            #self.__filesWid.Insert(filePath, idx+1)
            #self.__filesWid.SetSelection(idx+1, True)
            newSelection.append(idx+1)
        # repopulate files
        self.populate_files(self.__files)
        for idx in reversed(newSelection):
            self.__filesWid.SetSelection(idx)
        # set enables
        self.__moveDownWid.Enable(not  newSelection[-1] == len(self.__files)-1)
        self.__moveUpWid.Enable(not newSelection[0] == 0)
  
    def on_move_up(self, event):
        selected = self.__filesWid.GetSelections()   
        if not len(selected):
            return
        if selected[-1] == len(self.__files)-1:
            self.__moveDownWid.Enable(False)
        else:
            self.__moveDownWid.Enable(True)
        if selected[0] == 0:
            self.__moveUpWid.Enable(False)
            return
        # move selected
        newSelection = []
        for idx in selected:
            filePath = self.__files.pop(idx)
            #self.__filesWid.Delete(idx)
            self.__files.insert(idx-1, filePath)
            #self.__filesWid.Insert(filePath, idx-1)
            #self.__filesWid.SetSelection(idx-1, True)
            newSelection.append(idx-1)
        # repopulate files
        self.populate_files(self.__files)
        for idx in reversed(newSelection):
            self.__filesWid.SetSelection(idx)
        # set enables
        self.__moveDownWid.Enable(not  newSelection[-1] == len(self.__files)-1)
        self.__moveUpWid.Enable(not newSelection[0] == 0)
            
    def on_invert_order(self, event):
        # get selected files to select back
        selected = sorted(self.__filesWid.GetSelections())
        # clear all files
        self.__filesWid.Clear()
        self.__files = [item for item in reversed(self.__files)]
        [self.__filesWid.Insert(self.__files[idx], idx) for idx in range(len(self.__files))]
        # reselect files
        [self.__filesWid.SetSelection(len(self.__files)-1-idx, True) for idx in selected]
        
    def on_discard_down(self, event):    
        selected = sorted(self.__filesWid.GetSelections())
        if not len(selected):
            return
        # correct indexes
        selected = [selected[idx]-idx for idx in range(len(selected))]
        for idx in selected:
            self.__filesWid.SetSelection(idx, False)
            self.__filesWid.Delete(idx)
            self.__files.pop(idx)
     
    def on_load_data(self, event):
        if not len(self.__files):
            warnings.warn("must browse files first.")
            dlg = wx.MessageDialog(self, "must browse files first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        data    = []
        count   = 0
        self.__progressBar.SetValue(0) 
        self.__progressBar.SetRange(len(self.__files))
        vectLen = None
        unreadFiles = []
        # load single matrix file
        if self.__matrixFile:
            try:
                f = self.__files[0]
                d = np.genfromtxt(f, dtype = np.float32,
                                   comments    = self.__comment, 
                                   delimiter   = self.__delimiter, 
                                   skip_header = self.__headerLines,
                                   skip_footer = self.__footerLines)
                assert len(d.shape) == 2, "matrix should have N lines and M columns"
            except Exception as e:
                unreadFiles.append(f)
                warnings.warn("file %s can't be read. %s"%(f,e))
                dlg = wx.MessageDialog(self, "file %s can't be read. %s"%(f,e),
                                             "Reading error", wx.OK|wx.ICON_ERROR)
                result = dlg.ShowModal()
                dlg.Destroy()
            else:
                # cast vectors length
                if not self.__readColumnWise:
                    self.__allData = [d[idx,:] for idx in range(d.shape[0])]
                else:
                    self.__allData = [d[:,idx] for idx in range(d.shape[1])]
                
                # create files list    
                #self.__files = [f for f in files if os.path.isfile(f) and os.access(f, os.R_OK)]
                # update widget
                self.__filesWid.Clear()
                if self.__readColumnWise:
                    [self.__filesWid.Insert("%i --> "%idx+"matrix data loaded column wise", idx) for idx in range(len(self.__allData))]
                else: 
                    [self.__filesWid.Insert("%i --> "%idx+"matrix data loaded row wise", idx) for idx in range(len(self.__allData))]
                             
        # load vector files
        else:
            warnMsgs = []
            for f in self.__files:
                try:
                    d = np.genfromtxt(f, dtype    = np.float32,
                                      comments    = self.__comment, 
                                      delimiter   = self.__delimiter, 
                                      skip_header = self.__headerLines,
                                      skip_footer = self.__footerLines,
                                      usecols     = self.__useColumn)
                    assert len(d), "file must have data"
                except Exception as e:
                    unreadFiles.append(f)
                    message = "file %s can't be read. %s"%(f,e)
                    warnings.warn(message)
                    warnMsgs.append(message)     
                else:
                    if vectLen is None:
                        vectLen = len(d)
                    elif vectLen != len(d):
                        message = "file %s length is found to be different than the rest of files"%(f)
                        warnings.warn(message)
                        warnMsgs.append(message)
                    data.append(d)
                # update progress    
                count += 1
                self.__progressBar.SetValue(count)
            # cast vectors length
            self.__allData  = [d[:vectLen] for d in data]
            # warn when needed
            if len(warnMsgs):
                message = ""
                if len(warnMsgs)>3: 
                    warnMsgs=[warnMsgs[idx] for idx in range(3)]
                    message = "ONLY FIRST 3 WARNINGS ARE SHOWN HERE, PLEASE LOOK AT TERMINAL \n\n"
                for m in warnMsgs:
                    message += m + "\n"                
                dlg = wx.MessageDialog(self, message,
                      "No data found", wx.OK|wx.ICON_WARNING)
                result = dlg.ShowModal()
                dlg.Destroy()
        # warn unread files
        if len(unreadFiles):
            dlg = wx.MessageDialog(self, "The following files were skipped because an error is encountered upon reading.\n%s\n"%("\n".join(unreadFiles)),
                  "Files skipped", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
        # set used data
        self.__set_used_data()
        # reset calculations
        self.initialize_analysis_data()
        # reset data manipulation
        self.initialize_data_manipulation()
        # reset progress bar
        self.__progressBar.SetValue(len(self.__files))    
   
    def on_compare_selected_data(self, event):
        if not len(self.__allData):
            warnings.warn("must load data first.")
            dlg = wx.MessageDialog(self, "must load data first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        selected = sorted(self.__filesWid.GetSelections())
        if not len(selected):
            warnings.warn("must select data files first.")
            dlg = wx.MessageDialog(self, "must select data files first.",
                  "No selection found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        # plot data
        data   = [self.__usedData[idx] for idx in selected]
        labels = []
        for idx in selected:
            p, fn = os.path.split(self.__filesWid.GetString(idx))
            if len(fn):
                labels.append(fn)
            else:
                labels.append(p)
        plot = PlotFigure(parent=self, title="raw data",
                          plotTitle = "raw data",
                          mapOptions=False, compareOptions=True)
        # compare data  
        plot.compare_vectors(data, labels=labels)                  
        plot.Show()                 
    
    def on_plot_selected_data(self, event):
        if not len(self.__allData):
            warnings.warn("must load data first.")
            dlg = wx.MessageDialog(self, "must load data first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        selected = sorted(self.__filesWid.GetSelections())
        if len(selected) <= 1:
            warnings.warn("must select multiple data files.")
            dlg = wx.MessageDialog(self, "must select multiple data files.",
                  "No selection found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        # vertical stack data
        data = np.vstack([self.__usedData[idx] for idx in selected])
        # plot data
        plot = PlotFigure(parent=self, title="raw data",
                          plotTitle = "raw data",
                          mapOptions=True)
        plot.plot_image(data, extent=(0,100,0,100), axis='on')
        plot.Show()
        
    def on_plot_data(self, event):
        if not len(self.__allData):
            warnings.warn("must load data first.")
            dlg = wx.MessageDialog(self, "must load data first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if not len(self.__usedData):
            warnings.warn("Used data range returns no data.")
            dlg = wx.MessageDialog(self, "Used data range returns no data.",
                  "Wrong data range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        # vertical stack data
        data = np.vstack(self.__usedData)
        # plot data
        plot = PlotFigure(parent=self, title="raw data",
                          plotTitle = "raw data",
                          mapOptions=True)
        plot.plot_image(data, extent=(0,100,0,100), axis='on')
        plot.Show()
    
    def on_compute_correlation(self, event):
        if not len(self.__allData):
            warnings.warn("must load data first.")
            dlg = wx.MessageDialog(self, "must load data first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if not len(self.__usedData):
            warnings.warn("Used data range returns no data.")
            dlg = wx.MessageDialog(self, "Used data range returns no data.",
                  "Wrong data range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.__usedData) <= 1:
            warnings.warn("At least two data set must be loaded")
            dlg = wx.MessageDialog(self, "At least two data set must be loaded.",
                  "Not enough data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if self.__correlation is None:
            correlation = []
            self.__progressBar.SetValue(0)  
            self.__progressBar.SetRange(len(self.__usedData)-1)
            for idx in range(0,len(self.__usedData)-1, self.__filesInterval):
                y0 = self.__usedData[idx]
                y1 = self.__usedData[idx+1]
                # create correlation vector
                y0mean = np.mean(y0)
                y1mean = np.mean(y1)
                y0_mean = y0-y0mean
                y1_mean = y1-y1mean
                numerator = np.sum(y0_mean*y1_mean)
                denominator = np.sqrt(np.sum(y0_mean**2)*np.sum(y1_mean**2))
                correlation.append( numerator/denominator )
                # update bar
                self.__progressBar.SetValue(idx+1)
            self.__correlation = np.array(correlation)
        # reset progress bar
        self.__progressBar.SetValue(len(self.__usedData)-1)  
        # plot data
        plot = PlotFigure(parent=self, title="correlation", plotTitle="correlation interval %i"%self.__filesInterval)
        plot.plot_vector(self.__correlation)
        plot.Show()
    
    def __get_scedasticity_correlation(self, y0, y1, halfwindow):   
        # create correlation vector
        corr = np.nan*np.zeros(len(y0))
        # create positions vector
        positions = range(halfwindow, len(y0)-halfwindow, 1)
        # calculate correlations
        for idx in positions:
            dotproduct = np.dot(y0[idx-halfwindow:idx+halfwindow+1], y1[idx-halfwindow:idx+halfwindow+1])
            normy1 = norm(y0[idx-halfwindow:idx+halfwindow+1])
            normy2 = norm(y1[idx-halfwindow:idx+halfwindow+1])
            corr[idx] = dotproduct/(normy1*normy2)
        return corr
        
    def on_compute_scedasticity(self, event):
        if not len(self.__allData):
            warnings.warn("must load data first.")
            dlg = wx.MessageDialog(self, "must load data first.",
                  "No data found", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        if not len(self.__usedData):
            warnings.warn("Used data range returns no data.")
            dlg = wx.MessageDialog(self, "Used data range returns no data.",
                  "Wrong data range", wx.OK|wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        windowSize=float(self.__scedasticityWindowSize)
        assert windowSize<=len(self.__usedData[0]), "scedasticity size cannot be bigger than the data size"
        halfwindow = int(windowSize/2)
        if self.__scedasticity is None:
            correlation = []
            self.__progressBar.SetValue(0)  
            self.__progressBar.SetRange(len(self.__usedData)-self.__filesInterval)
            for idx in range(0, len(self.__usedData)-self.__filesInterval): 
                y0 = self.__usedData[idx]
                y1 = self.__usedData[idx+self.__filesInterval] 
                correlation.append(self.__get_scedasticity_correlation(y0,y1, halfwindow))
                # update bar
                self.__progressBar.SetValue(idx+1)
            # reset progress bar
            self.__progressBar.SetValue(len(self.__usedData)-self.__filesInterval)  
            self.__scedasticity = np.vstack(correlation)
        # vertical stack data
        data = np.array( self.__scedasticity )
        # normalize between 0 and 1
        data -= np.nanmin( data )
        data /= np.nanmax( data )
        # plot data
        plot = PlotFigure(parent=self, title="scedasticity", 
                          plotTitle="interval %i - window %i"%(self.__filesInterval, self.__scedasticityWindowSize),
                          mapOptions=True)
        plot.plot_image(data, extent=(0,100,0,100), axis='on', colormap="jet")
        plot.Show()

    def __update_read_files_parameters(self, comment, delimiter, headerLines, footerLines, useColumn):
        # create comment
        self.__commentWid.ChangeValue(str(comment))
        self.__comment = comment
        # create delimiter
        self.__delimiterWid.ChangeValue(str(delimiter))
        self.__delimiter = delimiter
        # create header lines
        self.__headerLinesWid.ChangeValue(str(headerLines))
        self.__headerLines = headerLines
        # create footer lines
        self.__footerLinesWid.ChangeValue(str(footerLines))
        self.__footerLines = footerLines
        # create use column
        self.__useColumnWid.ChangeValue(str(useColumn))
        self.__useColumn = useColumn     
        
    def on_chi_file_parameter(self, event):
        self.__update_read_files_parameters(comment="#", delimiter="", headerLines=4, footerLines=0, useColumn=1)
        
    def on_gr_file_parameter(self, event):
        self.__update_read_files_parameters(comment="#", delimiter="", headerLines=135, footerLines=0, useColumn=1)   
    
    def on_sq_file_parameter(self, event):
        self.__update_read_files_parameters(comment="#", delimiter="", headerLines=135, footerLines=0, useColumn=1)   
        
        
        
        
        



