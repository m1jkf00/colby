'''Visualization module. 
The Exhibit class provides the main interface for building panels, but this module also contains several support functions.
Some of these functions will be exclusively used in the backend for Exhibit, but others, such as concat_pdf, concat_ps, fixed2data, and gen_ts_tick_label_range, do have application on the user side as well.

Below is a listing of the function and class names. Assuming you imported this module with "from colby import cb", 
use help(cb.name), where name is a function or class name from the lists below, for more information.

Functions:
calc_ts_bar_width
center_cs_obs
center_ts_obs
concat_pdf
concat_ps
data2fixed
fixed2data
form_partition
format_month_irregular
gen_ts_tick_label_range
impose_ts_xrange
period_to_ts

Classes:
Exhibit
'''

#Linux package versions used in testing
#Python > 3.13.0
#matplotlib > 3.9.2
#pandas > 2.2.3
#PyPDF2 > 3.0.1

#Windows package versions used in testing
#Python > 3.12.6
#matplotlib > 3.9.2
#pandas > 2.2.3
#PyPDF2 > 3.0.1

import matplotlib, matplotlib.pyplot as plt, matplotlib.font_manager as fman, matplotlib.dates as mdates, matplotlib.ticker as ticker
import sys
import numbers
import pandas as pd
from datetime import timedelta
import copy
import re
import shutil
import PyPDF2 as Pdf

def data2fixed(coord, ax, axis = 0):
    '''Converts data coordinate (based on scale of the graph) to fixed axis coordinates (mostly lie in [-1.1, 1.1].
    matplotlib does provide built-in transform methods for making making these adjustments, but those methods are not available for all graphing functions.
   
    Inputs:
    coord: int or float, date, or date string following %Y-%m-%d format to be interpreted according to the scale of the graph
    ax: Axis object whose axis scales to use
    axis: Which axis from the ax object to use for conversion. 
          The default 0 corresponds to the x-axis and any other value (but preferably 1 by convention) maps to the y-axis.
    
    Output:
    data2fixed(): float to be interpreted in fixed-axis units
    '''

    if axis == 0:
        axis_lim = ax.get_xlim()
    else:
        axis_lim = ax.get_ylim()
    if not isinstance(coord, numbers.Number):
        if isinstance(coord, pd.Period):
            coord = coord.to_timestamp()
        coord = mdates.date2num(pd.Timestamp(coord))
    return((coord - axis_lim[0])/(axis_lim[1] - axis_lim[0]))


def fixed2data(coord, ax, axis = 0):
    '''Converts fixed axis coordinate (mostly lie in [-1.1, 1.1] to data coordinate (based on scale of the graph).
    matplotlib does provide built-in transform methods for making making these adjustments, but those methods are not available for all graphing functions.
   
    Inputs:
    coord: int or float to be interpreted in fixed-axis units
    ax: Axis object whose axis scales to use
    axis: Which axis from the ax object to use for conversion. 
          The default 0 corresponds to the x-axis and any other value (but preferably 1 by convention) maps to the y-axis.
    
    Output:
    fixed2data(): float to be interpreted according to scale of graph
    '''

    if axis == 0:
        axis_lim = ax.get_xlim()
    else:
        axis_lim = ax.get_ylim()
    return((coord * (axis_lim[1] - axis_lim[0])) + axis_lim[0])


def impose_ts_xrange(ser, x_range):
    '''Imposes x-axis's date range on time series to be plotted.

    Inputs:
    ser: pandas.Series whose index range should be adjusted.
    x_range: tuple or list of 2 x-coordinates specifying x-axis range
             Accepts coordinates in int, float, date, and date string (following %Y-%m-%d format) form

    Output:
    impose_ts_xrange(): pandas.Series subsetted to specified x_range
    '''
    
    if isinstance(x_range[0], numbers.Number):
        date_bounds = [pd.Timestamp(str(mdates.num2date(coord))[0:10], unit = "D") for coord in x_range]
    else:
        date_bounds = [pd.Timestamp(coord, unit = "D") for coord in x_range]
    new_series = copy.deepcopy(ser)
    return(new_series[date_bounds[0]:(date_bounds[1] + timedelta(days = 1))])


def period_to_ts(ser):
    '''Converts pandas.Series' PeriodIndex (default behavior from pyfame) to a DatetimeIndex (expected format for plotting functions). 
    Returns original series with no changes if it already has a DatetimeIndex.

    Input:
    ser: pandas.Series with some type of date index

    Output:
    period_to_ts(): pandas.Series with a DatetimeIndex
    '''

    output = copy.deepcopy(ser)
    if isinstance(output.index, pd.PeriodIndex):
        output.index = output.index.to_timestamp(freq = output.index.freq)
    return(output) 


def calc_ts_bar_width(freq, number_stacks = 1, width_coef = 1):
    '''Determines appropriate width of barstacks given frequency of the time series and the number of stacks to be plotted side-by-side.

    Inputs:
    freq: str indicating frequency of the series. Expected to be an element of this list: ["<Minute>", "<Hour>", "<Day>", "<BusinessDay>", "Week: weekday=6>", "<MonthEnd>", "<QuarterEnd: startingMonth=12>", "<2 * QuarterEnds: startingMonth=12>", "<YearEnd: month=12>"]
    number_stacks: int indicating numbers of stacks to be plotted side_by_side
    width_coef: int or float to be applied as a coefficient to automatically determined width of bars
                Defaults to 1.

    Output:
    calc_ts_bar_width(): float indicating width of bars to be plotted
    '''

    freq_dict = {"<Minute>": 1/(60*24), "<Hour>": 1/24, 
                 "<Day>": 1, "<BusinessDay>": 1,
                 "<MonthEnd>": 30, "<6 * MonthEnds>": 180, "<QuarterEnd: startingMonth=12>": 91, 
                 "<2 * QuarterEnds: startingMonth=12>": 182, "<YearEnd: month=12>": 365}
    for i in [5, 10, 15, 20, 30]:
        freq_dict[f'<{str(i)} Minutes>'] = i/(60 * 24)
    for i in [2, 3, 4, 6, 8, 12]:
        freq_dict[f'<{str(i)} Hours>'] = i/24
    for x in range(0,7):
        freq_dict["<Week: weekday=" + str(x) + ">"] = 7
    return(width_coef * freq_dict[freq]/number_stacks)


def center_ts_obs(ser, ser_freq = None, number_stacks = 1, curr_stack = 1, width_coef = 1, pos_adj = 0):
    '''Centers time series observations inside of the time period each observation takes place in. 
    For instance, a 2017 annual value would be shifted to 2017-07-01 under default behavior. 
    The adjustment is altered in the case of barcharts with multiple stacks in order to fit all stacks in the appropriate time period.
    
    Inputs:
    ser: pandas.Series whose indexes should be adjusted. The series' frequency is expected to be in ["<Minute>", "<Hour>", "<Day>", "<BusinessDay>", "Week: weekday=6>", "<MonthEnd>", "<QuarterEnd: startingMonth=12>", "<2 * QuarterEnds: startingMonth=12>", "<YearEnd: month=12>"]
         If not, the Series is returned with no changes.
    ser_freq: str indicating frequency of ser
              Should be an element of ["min", "h", "d", "b", "w", "m", "q", "a", "y"] (not case-sensitive), which maps to ["minute", "hour", "daily", "business", "week", "month", "quarter", "annual", "annual"].
              You may supply "5", "10", "15", "20", or "30" as a prefix to "min" (ie "5min"); "2", "3", "4", "6", "8", or "12" as a prefix to "h"; "6" as a prefix for "m"; or "2" as a prefix to "q" to apply a skip parameter.
              Defaults to None, in which case this function tries to automatically determine the frequency based on ser's attributes.
              This argument is only useful when ser does not have a freq attribute (occassionally happens when ser is subsetted down to 1 observation).
    number_stacks: int indicating how many stacks of bars are to be expected
                   The default of 1 provides appropriate behavior for line graphs, scatterplots, and barcharts with just 1 stack.
    curr_stack: int indicating which stack this series belongs in. This should lie between 1 and number_stacks
                The default of 1 provides appropriate behavior for line graphs, scatterplots, and barcharts with just 1 stack so long as number_stack = 1.
    width_coef: int or float to be applied as a coefficient to automatically determined width of bars (should match width_coef argument to calc_ts_bar_width)
                Defaults to 1.
    pos_adj: int or float specifying adjustment to be made to bars' locations (value is interpreted in units of days). Intended to help correct instances where bar edges overlap
             Defaults to 0 (assumes no error)
    
    Output:
    center_ts_obs(): pandas.Series with same values as ser but with adjusted indexes
    '''

    new_series = copy.deepcopy(ser)
    if ser_freq is None:
        ser_freq = str(new_series.index.freq)
    else:
        shorthand_freq_dict = {"min": "<Minute>", "h": "<Hour>", "d": "<Day>", "b": "<BusinessDay>",
                               "w": "Week: weekday=6>", "m": "<MonthEnd>", "6m": "<6 * MonthEnds>", "q": "<QuarterEnd: startingMonth=12>", 
                               "2q": "<2 * QuarterEnds: startingMonth=12>", "a": "<YearEnd: month=12>", "y": "<YearEnd: month=12>"}
        for i in [5, 10, 15, 20, 30]:
            shorthand_freq_dict[f'{str(i)}min'] = f'<{str(i)} Minutes>'
        for i in [2, 3, 4, 6, 8, 12]:
            shorthand_freq_dict[f'{str(i)}h'] = f'<{str(i)} Hours>'
        for dict_value in list(shorthand_freq_dict.values()):
            shorthand_freq_dict[dict_value.lower()] = dict_value
            
        ser_freq = shorthand_freq_dict[ser_freq.lower()]
    freq_dict = {"<Minute>": 1/(60*24), "<Hour>": 1/24,
                 "<Day>": 1, "<BusinessDay>": 1,
                 "<MonthEnd>": 30, "<6 * MonthEnd>": 180, "<QuarterEnd: startingMonth=12>": 91, 
                 "<2 * QuarterEnds: startingMonth=12>": 182, "<YearEnd: month=12>": 365}
    for i in [5, 10, 15, 20, 30]:
        freq_dict[f'<{str(i)} Minutes>'] = i/(60 * 24)
    for i in [2, 3, 4, 6, 8, 12]:
        freq_dict[f'<{str(i)} Hours>'] = i/24
    for x in range(0,7):
        freq_dict["<Week: weekday=" + str(x) + ">"] = 7
    
    freq_check = (ser_freq == "<2 * QuarterEnds: startingMonth=12>" and new_series.index[0].month not in [6,12])
    period_length = freq_dict[ser_freq]
    bar_width = width_coef * period_length/number_stacks
    
    if freq_check: #special treatment for when semi-annual series is already centered
        new_series.index = (new_series.index + timedelta(days = period_length/2)) - timedelta(days = ((.5 - width_coef/2) * period_length) + ((curr_stack - .5) * bar_width) - pos_adj)
    elif ser_freq in freq_dict.keys():
        new_series.index = new_series.index - timedelta(days = ((.5 - width_coef/2) * period_length) + ((curr_stack - .5) * bar_width) - pos_adj)
    return(new_series)


def center_cs_obs(ser, number_stacks = 1, curr_stack = 1, width_coef = .8, pos_adj = 0):
    '''Centers cross-section observations for purposes of graphing.
    Adjustment accounts for how many barstacks appear in the chart.
    
    Inputs:
    ser: iterable (ie list) holding values to be plotted
    number_stacks: int indicating how many stacks of bars are to be expected
                   The default of 1 provides appropriate behavior for line graphs, scatterplots, and barcharts with just 1 stack.
    curr_stack: int indicating which stack this series belongs in. This should lie between 1 and number_stacks
                The default of 1 provides appropriate behavior for line graphs, scatterplots, and barcharts with just 1 stack so long as number_stack = 1.
    width_coef: int or float to be treated as coefficient on automatically determined width of bars
                Defaults to .8
    pos_adj: int or float specifying adjustment to be made to bars' locations. Intended to help correct instances where bar edges overlap
             Defaults to 0 (assumes no error)
    
    Output:
    center_cs_obs(): list containing floats specifying locations of bars
    '''

    return([x + width_coef*((curr_stack - .5)/number_stacks - .5) + pos_adj for x in range(len(ser))])

    
def gen_ts_tick_label_range(start, end, freq, skip = ""):
    '''Generates a list of datetime objects that may be passed to plotting functions for specifying x-axis ticks and labels.

    Inputs:
    start: date object or date str in %Y-%m-%d format specifying start of date range
    end: date object or date str in %Y-%m-%d format specifying end of date range
    freq: str specifying frequency of range to be returned. This list has the most common choices: ["S", "MIN", "H", "D", "B", "W", "M", "Q", "A", "Y"]
    skip: int or integer string specifying how many periods to skip between elements of the date range
          The default of "" (equivalent to 1) does not skip any periods.

    Output:
    gen_ts_tick_label_range(): list of datetime objects
    '''
    
    freq = freq.upper()
    if isinstance(start, pd.Period):
        start = start.to_timestamp()
    if isinstance(end, pd.Period):
        end = end.to_timestamp()
    
    freq_dict = {freq_option: freq_option for freq_option in ["S", "MIN", "H", "D", "B", "W", "M", "Q", "A", "Y"]}
    freq_dict["A"] = "Y"
    for intraday_freq in ["S", "MIN", "H"]:
        freq_dict[intraday_freq] = intraday_freq.lower()
    
    return(list(pd.date_range(start, end, freq = f'{str(skip)}{freq_dict[freq]}{"S" * (freq_dict[freq] not in ["S", "MIN", "H", "D", "B", "W"])}')))


def format_month_irregular(date_obj):
    '''Returns a date's irregular month abbreviation (3-letters plus a period, with exceptions being May, June, July, and Sept.).

    Inputs:
    date_obj: date or date str object
          date, datetime, pd.Timestamp, and pd.Period objects are all supported.
          If passing a date str, it must be compatible with pd.Timestamp().

    Output:
    format_month_irregular(): str giving the irregular month abbreviation of date_obj
    '''
    if isinstance(date_obj, str):
        date_obj = pd.Timestamp(date_obj)
    month_str = date_obj.strftime("%b.").replace("May.", "May").replace("Jun.", "June").replace("Jul.", "July").replace("Sep.", "Sept.")
    return(month_str)


def form_partition(h_start, h_end, v_start, v_end, nrow, ncol, 
                   relative_row_sizes = None, relative_col_sizes = None):
    '''Given an [h_start, h_end] x [v_start, v_end] grid, splits the grid into nrow rows and ncol columns with desired relative
       dimensions and returns the minimum coordinate associated with each of them.
       Intended to help position elements in a table panel.

    Input:
    h_start: numeric between 0 and 1 specifying x-coordinate of grid's left edge
    h_end: numeric between 0 and 1 specifying x-coordinate of grid's right edge
    v_start: numeric between 0 and 1 specifying y-coordinate of grid's bottom edge
    v_end: numeric between 0 and 1 specifying y-coordinate of grid's top edge
    nrow: int indicating how many rows to split the grid into
    ncol: int indicating how many columns to split the grid into
    relative_row_sizes: iterable of numeric objects with length nrow giving relative height of each row (top row should come first)
                        Defaults to [1] * nrow (all rows have the same height)
    relative column_sizes: iterable of numeric objects with length ncol giving relative width of each column (left-most column should come first)
                           Defaults to [1] * ncol (all columns have the same width)

    Output:
    form_partition(): dictionary with keys "rows" and "cols"
                      form_partition()["rows"]: list of floats giving v_end and the bottom-most y-coordinate associated with each row (starting with the top row)
                      form_partition()["cols"]: list of floats giving the left-most x-coordinate associated with each column (starting with the left-most column) and h_end
    '''

    h_length = h_end - h_start
    v_length = v_end - v_start

    if relative_row_sizes is None:
        relative_row_sizes = [1] * nrow
    if relative_col_sizes is None:
        relative_col_sizes = [1] * ncol

    total_row_size = sum(relative_row_sizes)
    total_col_size = sum(relative_col_sizes)

    partition_dict = {"rows": [v_end - (v_length * sum(relative_row_sizes[:ind])/total_row_size) for ind in range(nrow)] + [v_start],
                      "cols": [h_start + (h_length * sum(relative_col_sizes[:ind])/total_col_size) for ind in range(ncol)] + [h_end]}

    return(partition_dict)


def concat_ps(ps_list, output_name):
    '''Concatenates multiple .ps files into one.
    os.system("ps2pdf " + ps_name) can then be used to convert the fused .ps file into a pdf.
    Note that .ps files do not properly apply hatching and alpha settings for barcharts and shaded regions. Use another file format in these instances.

    Inputs:
    ps_list: list of str specifying file name or file path to input .ps files
    output_name: str specifying file name or file path of combined .ps file to be created

    Output:
    concat_ps(): None, but creates specified output file
    '''

    with open(output_name, "wb") as fout:
        for fname in ps_list:
            with open(fname, "rb") as fin:
                shutil.copyfileobj(fin, fout)
    return(None)


def concat_pdf(pdf_list, output_name):
    '''Concatenates multiple .pdf files into one.

    Inputs:
    pdf_list: list of str specifying file name or file path to input .pdf files
    output_name: str specifying file name or file path of combined .pdf file to be created

    Output:
    concat_ps(): None, but creates specified output file
    '''

    pdf_writer = Pdf.PdfMerger()
    for fin in pdf_list:
        pdf_writer.append(fin)
    pdf_writer.write(output_name)
    pdf_writer.close()
    return(None)


class Exhibit():
    '''Support class for making pages of charts and tables. Each Exhibit instance corresponds to one pdf/ps page.
    In the following, "panel" is used as a generic term for charts and tables.

    Inputs:
        layout: tuple or list with 2 ints specifying, in order, how many rows and columns the Exhibit's underlying grid should be broken into.
        normal_font: str specifying path to .otf/.ttf file for desired "normal" font
        bold_font: str specifying path to .otf/.ttf file for desired bold font
        italic_font: str specifying path to .otf/.ttf file for desired italic font
        bold_italic_font:str specifying path to .otf/.ttf file for desired bold-italic font
        orientation: str specifying orientation (portrait vs landscape) for the exhibit.
                     Defaults to "portrait". All other values provided for this argument (but preferably "landscape" by convention) are mapped to "landscape".
        fig_dim: 2-tuple of floats specifying horizontal and vertical lengths of the exhibit in inches
                 If not specified, defaults to (8.5, 11) when orientation == "portrait" and (11, 8.5) otherwise.
        margins: tuple or list with 4 ints or floats specifying the left, bottom, right, and top margins of the exhibit's graphing space in inches.
                 Defaults to (1, 1, 1, 1.4)
        h_space: int or float specifying top and bottom margins for panels in inches.
                 Defaults to .3.
        w_space: int or float specifying left and right margins for panels in inches.
                 Defaults to .25.
        latex_preamble: str specifying session setting for matplotlib's LaTeX interface
                        Defaults to None, in which case LaTeX is not utilized at all.
                        matplotlib's standard text capabilities will be sufficient for most use-cases, but the use of sub- or superscripts or need to 
                        change font styles within a single text object may warrant the LaTeX option. 
                        Note that methods' font_style arguments are ignored when use_tex == True, so font styles need to be dictated in-text with LaTeX 
                        control sequences (ie "\\textbf{...}" for bold font). Be mindful that "\" is an escape character normally, so you will typically use them in pairs.
                        Using this argument does lengthen compilation, so users are encouraged to keep this False unless they really need LaTeX.

    Attributes:
    orientation: "portrait" or "landscape", determined by orientation argument to Exhibit()
    fig_dim: tuple specifying dimensions of figure in inches
             Set to (8.5, 11) for portrait orientation and (11, 8.5) for landscape unless specified as an argument
    fig: matplotlib.Figure to be populated with panels and converted into file form (mostly .ps)
         Use Exhibit.fig.show() to observe current state of the page and panels you've made.
         This show() method does fix the fig's features though, so you will need to re-initialize it afterwards to continue making changes.
    grid: matplotlib.GridSpec with mesh determined by layout argument to Exhibit()
    font_dict: dict providing paths to Helvetica font files
    panel_dict: dict for storing figure's chart objects as values. Initialized as an empty dict, but key-value pairs are added with each Exhibit.add_panel_ts, Exhibit.add_panel_nonts, Exhibit.add_panel_sec_yaxis, Exhibit.add_panel_sec_xaxis, or Exhibit.add_panel_table call

    Methods (use help function for more information):
    __init__ (docstring printed above)
    add_exhibit_title
    add_exhibit_captions
    add_exhibit_text
    save_exhibit
    add_panel_ts
    add_panel_nonts
    add_panel_sec_yaxis
    add_panel_sec_xaxis
    add_panel_table
    add_panel_title
    add_panel_captions
    add_panel_footnotes
    add_panel_text
    plot_panel_ts_line
    plot_panel_ts_scatter
    plot_panel_ts_barstack
    plot_panel_cs_line
    plot_panel_cs_scatter
    plot_panel_cs_barstack
    plot_panel_cs_pie
    plot_panel_num_line
    plot_panel_num_scatter
    plot_panel_num_barstack
    add_panel_keylines
    add_panel_keydots
    add_panel_keyboxes
    add_panel_hline
    add_panel_vline
    add_panel_shading
    add_panel_arrow
    format_panel_numaxis
    format_panel_ts_xaxis
    format_panel_cs_cataxis
    '''
    
    def __init__(self, layout, normal_font, bold_font, italic_font, bold_italic_font, orientation = "portrait", fig_dim = None, margins = (1, 1, 1, 1.4), h_space = .3, w_space = .25, latex_preamble = None, **kwargs):
        
        plt.style.use('classic')
        

        self.font_dict = {"normal": fman.FontProperties(fname = normal_font), 
                          "bold": fman.FontProperties(fname = bold_font),
                          "italic": fman.FontProperties(fname = italic_font),
                          "bold-italic": fman.FontProperties(fname = bold_italic_font)}
        
        if latex_preamble is not None:
            plt.rcParams.update({"text.usetex": True,
                                 "text.latex.preamble": latex_preamble})

        plt.rcParams['figure.facecolor'] = "w"

        if fig_dim is None:
            if orientation == "portrait":
                self.orientation = "portrait"
                self.fig_dim = (8.5, 11)
            else:
                self.orientation = "landscape"
                self.fig_dim = (11, 8.5)
        else:
            self.fig_dim = fig_dim
            # Set orientation parameter based on which dimension is larger.
            self.orientation = f'{"portrait" * (max(fig_dim) == fig_dim[1])}{"landscape" * (max(fig_dim) != fig_dim[1])}'
        
        self.fig = plt.figure(figsize = self.fig_dim)
        self.fig.subplots_adjust(left = margins[0]/self.fig_dim[0], bottom = margins[1]/self.fig_dim[1], 
                                 right = (self.fig_dim[0] - margins[2])/self.fig_dim[0], top = (self.fig_dim[1] - margins[3])/self.fig_dim[1], 
                                 hspace = h_space, wspace = w_space)

        self.grid = self.fig.add_gridspec(layout[0], layout[1])
        
        self.panel_dict = dict()


    def add_exhibit_title(self, text_str, dist_from_top = .8, font_style = "bold", font_size = 14):
        '''Prints exhibit title to top center of the page.
        
        Inputs:
        text_str: str specifying title to print.
        dist_from_top: int or float specifying how far, in inches, the title should be from the top of the page.
                       Defaults to .8.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "bold".
        font_size: int specifying fontsize for title.
                   Defaults to 18.
        
        Output:
        add_exhibit_title(): None, but prints a title to self.fig in-place
        '''
    
        self.fig.text(.5, (self.fig_dim[1] - dist_from_top)/self.fig_dim[1], text_str, fontproperties = self.font_dict[font_style], fontsize = font_size, ha = "center", va = "center")
        return(None)


    def add_exhibit_captions(self, left_caption = None, right_caption = None, dist_from_top = .6, dist_from_side = .8, font_style = "normal", font_size = 10):
        '''Prints exhibit captions to top-left and -right of the page.
        
        Inputs:
        left_caption: str specifying text to print as left caption
                      Defaults to None, in which case nothing is printed.
        right_caption: str specifying text to print as right caption
                       Defaults to None, in which case nothing is printed.
        dist_from_top: int or float specifying how far, in inches, the captions should be from the top of the page.
                       Defaults to .6.
        dist_from_side: int or float specifying how far, in inches, the captions should be from the left and right sides of the page.
                       Defaults to .8.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "normal".
        font_size: int specifying fontsize for captions.
                   Defaults to 10.
        
        Output:
        add_exhibit_captions(): None, but prints caption(s) to self.fig in-place
        '''

        y_coord = (self.fig_dim[1] - dist_from_top)/self.fig_dim[1]
        if left_caption is not None:
            self.fig.text(dist_from_side/self.fig_dim[0], y_coord, left_caption, fontproperties = self.font_dict[font_style], fontsize = font_size, ha = "left")
        if right_caption is not None:
            self.fig.text((self.fig_dim[0] - dist_from_side)/self.fig_dim[0], y_coord, right_caption, fontproperties = self.font_dict[font_style], fontsize = font_size, ha = "right")
        return(None)


    def add_exhibit_text(self, x_pos, y_pos, text_str, font_style = "normal", font_size = 10, horizontal_align = "left", vertical_align = "bottom", rotation = 0):
        '''Prints arbitrary text object to figure.
        
        Inputs:
        x_pos: float specifying text's horizontal position. Should be a value in [0, 1].
        y_pos: float specifying text's vertical position. Should be a value in [0, 1].
        text_str: str specifying text to be printed to the exhibit
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "normal".
        font_size: int specifying fontsize for text.
                   Defaults to 10.
        horizontal_align: str specifying horizontal alignment. Can be "left", "center", or "right".
                          Defaults to "left"
        vertical_align: str specifying vertical alignment. Can be "bottom", "center", or "top".
                        Defaults to "bottom"
        rotation: float or int specifying the rotation (in degrees) to be applied to the text element
                  Defaults to 0.
        
        Output:
        add_exhibit_text(): None, but prints text to self.fig in-place
        '''

        self.fig.text(x_pos, y_pos, text_str, fontproperties = self.font_dict[font_style], fontsize = font_size, ha = horizontal_align, va = vertical_align, rotation = rotation)
        return(None)


    def save_exhibit(self, filepath, dpi = None, bbox = None):
        '''Saves exhibit to file. File formats supported include pdf, ps, eps, png, and jpeg.
        Note that .ps files do not properly apply hatching and alpha settings for barcharts and shaded regions.  Use another file format in these instances.
        
        Inputs:
        filepath: str specifying file to save exhibit to
        dpi: float specifying resolution in dots per inch
             Defaults to matplotlib.rcParams["savefig.dpi"]
        bbox: str or Bbox object specifying bounds of exhibit to be saved
              Defaults to matplotlib.rcParams["savefig.bbox"]. 
              Most common non-default is "tight".
        
        Output:
        save_exhibit(): None, but generates desired file
        '''

        self.fig.savefig(filepath, orientation = self.orientation, dpi = dpi, bbox_inches = bbox)
        return(None)


    def add_panel_ts(self, panel_alias, x_range, h_start, v_start, h_end = None, v_end = None, axis_width = 1.3):
        '''Adds time-series chart panel to exhibit (specifically self.panel_dict) at desired location with specified x-axis range.
        
        Inputs:
        panel_alias: preferably a str to act as the dictionary key mapping to the created axis object in self.panel_dict
                     That said, any object type that can act as a dictionary key is acceptable.
        x_range: tuple or list of str or date objects specifying desired bounds of x-axis
        h_start: int indicating the row of the exhibit's grid where this chart should begin
        v_start: int indicating the column of the exhibit's grid where this chart should begin
        h_end: int indicating the row of the exhibit's grid where this chart should end - should be larger than h_start
               Defaults to (h_start + 1) - chart occupies the row indicated by h_start coordinate only
        v_end: int indicating vertical grid coordinate where this chart should end - should be larger than v_start
               Defaults to (v_start + 1) - chart occupies the column indicated by v_start coordinate only
               Note that h_end and v_end must be at least (h_start + 2) and (v_start + 2) to make an appreciable difference since Python omits right endpoints from ranges.
        axis_width: int or float specifying width of the chart's axes in points
                    Defaults to 1.3
        
        Output:
        add_panel_ts(): None, but adds axis object to self.panel_dict as a value with key panel_alias
        '''

        assert panel_alias not in self.panel_dict.keys(), "You have already declared a different panel with that name/alias. Please use a different name."

        plt.rcParams['axes.spines.top'] = False
        
        if h_end is None:
            h_end = h_start + 1
        if v_end is None:
            v_end = v_start + 1
        self.panel_dict[panel_alias] = self.fig.add_subplot(self.grid[h_start:h_end, v_start:v_end])
        
        self.panel_dict[panel_alias].tick_params(axis = 'x', which = 'both', bottom = True, top = False, 
                                                 labelbottom = False, labeltop = False)
        self.panel_dict[panel_alias].tick_params(axis = 'y', which = 'both', labelright = False, labelleft = False)
        if isinstance(x_range[0], pd.Period):
            x_range = [x.to_timestamp() for x in x_range]
        self.panel_dict[panel_alias].set_xlim([mdates.date2num(pd.Timestamp(x)) for x in x_range])
        
        self.panel_dict[panel_alias].spines["top"].set_visible(False)
        for side in ['left', 'bottom', 'right']:
            self.panel_dict[panel_alias].spines[side].set_linewidth(axis_width)
        
        return(None)


    def add_panel_nonts(self, panel_alias, h_start, v_start, h_end = None, v_end = None, invis_axis_list = ("top",), axis_width = 1.3):
        '''Adds non-timeseries chart panel to exhibit (specifically self.panel_dict) at desired location. 
        
        Inputs:
        panel_alias: preferably a str to act as the dictionary key mapping to the created axis object in self.panel_dict
                     That said, any object type that can act as a dictionary key is acceptable.
        h_start: int indicating the row of the exhibit's grid where this chart should begin
        v_start: int indicating the column of the exhibit's grid where this chart should begin
        h_end: int indicating the row of the exhibit's grid where this chart should end - should be larger than h_start
               Defaults to (h_start + 1) - chart occupies the row indicated by h_start coordinate only
        v_end: int indicating vertical grid coordinate where this chart should end - should be larger than v_start
               Defaults to (v_start + 1) - chart occupies the column indicated by v_start coordinate only
               Note that h_end and v_end must be at least (h_start + 2) and (v_start + 2) to make an appreciable difference since Python omits right endpoints from ranges.
        invis_axis_list: list of str specifying which axes to render invisible
                         Defaults to ["top"]. "left", "bottom", and "right" are the other acceptable elements.
                         To keep all axes visible, set this argument equal to an empty list
        axis_width: int or float specifying width of the chart's axes in points
                    Defaults to 1.3
        
        Output:
        add_panel_nonts(): None, but adds an axis object to self.panel_dict as a value with key panel_alias
        '''

        assert panel_alias not in self.panel_dict.keys(), "You have already declared a different panel with that name/alias. Please use a different name."
        
        if h_end is None:
            h_end = h_start + 1
        if v_end is None:
            v_end = v_start + 1
        self.panel_dict[panel_alias] = self.fig.add_subplot(self.grid[h_start:h_end, v_start:v_end])
        
        self.panel_dict[panel_alias].tick_params(axis = 'x', which = 'both', bottom = ("bottom" not in invis_axis_list), top = ("top" not in invis_axis_list),
                                                 labelbottom = False, labeltop = False)
        self.panel_dict[panel_alias].tick_params(axis = 'y', which = 'both', right = ("right" not in invis_axis_list), left = ("left" not in invis_axis_list), 
                                                 labelright = False, labelleft = False)
        
        for side in ['left', 'bottom', 'right', 'top']:
            self.panel_dict[panel_alias].spines[side].set_linewidth(axis_width)
            self.panel_dict[panel_alias].spines[side].set_visible((side not in invis_axis_list))
            
        return(None)


    def add_panel_sec_yaxis(self, original_panel_alias, sec_alias):
        '''Adds second y-axis scale (typically for a separate left axis, though fringe cases do exist) to an existing panel in the figure. 
        This second y-axis object is a new chart object in panel_dict even though it occupies the same space as the original panel.
        Users should be aware that this new chart object is layered on top of the original panel, so any elements in the new object will rest on top of (cover) the original panel's elements.
        
        Inputs:
        original_panel_alias: the panel alias for the chart to receive a second y-axis scale
        sec_alias: preferably a str to act as the dictionary key mapping to the second y-axis object in self.panel_dict
                   That said, any object type that can act as a dictionary key is acceptable.
        
        Output:
        add_panel_sec_yaxis(): None, but adds second y-axis object to self.panel_dict as a value with key sec_alias
        '''

        assert sec_alias not in self.panel_dict.keys(), "You have already declared a different panel with that name/alias. Please use a different name."

        self.panel_dict[sec_alias] = self.panel_dict[original_panel_alias].twinx()
        self.panel_dict[sec_alias].tick_params(axis = 'x', which = 'both', bottom = False, top = False, 
                                                  labelbottom = False, labeltop = False)
        self.panel_dict[sec_alias].tick_params(axis = 'y', which = 'both', labelright = False, labelleft = False)
        return(None)


    def add_panel_sec_xaxis(self, original_panel_alias, sec_alias):
        '''Adds second x-axis scale (typically for a separate top axis, though fringe cases may exist) to an existing panel in the figure. 
        This second x-axis object is a new chart object in panel_dict even though it occupies the same space as the original panel.
        This method should only ever be used in the context of a horizontal cross-section chart, and even in that circumstance this method is not recommended.
        Users should be aware that this new chart object is layered on top of the original panel, so any elements in the new object will rest on top of (cover) the original panel's elements.
        
        Inputs:
        original_panel_alias: the panel alias for the chart to receive a second x-axis scale
        sec_alias: preferably a str to act as the dictionary key mapping to the second x-axis object in self.panel_dict
                   That said, any object type that can act as a dictionary key is acceptable.
        
        Output:
        add_panel_sec_xaxis(): None, but adds second x-axis object to self.panel_dict as a value with key sec_alias
        '''

        assert sec_alias not in self.panel_dict.keys(), "You have already declared a different panel with that name/alias. Please use a different name."

        self.panel_dict[sec_alias] = self.panel_dict[original_panel_alias].twiny()
        self.panel_dict[sec_alias].tick_params(axis = 'y', which = 'both', left = False, right = False, 
                                                 labelleft = False, labelright = False)
        self.panel_dict[sec_alias].tick_params(axis = 'x', which = 'both', labelbottom = False, labeltop = False)
        return(None)


    def add_panel_table(self, panel_alias, h_start, v_start, h_end = None, v_end = None):
        '''Adds table panel ([0,1] x [0,1] grid) to exhibit (specifically self.panel_dict) at desired location. 
        Tables should be constructed using the add_panel_text(), add_panel_hline(), and add_panel_vline() methods.
        Shading may be added with the add_panel_shading() method.
        This module's form_partition() function should prove valuable for determining element locations, and
        loops are heavily encouraged for actually placing elements on the grid space.
        
        Inputs:
        panel_alias: preferably a str to act as the dictionary key mapping to the created axis object in self.panel_dict
                     That said, any object type that can act as a dictionary key is acceptable.
        h_start: int indicating the row of the exhibit's grid where this table should begin
        v_start: int indicating the column of the exhibit's grid where this table should begin
        h_end: int indicating the row of the exhibit's grid where this table should end - should be larger than h_start
               Defaults to (h_start + 1) - table occupies the row indicated by h_start coordinate only
        v_end: int indicating vertical grid coordinate where this table should end - should be larger than v_start
               Defaults to (v_start + 1) - table occupies the column indicated by v_start coordinate only
               Note that h_end and v_end must be at least (h_start + 2) and (v_start + 2) to make an appreciable difference since Python omits right endpoints from ranges.
        
        Output:
        add_panel_table(): None, but adds [0,1] x [0,1] table grid object to self.panel_dict as a value with key panel_alias
        '''

        assert panel_alias not in self.panel_dict.keys(), "You have already declared a different panel with that name/alias. Please use a different name."
        
        if h_end is None:
            h_end = h_start + 1
        if v_end is None:
            v_end = v_start + 1
        self.panel_dict[panel_alias] = self.fig.add_subplot(self.grid[h_start:h_end, v_start:v_end])
        
        self.panel_dict[panel_alias].tick_params(axis = 'x', which = 'both', bottom = False, top = False, 
                                                 labelbottom = False, labeltop = False)
        self.panel_dict[panel_alias].tick_params(axis = 'y', which = 'both', left = False, right = False,
                                                 labelright = False, labelleft = False)
        self.panel_dict[panel_alias].set_xlim([0,1])
        self.panel_dict[panel_alias].set_ylim([0,1])
        
        for side in ['left', 'bottom', 'right', 'top']:
            self.panel_dict[panel_alias].spines[side].set_visible(False)
        
        return(None)


    def add_panel_title(self, panel_alias, text_str, x_pos = 0, y_pos = 1.08, font_size = 12, font_style = "bold", color = "black"):
        '''Prints title to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add a title to.
        text_str: str specifying title text.
        x_pos: float specifying x-position (in fixed-axis units) for title.
               Defaults to 0. Should be a small decimal otherwise.
        y_pos: float specifying y-position (in fixed-axis units) for title.
               Defaults to 1.08. Should be slightly higher than 1.
        font_size: int specifying fontsize for title.
                   Defaults to 12.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "bold".
        color: str specifying color of font.
               Defaults to "black".
        
        Output:
        add_panel_title(): None, but prints title to specified panel in-place
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_ax.text(x_pos, y_pos, text_str, transform = curr_ax.transAxes, 
                     fontproperties = self.font_dict[font_style], fontsize = font_size, color = color)
        return(None)


    def add_panel_captions(self, panel_alias, left_caption = None, right_caption = None, padding = 3, font_size = 10, font_style = "normal", left_color = "black", right_color = "black"):
        '''Prints captions to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add captions to.
        left_caption: str specifying text to print as left caption
                      Defaults to None, in which case nothing is printed.
        right_caption: str specifying text to print as right caption
                       Defaults to None, in which case nothing is printed.
        padding: int indicating vertical distance between captions and the top of the vertical axes
                 Defaults to 3.
        font_size: int specifying fontsize for captions.
                   Defaults to 10.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "normal".
        left_color: str specifying color of left caption.
                    Defaults to "black".
        right_color: str specifying color of right caption.
                    Defaults to "black".
        
        Output:
        add_panel_captions(): None, but prints captions to specified panel in-place
        '''

        if left_caption is not None:
            self.panel_dict[panel_alias].set_title(left_caption, loc = "left", pad = padding,
                              fontproperties = self.font_dict[font_style], fontsize = font_size, color = left_color)
        if right_caption is not None:
            self.panel_dict[panel_alias].set_title(right_caption, loc = "right", pad = padding,
                              fontproperties = self.font_dict[font_style], fontsize = font_size, color = right_color)
        return(None)


    def add_panel_footnotes(self, panel_alias, text_list, x_pos = .01, y_pos = -.07, y_delta = -.058, font_size = 9, font_style = "normal", color = "black"):
        '''Prints footnotes to specifed panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add footnotes to.
        text_list: list of str specifying footnote text (supports end-of-line characters and certain LaTeX expressions, including superscripts).
        x_pos: float specifying x-position (in fixed-axis units) for footnotes
               Defaults to .01. 
        y_pos: float specifying y-position (in fixed-axis units) for first footnote.
               Defaults to -.07. Should be a small negative decimal.
        y_delta: float specifying how much vertical space (in fixed-axis units) should be placed between lines.
                 Defaults to -.058. Should be a small negative decimal.
        font_size: int specifying fontsize for footnotes.
                   Defaults to 9.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "normal".
        color: str specifying color of font.
               Defaults to "black".
        
        Output:
        add_panel_footnotes(): None, but prints footnotes to specified panel in-place
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_y_fixed = y_pos
        for fn in text_list:
            curr_ax.text(x_pos, curr_y_fixed, fn, transform = curr_ax.transAxes, va = "top",
                         fontproperties = self.font_dict[font_style], fontsize = font_size, color = color)
            curr_y_fixed += (y_delta * (fn.count("\n") + 1))
        return(None)


    def add_panel_text(self, panel_alias, x_pos, y_pos, text_str, scale = "data", font_style = "normal", font_size = 10, color = "black", horizontal_align = "left", vertical_align = "bottom", rotation = 0):
        '''Prints arbitrary text to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add text to.
        x_pos: specifies x-position of text
               int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_pos: int or float specifying y-position of text
        text_str: str specifying text
        scale: Specifies scale to use for interpreting x_pos and y_pos.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_pos and y_pos as fixed-axis units (mostly lie in [-1.1, 1.1]).
        font_size: int specifying fontsize for text.
                   Defaults to 10.
        font_style: str for "normal", "bold", "italic", or "bold-italic" font.
                    Defaults to "normal".
        color: str specifying color of captions.
               Defaults to "black".
        horizontal_align: str specifying horizontal alignment of text. Can be "left", "center", or "right".
                        Defaults to "left".
        vertical_align: str specifying vertical alignment of text. Can be "bottom", "center", or "top".
                        Defaults to "bottom".
        rotation: float or int specifying the rotation (in degrees) to be applied to the text element
                  Defaults to 0.
        
        Output:
        add_panel_text(): None, but prints text to specified panel in-place
        '''

        curr_ax = self.panel_dict[panel_alias]
        if scale == "data":
            if not isinstance(x_pos, numbers.Number):
                if isinstance(x_pos, pd.Period):
                    x_pos = x_pos.to_timestamp()
                x_coord = mdates.date2num(pd.Timestamp(x_pos))
            else:
                x_coord = x_pos
            y_coord = y_pos
        else:
            x_coord = fixed2data(x_pos, curr_ax, 0)
            y_coord = fixed2data(y_pos, curr_ax, 1)
        curr_ax.text(x_coord, y_coord, text_str, 
                     fontproperties = self.font_dict[font_style], fontsize = font_size, color = color,
                     ha = horizontal_align, va = vertical_align, rotation = rotation)
        return(None)


    def add_panel_keylines(self, panel_alias, x_pos, y_pos, text_list, keyline_length = .08, color_list = None, style_list = None, alpha_list = None, width_list = None, 
                           scale = "data", font_size = 9, text_xoffset = .015, text_yoffset = -.019, y_delta = -.06):
        '''Prints keylines (legend-esque information) to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add keylines to.
        x_pos: specifies x-position of first keyline
               int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_pos: int or float specifying y-position of first keyline
        text_list: list of str specifying label for each keyline
        keyline_length: float specifying length of keylines in fixed-axis units
                        Defaults to .08. Should be a small positive decimal.
        color_list: list of str specifying colors of each keyline
                    Defaults to ["black"]*len(text_list)
        style_list: list of str specifying linestyle of each keyline. 
                    Common linestyles include "-" for solid, "--" for dashed, and ":" for dotted.
                    Defaults to ["-"]*len(text_list)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(ser_list).
        width_list: list of floats specifying line width of each keyline
                    Defaults to [1]*len(text_list)
        scale: Specifies scale to use for interpreting x_pos and y_pos.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_pos and y_pos as fixed-axis units (mostly lie in [-1.1, 1.1]).
        font_size: int specifying fontsize for text.
                   Defaults to 9.
        text_xoffset: float specifying horizontal distance of labels from corresponding keylines in fixed-axis units
                      Defaults to .015
        text_yoffset: float specifying vertical distance of labels from corresponding keylines in fixed-axis units
                      Defaults to -.019
        y_delta: float specifying vertical distance between consecutive keylines in fixed-axis units
                 Defaults to -.06
        
        Output:
        add_panel_keylines(): None, but adds keylines to specified panel in-place
        '''

        curr_ax = self.panel_dict[panel_alias]
        if color_list is None:
            color_list = ["black"] * len(text_list)
        if style_list is None:
            style_list = ["-"] * len(text_list)
        if alpha_list is None:
            alpha_list = [1] * len(text_list)
        if width_list is None:
            width_list = [1] * len(text_list)
        if scale == "data":
            if not isinstance(x_pos, numbers.Number):
                if isinstance(x_pos, pd.Period):
                    x_pos = x_pos.to_timestamp()
                x_coord = mdates.date2num(pd.Timestamp(x_pos))
            else:
                x_coord = x_pos
            y_coord = y_pos
        else:
            x_coord = fixed2data(x_pos, curr_ax, 0)
            y_coord = fixed2data(y_pos, curr_ax, 1)
        x_min = curr_ax.get_xlim()[0]
        x_range = curr_ax.get_xlim()[1] - curr_ax.get_xlim()[0]
        y_range = curr_ax.get_ylim()[1] - curr_ax.get_ylim()[0]
        for ind in range(len(text_list)):
            curr_ax.axhline(y_coord, (x_coord - x_min)/x_range, (x_coord - x_min)/x_range + keyline_length, 
                            color = color_list[ind], ls = style_list[ind], lw = width_list[ind], alpha = alpha_list[ind])
            curr_ax.text(x_coord + ((keyline_length + text_xoffset) * x_range), 
                         y_coord + (text_yoffset * y_range), 
                         text_list[ind], fontproperties = self.font_dict["normal"], fontsize = font_size, 
                         color = color_list[ind])
            y_coord += y_delta * y_range
        return(None)


    def add_panel_keydots(self, panel_alias, x_pos, y_pos, text_list, color_list = None, marker_type_list = None, marker_size_list = None, alpha_list = None, scale = "data", font_size = 9, 
                          text_xoffset = .03, text_yoffset = -.019, y_delta = -.06):
        '''Prints keydots (legend-esque information) to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add keydots to.
        x_pos: specifies x-position of first keydot
               int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_pos: int or float specifying y-position of first keydot
        text_list: list of str specifying label for each keydot
        color_list: list of str specifying colors of each keydot
                    Defaults to ["black"]*len(text_list)
        marker_type_list: list of str specifying marker (shape) of each keydot. 
                          Common markers include "o" for circles and "s" for squares.
                          Defaults to ["o"]*len(text_list)
        marker_size_list: list of int or float specifying size of each keydot in points. 
                          Defaults to [5]*len(text_list)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(ser_list).
        scale: Specifies scale to use for interpreting x_pos and y_pos.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_pos and y_pos as fixed-axis units (mostly lie in [-1.1, 1.1]).
        font_size: int specifying fontsize for text.
                   Defaults to 9.
        text_xoffset: float specifying horizontal distance of labels from corresponding keydots in fixed-axis units
                      Defaults to .03
        text_yoffset: float specifying vertical distance of labels from corresponding keydots in fixed-axis units
                      Defaults to -.019
        y_delta: float specifying vertical distance between consecutive keydots in fixed-axis units
                 Defaults to -.06
        
        Output:
        add_panel_keydots(): None, but adds keydots to specified panel in-place
        '''

        curr_ax = self.panel_dict[panel_alias]
        if color_list is None:
            color_list = ["black"] * len(text_list)
        if marker_type_list is None:
            marker_type_list = ["o"] * len(text_list)
        if marker_size_list is None:
            marker_size_list = [5] * len(text_list)
        if alpha_list is None:
            alpha_list = [1] * len(text_list)
        if scale == "data":
            if not isinstance(x_pos, numbers.Number):
                if isinstance(x_pos, pd.Period):
                    x_pos = x_pos.to_timestamp()
                x_coord = mdates.date2num(pd.Timestamp(x_pos))
            else:
                x_coord = x_pos
            y_coord = y_pos
        else:
            x_coord = fixed2data(x_pos, curr_ax, 0)
            y_coord = fixed2data(y_pos, curr_ax, 1)
        x_range = curr_ax.get_xlim()[1] - curr_ax.get_xlim()[0]
        y_range = curr_ax.get_ylim()[1] - curr_ax.get_ylim()[0]
        for ind in range(len(text_list)):
            curr_ax.plot(x_coord, y_coord, 
                         marker = marker_type_list[ind], markersize = marker_size_list[ind], color = color_list[ind], alpha = alpha_list[ind])
            curr_ax.text(x_coord + (text_xoffset * x_range), 
                         y_coord + (text_yoffset * y_range), 
                         text_list[ind], fontproperties = self.font_dict["normal"], fontsize = font_size, 
                         color = color_list[ind])
            y_coord += y_delta * y_range
        return(None)


    def add_panel_keyboxes(self, panel_alias, x_pos, y_pos, text_list, face_color_list = None, edge_color_list = None, hatch_list = None, alpha_list = None, line_width_list = None, scale = "data", font_size = 9,
                           box_length = .05, box_width = .04, text_xoffset = .065, text_yoffset = -.018, y_delta = -.06):
        '''Prints keyboxes (legend-esque information) to specified panel.
        Note that .ps files do not properly apply hatching. Use another file format in these instances.
        
        Inputs:
        panel_alias: the panel alias for the chart to add keyboxes to.
        x_pos: specifies x-position of first keybox
               int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_pos: int or float specifying y-position of first keybox
        text_list: list of str specifying label for each keybox
        face_color_list: list of str specifying what color to use for each bar's interior
                         Defaults to ["white"]*len(text_list)
        edge_color_list: list of str specifying what color to use for each bar's edges and hatching (if applicable)
                         Defaults to ["black"]*len(text_list)
        hatch_list: list of str specifying hatching of each keybox. 
                    Common hatching options include "" for no hatching, "/", "\", "x", and "+".
                    Hatching can be intensfied through repetition (ie "///" has denser hatching than "/" and "//")
                    Defaults to [""]*len(text_list)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(ser_list).
        line_width_list: list of floats specifying width of bar edges
                         Defaults to [1]*len(text_list)
        scale: Specifies scale to use for interpreting x_pos and y_pos.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_pos and y_pos as fixed-axis units (mostly lie in [-1.1, 1.1]).
        font_size: int specifying fontsize for text.
                   Defaults to 9.
        box_length: float specifying horizontal dimension of keyboxes in fixed-axis units
                    Defaults to .05
        box_width: float specifying vertical dimension of keyboxes in fixed-axis units
                   Defaults to .04
        text_xoffset: float specifying horizontal distance of labels from corresponding keyboxes in fixed-axis units
                      Defaults to .065
        text_yoffset: float specifying vertical distance of labels from corresponding keyboxes in fixed-axis units
                      Defaults to -.0115
        y_delta: float specifying vertical distance between consecutive keyboxes in fixed-axis units
                 Defaults to -.06
        
        Output:
        add_panel_keyboxes(): None, but adds keyboxes to specified panel in-place
        '''        

        curr_ax = self.panel_dict[panel_alias]
        if edge_color_list is None:
            edge_color_list = ["black"] * len(text_list)
        if face_color_list is None:
            face_color_list = ["white"] * len(text_list)
        if hatch_list is None:
            hatch_list = [""] * len(text_list)
        if alpha_list is None:
            alpha_list = [1] * len(text_list)
        if line_width_list is None:
            line_width_list = [1] * len(text_list)
        if scale == "data":
            if not isinstance(x_pos, numbers.Number):
                if isinstance(x_pos, pd.Period):
                    x_pos = x_pos.to_timestamp()
                x_coord = mdates.date2num(pd.Timestamp(x_pos))
            else:
                x_coord = x_pos
            y_coord = y_pos
        else:
            x_coord = fixed2data(x_pos, curr_ax, 0)
            y_coord = fixed2data(y_pos, curr_ax, 1)
        x_range = curr_ax.get_xlim()[1] - curr_ax.get_xlim()[0]
        y_range = curr_ax.get_ylim()[1] - curr_ax.get_ylim()[0]
        for ind in range(len(text_list)):
            curr_ax.fill_between([x_coord, x_coord + box_length * x_range], 
                                     y_coord + (box_width/2 * y_range), 
                                     y_coord - (box_width/2 * y_range),
                                     facecolor = face_color_list[ind], edgecolor = edge_color_list[ind], hatch = hatch_list[ind], alpha = alpha_list[ind], linewidth = line_width_list[ind])
            curr_ax.text(x_coord + (text_xoffset * x_range), 
                         y_coord + (text_yoffset * y_range), 
                         text_list[ind], fontproperties = self.font_dict["normal"], fontsize = font_size, color = 'black')
            y_coord += y_delta * y_range
        return(None)


    def add_panel_hline(self, panel_alias, y, x_min = None, x_max = None, scale = "data", line_style = "-", line_width = 1.3, color = "black", alpha = 1):
        '''Prints horizontal line to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add the line to
        y: int or float specifying vertical position of the line
        x_min: int, float, date, or date str specifying the horizontal position of an endpoint of the line
               Defaults to minimum of the x-axis range or 0 (depending on whether scale == "data" or "fixed")
        x_max: int, float, date, or date str specifying the horizontal position of an endpoint of the line
               Defaults to maximum of the x-axis range or 1 (depending on whether scale == "data" or "fixed")
        scale: str specifying how the function should interpret the y, x_min, and x_max arguments
               Defaults to "data", in which case these arguments are interpreted according to the axes' scale.
               Otherwise, the coordinates are interpreted in fixed-axis units (mostly lie in [-1.1, 1.1]).
        line_style: str specifying style of line to draw
                    Common linestyles include "-" for solid, "--" for dashed, and ":" for dotted.
                    Defaults to "-"
        line_width: int or float specifying width of line to draw in points
                    Defaults to 1.3 (same width as the axes)
        color: str specifying the line's color
               Defaults to "black"
        alpha: int or float specifying opaqueness of line
               Defaults to 1.
        
        Output:
        add_panel_hline(): None, but adds a horizontal line to specified panel in place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        if scale == "data":
            if x_min is None:
                x_min = curr_ax.get_xlim()[0]
            if x_max is None:
                x_max = curr_ax.get_xlim()[1]
            if not isinstance(x_min, numbers.Number):
                if isinstance(x_min, pd.Period):
                    x_min = x_min.to_timestamp()
                x_min = mdates.date2num(pd.Timestamp(x_min))
            if not isinstance(x_max, numbers.Number):
                if isinstance(x_max, pd.Period):
                    x_max = x_max.to_timestamp()
                x_max = mdates.date2num(pd.Timestamp(x_max))
            x_min = data2fixed(x_min, curr_ax, 0)
            x_max = data2fixed(x_max, curr_ax, 0)
        else:
            if x_min is None:
                x_min = 0
            if x_max is None:
                x_max = 1
            y = fixed2data(y, curr_ax, 1)
        curr_ax.axhline(y, x_min, x_max, ls = line_style, lw = line_width, color = color, alpha = alpha)
        return(None)


    def add_panel_vline(self, panel_alias, x, y_min = None, y_max = None, scale = "data", line_style = "-", line_width = 1, color = "black", alpha = 1):
        '''Prints vertical line to specified panel.
        
        Inputs:
        panel_alias: the panel alias for the chart to add the line to
        x: int or float specifying horizontal position of the line
        y_min: int or float specifying the vertical position of an endpoint of the line
               Defaults to minimum of the y-axis range or 0 (depending on whether scale == "data" or "fixed")
        y_max: int or float specifying the vertical position of an endpoint of the line
               Defaults to maximum of the y-axis range or 1 (depending on whether scale == "data" or "fixed")
        scale: str specifying how the function should interpret the y, x_min, and x_max arguments
               Defaults to "data", in which case these arguments are interpreted according to the axes' scale.
               Otherwise, the coordinates are interpreted in fixed-axis units (mostly lie in [-1.1, 1.1]).
        line_style: str specifying style of line to draw
                    Common linestyles include "-" for solid, "--" for dashed, and ":" for dotted.
                    Defaults to "-"
        line_width: int or float specifying width of line to draw in points
                    Defaults to 1 (slightly thinner than the axes)
        color: str specifying the line's color
               Defaults to "black"
        alpha: int or float specifying opaqueness of line
               Defaults to 1.
        
        Output:
        add_panel_vline(): None, but adds a vertical line to specified panel in place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        if scale == "data":
            if y_min is None:
                y_min = curr_ax.get_ylim()[0]
            if y_max is None:
                y_max = curr_ax.get_ylim()[1]
            if not isinstance(x, numbers.Number):
                if isinstance(x, pd.Period):
                    x = x.to_timestamp()
                x = mdates.date2num(pd.Timestamp(x))
            y_min = data2fixed(y_min, curr_ax, 1)
            y_max = data2fixed(y_max, curr_ax, 1)
        else:
            if y_min is None:
                y_min = 0
            if y_max is None:
                y_max = 1
            x = fixed2data(x, curr_ax, 0)
        curr_ax.axvline(x, y_min, y_max, ls = line_style, lw = line_width, color = color, alpha = alpha)
        return(None)

    def add_panel_shading(self, panel_alias, x_range, y_low = None, y_high = None, face_color = "dodgerblue", edge_color = None, hatch = "", alpha = .3, scale = "data"):
        '''Adds solid or hatched shading over a region of the specified panel
        Note that .ps files do not properly apply hatching and alpha settings for shaded regions. Use another file format in these instances.
        
        Inputs:
        panel_alias: the panel alias for the chart to add shading to.
        x_range: iterable object of at least 2 x-coordinate over which shading should be applied
                 Elements should be int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_low: Iterable object (list, tuple, pd.Series) of ints or floats specifying lower bound of shaded region
               If len(y_low) = 1, the lower bound is a horizontal line. Include additional elements for more complicated bounds. 
               If len(y_low) > 1, x_range, y_low, and y_high should contain the same number of elements.
               Defaults to minimum of the y-axis range.
        y_high: Iterable object (list, tuple, pd.Series) of ints or floats specifying upper bound of shaded region
                If len(y_high) = 1, the upper bound is a horizontal line. Include additional elements for more complicated bounds. 
                If len(y_high) > 1, x_range, y_low, and y_high should contain the same number of elements.
                Defaults to maximum of the y-axis range.
        face_color: str specifying color of shaded region interior
                    Defaults to "dodgerblue".
        edge_color: str specifying  color of hatching (if applicable) of shaded region
                    Defaults to face_color's value
        hatch: str specifying hatching of shaded region. 
               Common hatching options include "" for no hatching, "/", "\", "x", and "+".
               Hatching can be intensfied through repetition (ie "///" has denser hatching than "/" and "//")
               Defaults to ""
        alpha: float lying in [0,1] that specifies transparency of shading (alpha = 1 equates to minimal transparency)
               Defaults to .3
        scale: Specifies scale to use for interpreting x_pos and y_pos.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_pos and y_pos as fixed-axis units (mostly lie in [-1.1, 1.1]).
        
        Output:
        add_panel_shading(): None, but adds shaded region to specified panel in-place
        '''          

        curr_ax = self.panel_dict[panel_alias]
        if edge_color is None:
            edge_color = face_color
        if scale == "data":
            if not isinstance(x_range[0], numbers.Number):
                if isinstance(x_range[0], pd.Period):
                    x_range = [x.to_timestamp() for x in x_range]
                x_span = [mdates.date2num(pd.Timestamp(coord)) for coord in x_range]
            else:
                x_span = [coord for coord in x_range]
            if y_low is None:
                y_low = [fixed2data(0, curr_ax, 1)]
            if y_high is None:
                y_high = [fixed2data(1, curr_ax, 1)]
            y1 = y_low
            y2 = y_high
        else:
            x_span = [fixed2data(coord, curr_ax, 0) for coord in x_range]
            if y_low is None:
                y_low = [0]
            if y_high is None:
                y_high = [1]
            y1 = [fixed2data(coord, curr_ax, 1) for coord in list(y_low)]
            y2 = [fixed2data(coord, curr_ax, 1) for coord in list(y_high)]
        curr_ax.fill_between(x_span, y1, y2,
                             alpha = alpha, facecolor = face_color, edgecolor = edge_color, hatch = hatch)
        return(None)


    def add_panel_arrow(self, panel_alias, x_range, y_range, color = "black", scale = "data", head_length = .5, head_width = .35):
        '''Draws arrow on specified panel.

        Inputs:
        panel_alias: the panel alias for the chart to add an arrow to.
        x_range: list or tuple of 2 elements specifying x-coordinates of the beginning and end of the arrow
                 Elements should be int or float. If scale = "data", date and date str (with format %Y-%m-%d) are also acceptable.
        y_range: list or tuple of 2 elements specifying y-coordinates of the beginning and end of the arrow
                 Elements should be int or float.
        color: str specifying color of arrow
        scale: Specifies scale to use for interpreting x_range and y_range elements.
               Defaults to "data", which uses scale of axes. 
               All other values (but preferably the str "fixed") will cause it to interpret x_range and y_range elements as fixed-axis units (mostly lie in [-1.1, 1.1]).
        head_length: float specifying length of arrow head as a fraction of total arrow length
                     Defaults to .5
        head_width: float specifying width of arrow head in points
                    Defaults to .35

        Output:
        add_panel_arrow(): None, but adds shaded region to specified panel in-place
        ''' 

        curr_ax = self.panel_dict[panel_alias]
        if scale == "data":
            if not isinstance(x_range[0], numbers.Number):
                if isinstance(x_range[0], pd.Period):
                    x_range = [x.to_timestamp() for x in x_range]
                x_span = [mdates.date2num(pd.Timestamp(coord)) for coord in x_range]
            else:
                x_span = x_range
            y_span = y_range
        else:
            x_span = [fixed2data(coord, curr_ax, 0) for coord in x_range]
            y_span = [fixed2data(coord, curr_ax, 1) for coord in y_range]
        curr_ax.annotate("", (x_span[0], y_span[0]), (x_span[1], y_span[1]),
                         arrowprops = {"arrowstyle": "<-, head_length = " + str(head_length) + ", head_width = " + str(head_width), "color": color})
        return(None)


    def plot_panel_ts_line(self, panel_alias, ser, ser_freq = None, number_stacks = 1, curr_stack = 1, bar_width_coef = 1, pos_adj = 0, line_color = "black", line_style = "-", line_width = 1, marker_type = "", marker_size = 5, alpha = 1):
        '''Plots a time series on the specified panel as a line.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        ser: pd.Series to be plotted. ser should have a PeriodIndex or DatetimeIndex.
        ser_freq: str indicating frequency of ser
                  Should be an element of ["min", "h", "d", "b", "w", "m", "q", "a", "y"] (not case-sensitive), which maps to ["minute", "hour", "daily", "business", "week", "month", "quarter", "annual", "annual"].
                  You may supply "5", "10", "15", "20", or "30" as a prefix to "min" (ie "5min"); "2", "3", "4", "6", "8", or "12" as a prefix to "h"; "6" as a prefix for "m"; or "2" as a prefix to "q" to apply a skip parameter.
                  Defaults to None, in which case an attempt is made to determine the frequency based on ser's attributes.
                  This argument is only useful when ser does not have a freq attribute (when dealing with pd.Datetime, also occassionally happens when ser is subsetted down to 1 observation).
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        For example, the base width for a monthly series bars is about 30 days by default (assuming you're only plotting one stack). 
                        With bar_width_coef = .8, this function will instead use .8 * 30 = 24 days as the width instead.
                        Defaults to 1. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        pos_adj: int or float specifying adjustment to be made to bars' locations (value is interpreted in units of days). Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error). This should only be used when trying to align a line with a dodge barchart (HEAVILY discouraged).
        line_color: str specifying color of line to be plotted
                    Defaults to "black"
        line_style: str specifying style of line to be plotted. 
                    Common choices include "-" for solid, "--" for dashed, and ":" for dotted
                    Defaults to "-" for solid.
        line_width: float specifying width of line to be plotted in points
                    Defaults to 1
        marker_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "" for none.
        marker_size: int or float specifying size of markers in points
                     Defaults to 5.
        alpha: int or float specifying opaqueness of line
               Defaults to 1.

        Output:
        plot_panel_ts_line(): None, but adds a line plot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        x_range = curr_ax.get_xlim()
        
        if type(ser_freq) is str:
            ser_freq_dict = {x: x.upper() for x in ["min", "h", "d", "b", "w", "m", "6m", "q", "2q", "a", "y"]}
            ser_freq_dict["a"] = "Y"
            for x in ["", "5", "10", "15", "20", "30"]:
                ser_freq_dict[f'{x}min'] = f'{x}min'
            
            for x in ["", "2", "3", "4", "6", "8", "12"]:
                ser_freq_dict[f'{x}h'] = f'{x}h'
            
            ser_freq_obj = pd.Period("1970-01-01", freq = ser_freq_dict[ser_freq.lower()]).freq
        else:
            if hasattr(ser.index, "freq"):
                if ser.index.freq is not None:
                    ser_freq_obj = ser.index.freq
                else:
                    assert len(ser) >= 3, "ser has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                    ser_freq_obj = pd.infer_freq(ser.index)
            else:
                assert len(ser) >= 3, "ser has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                ser_freq_obj = pd.infer_freq(ser.index)
        
        curr_ax.plot(center_ts_obs(impose_ts_xrange(period_to_ts(ser), x_range), str(ser_freq_obj), number_stacks, curr_stack, bar_width_coef, pos_adj), color = line_color, linestyle = line_style, linewidth = line_width, marker = marker_type, markersize = marker_size, alpha = alpha)
        return(None)


    def plot_panel_ts_scatter(self, panel_alias, ser, ser_freq = None, number_stacks = 1, curr_stack = 1, bar_width_coef = 1, pos_adj = 0, scatter_type = "o", scatter_color = "black", scatter_size = 5, alpha = 1):
        '''Plots a time series on the specified panel as a scatterplot.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        ser: pd.Series to be plotted. ser should have a PeriodIndex or DatetimeIndex.
        ser_freq: str indicating frequency of ser
                  Should be an element of ["min", "h", "d", "b", "w", "m", "q", "a", "y"] (not case-sensitive), which maps to ["minute", "hour", "daily", "business", "week", "month", "quarter", "annual", "annual"].
                  You may supply "5", "10", "15", "20", or "30" as a prefix to "min" (ie "5min"); "2", "3", "4", "6", "8", or "12" as a prefix to "h"; "6" as a prefix for "m"; or "2" as a prefix to "q" to apply a skip parameter.
                  Defaults to None, in which case an attempt is made to determine the frequency based on ser's attributes.
                  This argument is only useful when ser does not have a freq attribute (when dealing with pd.Datetime, also occassionally happens when ser is subsetted down to 1 observation).
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1. Should only be altered when trying to align a scatter series with a dodge bar chart.
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks. Should only be altered when trying to align a scatter series with a dodge bar chart.
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        For example, the base width for a monthly series bars is about 30 days by default (assuming you're only plotting one stack). 
                        With bar_width_coef = .8, this function will instead use .8 * 30 = 24 days as the width instead.
                        Defaults to 1. Should only be altered when trying to align a scatter series with a dodge bar chart.
        pos_adj: int or float specifying adjustment to be made to bars' locations (value is interpreted in units of days). Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error). This should only be used when trying to align a scatter series with a dodge barchart.
        scatter_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "o" for circles.
        scatter_color: str specifying color of line to be plotted
                       Defaults to "black"
        scatter_size: int or float specifying size of markers in points
                      Defaults to 5.
        alpha: int or float specifying opaqueness of markers
               Defaults to 1.

        Output:
        plot_panel_ts_scatter(): None, but adds a scatterplot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        x_range = curr_ax.get_xlim()
        
        if type(ser_freq) is str:
            ser_freq_dict = {x: x.upper() for x in ["min", "h", "d", "b", "w", "m", "6m", "q", "2q", "a", "y"]}
            ser_freq_dict["a"] = "Y"
            for x in ["", "5", "10", "15", "20", "30"]:
                ser_freq_dict[f'{x}min'] = f'{x}min'
            
            for x in ["", "2", "3", "4", "6", "8", "12"]:
                ser_freq_dict[f'{x}h'] = f'{x}h'
            
            ser_freq_obj = pd.Period("1970-01-01", freq = ser_freq_dict[ser_freq.lower()]).freq
        else:
            if hasattr(ser.index, "freq"):
                if ser.index.freq is not None:
                    ser_freq_obj = ser.index.freq
                else:
                    assert len(ser) >= 3, "ser has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                    ser_freq_obj = pd.infer_freq(ser.index)
            else:
                assert len(ser) >= 3, "ser has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                ser_freq_obj = pd.infer_freq(ser.index)
        
        curr_ax.plot(center_ts_obs(impose_ts_xrange(period_to_ts(ser), x_range), str(ser_freq_obj), number_stacks, curr_stack, bar_width_coef, pos_adj), linestyle = "None", marker = scatter_type, color = scatter_color, markersize = scatter_size, alpha = alpha)
        return(None)


    def plot_panel_ts_barstack(self, panel_alias, ser_list, ser_freq = None, number_stacks = 1, curr_stack = 1, pos_adj = 0, bar_width_coef = .8, edge_color_list = None, face_color_list = None, 
                               hatch_list = None, alpha_list = None, line_width_list = None):
        '''Plots time series on the specified panel as a stacked barchart.
        Note that .ps files do not properly apply hatching for barcharts. Use another file format in these instances.

        Inputs:
        panel_alias: the panel alias for the chart to add a bar stack to.
        ser_list: list of pd.Series to be plotted. Each Series should have a PeriodIndex or DatetimeIndex with the same frequency.
        ser_freq: str indicating frequency of the series in ser_list
                  Should be an element of ["min", "h", "d", "b", "w", "m", "q", "a", "y"] (not case-sensitive), which maps to ["minute", "hour", "daily", "business", "week", "month", "quarter", "annual", "annual"].
                  You may supply "5", "10", "15", "20", or "30" as a prefix to "min" (ie "5min"); "2", "3", "4", "6", "8", or "12" as a prefix to "h"; "6" as a prefix for "m"; or "2" as a prefix to "q" to apply a skip parameter.
                  Defaults to None, in which case an attempt is made to determine the frequency based on the series' attributes.
                  This argument is only useful when ser does not have a freq attribute (when dealing with pd.Datetime, also occassionally happens when ser is subsetted down to 1 observation).
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1.
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks
        pos_adj: int or float specifying adjustment to be made to bars' locations (value is interpreted in units of days). Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error)
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        For example, the base width for a monthly series bars is about 30 days by default (assuming you're only plotting one stack). 
                        With bar_width_coef = .8, this function will instead use .8 * 30 = 24 days as the width instead.
                        Defaults to .8
        line_width_list: list of float or int specifying width of bar edges in points
                         Defaults to [1]*len(ser_list).
        edge_color_list: list of str specifying what color to use for each bar's edges and hatching (if applicable)
                        Defaults to ["black"]*len(ser_list)
        face_color_list: list of str specifying what color to use for each bar's interior
                        Defaults to ["white"]*len(ser_list)
        hatch_list: list of str specifying hatching pattern for each bar
                    Common choices include "" for no hatching, "/", "\", "x", and "+".
                    Hatching can be intensfied through repetition (ie "///" has denser hatching than "/" and "//")
                    Defaults to [""]*len(ser_list)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(ser_list).
        line_width_list: list of float or int specifying width of bar edges in points
                         Defaults to [1]*len(ser_list).

        Output:
        plot_panel_ts_barstack(): None, but adds a bar stack to specified panel in-place.
        '''        

        curr_ax = self.panel_dict[panel_alias]
        if edge_color_list is None:
            edge_color_list = ["black"] * len(ser_list)
        if face_color_list is None:
            face_color_list = ["white"] * len(ser_list)
        if hatch_list is None:
            hatch_list = [""] * len(ser_list)
        if alpha_list is None:
            alpha_list = [1] * len(ser_list)
        if line_width_list is None:
            line_width_list = [1] * len(ser_list)
        
        if type(ser_freq) is str:
            ser_freq_dict = {x: x.upper() for x in ["min", "h", "d", "b", "w", "m", "6m", "q", "2q", "a", "y"]}
            ser_freq_dict["a"] = "Y"
            for x in ["", "5", "10", "15", "20", "30"]:
                ser_freq_dict[f'{x}min'] = f'{x}min'
            
            for x in ["", "2", "3", "4", "6", "8", "12"]:
                ser_freq_dict[f'{x}h'] = f'{x}h'
            
            ser_freq_obj = pd.Period("1970-01-01", freq = ser_freq_dict[ser_freq.lower()]).freq
        else:
            if hasattr(ser_list[0].index, "freq"):
                if ser_list[0].index.freq is not None:
                    ser_freq_obj = ser_list[0].index.freq
                else:
                    assert len(ser_list[0]) >= 3, "ser_list[0] has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                    ser_freq_obj = pd.infer_freq(ser_list[0].index)
            else:
                assert len(ser_list[0]) >= 3, "ser_list[0] has no stored freq and is not long enough for pd.infer_freq(), so you must specify ser_freq as an argument. See docstring for details."
                ser_freq_obj = pd.infer_freq(ser_list[0].index)
        
        bar_width = calc_ts_bar_width(str(ser_freq_obj), number_stacks, width_coef = bar_width_coef)
        x_range = curr_ax.get_xlim()
        
        centered_list = [center_ts_obs(impose_ts_xrange(period_to_ts(ser), x_range), str(ser_freq_obj), number_stacks, curr_stack, bar_width_coef, pos_adj) for ser in ser_list]
        all_index = centered_list[0].index
        for ser_num in range(1,len(centered_list)):
            all_index = all_index.append(centered_list[ser_num].index)
    
        all_index = all_index.unique().sort_values()
        
        # bottom_list holds information for where each bar should start vertically
        # bottom_list[0] ([1]) holds running tally of all positive (negative) values already plotted
        # bottom_list[2] is updated with vertical starting positions for each bar of each series. It is reset from scratch for each series.
        bottom_list = [[0] * len(all_index), [0] * len(all_index), [0] * len(all_index)]
        
        for ser_num in range(len(centered_list)):
            for time_ind in all_index:
                if (time_ind not in centered_list[ser_num].index) or pd.isnull(centered_list[ser_num][time_ind]):
                    centered_list[ser_num][time_ind] = 0
            centered_list[ser_num] = centered_list[ser_num].sort_index()
            for ind in range(len(centered_list[ser_num])):
                if centered_list[ser_num][centered_list[ser_num].index[ind]] >= 0:
                    bottom_list[2][ind] = bottom_list[0][ind]
                    bottom_list[0][ind] += centered_list[ser_num][centered_list[ser_num].index[ind]]
                else:
                    bottom_list[2][ind] = bottom_list[1][ind]
                    bottom_list[1][ind] += centered_list[ser_num][centered_list[ser_num].index[ind]]
            curr_ax.bar(all_index, centered_list[ser_num], width = bar_width, linewidth = line_width_list[ser_num], edgecolor = edge_color_list[ser_num], 
                        facecolor = face_color_list[ser_num], hatch = hatch_list[ser_num], alpha = alpha_list[ser_num], bottom = bottom_list[2])
        return(None)


    def plot_panel_cs_line(self, panel_alias, ser, number_stacks = 1, curr_stack = 1, bar_width_coef = 1, pos_adj = 0, line_color = "black", line_style = "-", line_width = 1, marker_type = "", marker_size = 5, alpha = 1, orientation = "vertical"):
        '''Plots a cross-sectional series on the specified panel as a line.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        ser: iterable holding values to be plotted
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        For example, the base width for a monthly series bars is about 30 days by default (assuming you're only plotting one stack). 
                        With bar_width_coef = .8, this function will instead use .8 * 30 = 24 days as the width instead.
                        Defaults to 1. Should only be altered when trying to align a line series with a dodge bar chart (HEAVILY discouraged).
        pos_adj: int or float specifying adjustment to be made to bars' locations. Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error). Should only be used when trying to align a line with a dodge bar chart (HEAVILY discouraged).
        line_color: str specifying color of line to be plotted
                    Defaults to "black"
        line_style: str specifying style of line to be plotted. 
                    Common choices include "-" for solid, "--" for dashed, and ":" for dotted
                    Defaults to "-" for solid.
        line_width: float specifying width of line to be plotted in points
                    Defaults to 1
        marker_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "" for none.
        marker_size: int or float specifying size of markers in points
                     Defaults to 5.
        alpha: int or float specifying opaqueness of line
               Defaults to 1.
        orientation: str specifying orientation of chart
                     Defaults to "vertical". Should only be changed if trying to plot a line over a horizontal bar chart (HEAVILY discouraged).

        Output:
        plot_panel_cs_line(): None, but adds a line plot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        centered_pos = center_cs_obs(ser, number_stacks = number_stacks, curr_stack = curr_stack, width_coef = bar_width_coef, pos_adj = pos_adj)
        if orientation == "vertical":
            curr_ax.plot(centered_pos, ser, color = line_color, linestyle = line_style, linewidth = line_width, marker = marker_type, markersize = marker_size, alpha = alpha)
        else:
            curr_ax.plot(ser, centered_pos, color = line_color, linestyle = line_style, linewidth = line_width, marker = marker_type, markersize = marker_size, alpha = alpha)
        return(None)


    def plot_panel_cs_scatter(self, panel_alias, ser, number_stacks = 1, curr_stack = 1, bar_width_coef = 1, pos_adj = 0, scatter_type = "o", scatter_color = "black", scatter_size = 5, alpha = 1, orientation = "vertical"):
        '''Plots a cross-sectional series on the specified panel as a scatterplot.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        ser: iterable holding values to be plotted
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1. Should only be altered when trying to align a scatter series with a dodge bar chart.
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks. Should only be altered when trying to align a scatter series with a dodge bar chart.
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        For example, the base width for a monthly series bars is about 30 days by default (assuming you're only plotting one stack). 
                        With bar_width_coef = .8, this function will instead use .8 * 30 = 24 days as the width instead.
                        Defaults to 1. Should only be altered when trying to align a scatter series with a dodge bar chart.
        pos_adj: int or float specifying adjustment to be made to bars' locations. Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error). Should only be used when trying to align a scatter series with a dodge bar chart.
        scatter_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "o" for circles.
        scatter_color: str specifying color of line to be plotted
                       Defaults to "black"
        scatter_size: int or float specifying size of markers in points
                      Defaults to 5.
        alpha: int or float specifying opaqueness of line
               Defaults to 1.
        orientation: str specifying orientation of chart
                     Defaults to "vertical". Should only be changed if trying to plot a line over a horizontal bar chart.

        Output:
        plot_panel_cs_scatter(): None, but adds a scatterplot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        centered_pos = center_cs_obs(ser, number_stacks = number_stacks, curr_stack = curr_stack, width_coef = bar_width_coef, pos_adj = pos_adj)
        if orientation == "vertical":
            curr_ax.plot(centered_pos, ser, linestyle = "None", marker = scatter_type, color = scatter_color, markersize = scatter_size, alpha = alpha)
        else:
            curr_ax.plot(ser, centered_pos, linestyle = "None", marker = scatter_type, color = scatter_color, markersize = scatter_size, alpha = alpha)
        return(None)


    def plot_panel_cs_barstack(self, panel_alias, ser_list, number_stacks = 1, curr_stack = 1, pos_adj = 0, edge_color_list = None, face_color_list = None,
                               hatch_list = None, alpha_list = None, line_width_list = None, bar_width_coef = .8, orientation = "vertical"):
        '''Plots cross-sectional series on the specified panel as a stacked barchart.
        Note that .ps files do not properly apply hatching for barcharts. Use another file format in these instances.

        Inputs:
        panel_alias: the panel alias for the chart to add a bar stack to.
        ser_list: list of iterables holding values to be plotted.
        number_stacks: positive int specifying how many separate stacks (with overlapping date coverage) are to be plotted on this panel (used for centering purposes)
                       Defaults to 1.
        curr_stack: positive int specifying what number stack this function call is building (if this is the first plot_panel_barstack() call, this is 1; if it's the second call, use 2)
                    Defaults to 1. This number should be <= number_stacks
        pos_adj: int or float specifying adjustment to be made to bars' locations. Intended to help correct instances where bar edges overlap
                 Defaults to 0 (assumes no error)
        edge_color_list: list of str specifying what color to use for each bar's edges and hatching (if applicable)
                        Defaults to ["black"]*len(ser_list)
        face_color_list: list of str specifying what color to use for each bar's interior
                        Defaults to ["white"]*len(ser_list)
        hatch_list: list of str specifying hatching pattern for each bar
                    Common choices include "" for no hatching, "/", "\", "x", and "+".
                    Hatching can be intensfied through repetition (ie "///" has denser hatching than "/" and "//")
                    Defaults to [""]*len(ser_list)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(ser_list).
        line_width_list: list of float or int specifying width of bar edges in points
                         Defaults to [1]*len(ser_list).
        bar_width_coef: float or int to be applied to bar widths as a coefficient
                        Defaults to .8.
        orientation: str specifying orientation of bars (verticals bars vs. horizontal bars)
                     Defaults to "vertical". All other values are interpreted to "horizontal"

        Output:
        plot_panel_cs_barstack(): None, but adds a bar stack to specified panel in-place with orientation specified.
        '''

        curr_ax = self.panel_dict[panel_alias]
        if edge_color_list is None:
            edge_color_list = ["black"] * len(ser_list)
        if face_color_list is None:
            face_color_list = ["white"] * len(ser_list)
        if hatch_list is None:
            hatch_list = [""] * len(ser_list)
        if alpha_list is None:
            alpha_list = [1] * len(ser_list)
        if line_width_list is None:
            line_width_list = [1] * len(ser_list)
        
        bar_width = bar_width_coef/number_stacks
        bar_locations = center_cs_obs(ser_list[0], number_stacks = number_stacks, curr_stack = curr_stack, width_coef = bar_width_coef, pos_adj = pos_adj)
        
        # bottom_list holds information for where each bar should start vertically (or horizontal when making a horizontal bar chart)
        # bottom_list[0] ([1]) holds running tally of all positive (negative) values already plotted
        # bottom_list[2] is updated with vertical starting positions for each bar of each series. It is reset from scratch for each series.
        bottom_list = [[0] * len(ser_list[0]), [0] * len(ser_list[0]), [0] * len(ser_list[0])]
        
        for ser_num in range(len(ser_list)):
            for ind in range(len(ser_list[ser_num])):
                if ser_list[ser_num][ind] >= 0:
                    bottom_list[2][ind] = bottom_list[0][ind]
                    bottom_list[0][ind] += ser_list[ser_num][ind]
                else:
                    bottom_list[2][ind] = bottom_list[1][ind]
                    bottom_list[1][ind] += ser_list[ser_num][ind]
            if orientation == "vertical":
                curr_ax.bar(bar_locations, ser_list[ser_num], width = bar_width, linewidth = line_width_list[ser_num], edgecolor = edge_color_list[ser_num], 
                            facecolor = face_color_list[ser_num], hatch = hatch_list[ser_num], alpha = alpha_list[ser_num], bottom = bottom_list[2])
            else:
                curr_ax.barh(bar_locations, ser_list[ser_num], height = bar_width, linewidth = line_width_list[ser_num], edgecolor = edge_color_list[ser_num], 
                             facecolor = face_color_list[ser_num], hatch = hatch_list[ser_num], alpha = alpha_list[ser_num], left = bottom_list[2])
        return(None)


    def plot_panel_cs_pie(self, panel_alias, obs_list, color_list, label_list = None, label_distance = 1.1, auto_pct = None, pct_distance = .6, font_size = 9, 
                          explode_list = None, shadow = False, start_angle = 0, radius = 1, counter_clock = True, wedge_props = None, 
                          center = (0,0), frame = False, rotate_labels = False):
        '''Plots a pie chart on the specified panel.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        obs_list: iterable holding positive numerical values to parition the pie with
                  Every term will be divided by the sum, so there is no need for them to sum to 1.
        color_list: iterable of str specifying colors to use for the pie's wedges
                    Must have the same length as obs_list
        label_list: iterable of str specifying labels to put outside of each wedge
                    Defaults to None for no labels. Must have the same length as obs_list otherwise.
        label_distance: positive numeric specifying how far wedge label should be placed from the wedges in points.
                        Defaults to 1.1.
        auto_pct: str or function specifying how to label the interior of each wedge with its numerical value (scaled so as to sum to 1)
                  Defaults to None for no percent labels. 
                  See the examples at https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.pie.html for valid formats.
        pct_distance: positive numeric specifying how far from the pie's center percent labels should be placed.
                      Defaults to .6.
        font_size: int specifying fontsize for text.
                   Defaults to 9.
        explode_list: iterable of numerics specifying how much wedges should be offset from each other.
                      Defaults to None to keep the pie chart whole (no offset). Must have the same length as obs_list otherwise.
        shadow: boolean indicating whether the pie chart should cast a shadow.
                Defaults to False.
        start_angle: numeric specifying the angle in degrees to offset the first wedge from the x-axis.
                     Defaults to 0.
        radius: postive numeric speicfying the radius of the pie
                Defaults to 1
        counter_clock: boolean indicating whether wedges should be placed in a counter-clockwise manner
                       Defaults to True.
        wedge_props: dictionary of properties to apply to the wedges
                     Defaults to None.
                     See the examples at https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.pie.html for possible inputs.
        center: 2-element iterable specifying location of pie chart's center
                Defaults to (0, 0).
        frame: boolean indicating whether a rectangular frame should be placed around the pie chart
               Defaults to False.
        rotate_labels: boolean indicating whether labels should be rotated to match their wedges' orientation
                       Defaults to False.

        Output:
        plot_panel_cs_pie(): None, but adds a pie chart to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_ax.pie(obs_list, colors = color_list, labels = label_list, labeldistance = label_distance, autopct = auto_pct, pctdistance = pct_distance, 
                    textprops = {"fontproperties": self.font_dict["normal"], "fontsize": font_size}, explode = explode_list, shadow = shadow,
                    startangle = start_angle, radius = radius, counterclock = counter_clock, wedgeprops = wedge_props, center = center, frame = frame,
                    rotatelabels = rotate_labels)


    def plot_panel_num_line(self, panel_alias, x_obs, y_obs, line_color = "black", line_style = "-", line_width = 1, marker_type = "", marker_size = 5, alpha = 1):
        '''Plots a numeric-by-numeric series on the specified panel as a line.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        x_obs: iterable holding x-values to be plotted
        y_obs: iterable holding y-values to be plotted
        line_color: str specifying color of line to be plotted
                    Defaults to "black"
        line_style: str specifying style of line to be plotted. 
                    Common choices include "-" for solid, "--" for dashed, and ":" for dotted
                    Defaults to "-" for solid.
        line_width: float specifying width of line to be plotted in points
                    Defaults to 1
        marker_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "" for none.
        marker_size: int or float specifying size of markers in points
                     Defaults to 5.
        alpha: int or float specifying opaqueness of line
               Defaults to 1.

        Output:
        plot_panel_num_line(): None, but adds a line plot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_ax.plot(x_obs, y_obs, color = line_color, linestyle = line_style, linewidth = line_width, marker = marker_type, markersize = marker_size, alpha = alpha)
        return(None)


    def plot_panel_num_scatter(self, panel_alias, x_obs, y_obs, scatter_type = "o", scatter_color = "black", scatter_size = 5, alpha = 1):
        '''Plots a numeric-by-numeric series on the specified panel as a scatterplot.

        Inputs:
        panel_alias: the panel alias for the chart to add a line plot to.
        x_obs: iterable holding x-values to be plotted
        y_obs: iterable holding y-values to be plotted
        scatter_type: str specifying shape of markers to place over actual observations (which are connected with line segments to form the line).
                     Common choices are "" for none, "o" for circles, and "s" for squares.
                     Defaults to "o" for circles.
        scatter_color: str specifying color of markers to be plotted
                       Defaults to "black"
        scatter_size: int or float specifying size of markers in points
                      Defaults to 5
        alpha: int or float specifying opaqueness of line
               Defaults to 1.

        Output:
        plot_panel_num_scatter(): None, but adds a scatterplot to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_ax.plot(x_obs, y_obs, linestyle = "None", marker = scatter_type, color = scatter_color, markersize = scatter_size, alpha = alpha)
        return(None)


    def plot_panel_num_barstack(self, panel_alias, x_obs, y_obs, edge_color_list = None, face_color_list = None,
                                hatch_list = None, alpha_list = None, line_width_list = None, bar_width = None, bar_width_coef = 1.0):
        '''Plots numerical-by-numeric series on the specified panel as a stacked barchart.
        Note that .ps files do not properly apply hatching for barcharts. Use another file format in these instances.

        Inputs:
        panel_alias: the panel alias for the chart to add a bar stack to.
        x_obs: iterable x-values to be plotted. These x-values specify the centers of the bars.
        y_obs: iterable holding sets of y-values (ie list of lists) to be plotted
               Every element of y_obs must have the same number of elements as x_obs.
        edge_color_list: list of str specifying what color to use for each bar's edges and hatching (if applicable)
                        Defaults to ["black"]*len(y_obs)
        face_color_list: list of str specifying what color to use for each bar's interior
                        Defaults to ["white"]*len(y_obs)
        hatch_list: list of str specifying hatching pattern for each bar
                    Common choices include "" for no hatching, "/", "\", "x", and "+".
                    Hatching can be intensfied through repetition (ie "///" has denser hatching than "/" and "//")
                    Defaults to [""]*len(y_obs)
        alpha_list: list of int or float specifying opaqueness of associated object
                    Defaults to [1]*len(y_obs).
        line_width_list: list of float or int specifying width of bar edges in points
                         Defaults to [1]*len(y_obs).
        bar_width: float or int to use as width of the bars
                   Defaults to None, in which case this function will attempt to determine the proper width to use
        bar_width_coef: float or int to be applied to automatically determined bar widths as a coefficient when bar_width is not specified
                        Defaults to 1. Ignored if bar_width argument is specified

        Output:
        plot_panel_num_barstack(): None, but adds a bar stack to specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        if edge_color_list is None:
            edge_color_list = ["black"] * len(y_obs)
        if face_color_list is None:
            face_color_list = ["white"] * len(y_obs)
        if hatch_list is None:
            hatch_list = [""] * len(y_obs)
        if alpha_list is None:
            alpha_list = [1] * len(y_obs)
        if line_width_list is None:
            line_width_list = [1] * len(y_obs)
        
        if bar_width is None:
            assert len(x_obs) > 1, "bar_width argument must be specified if the series to be plotted as bars only have 1 observation."
            bar_width = min([x_obs[j] - x_obs[j - 1] for j in range(1, len(x_obs))]) * bar_width_coef
        
        # bottom_list holds information for where each bar should start vertically
        # bottom_list[0] ([1]) holds running tally of all positive (negative) values already plotted
        # bottom_list[2] is updated with vertical starting positions for each bar of each series. It is reset from scratch for each series.
        bottom_list = [[0] * len(x_obs), [0] * len(x_obs), [0] * len(x_obs)]
        
        for ser_num in range(len(y_obs)):
            for ind in range(len(x_obs)):
                if y_obs[ser_num][ind] >= 0:
                    bottom_list[2][ind] = bottom_list[0][ind]
                    bottom_list[0][ind] += y_obs[ser_num][ind]
                else:
                    bottom_list[2][ind] = bottom_list[1][ind]
                    bottom_list[1][ind] += y_obs[ser_num][ind]
            curr_ax.bar(x_obs, y_obs[ser_num], width = bar_width, linewidth = line_width_list[ser_num], edgecolor = edge_color_list[ser_num], 
                        facecolor = face_color_list[ser_num], hatch = hatch_list[ser_num], alpha = alpha_list[ser_num], bottom = bottom_list[2])
        return(None)


    def format_panel_numaxis(self, panel_alias, axis = 1, num_range = None, tick_pos = None, skip_ticks = None, invert = False, color = "black", minor_length = 3.5, minor_width = 1, 
                             major_at_end = None, major_length = 7, major_width = 1.3, add_minor_labels = True, add_major_label = True, label_skip = 1, label_fmt = '{:g}', label_xoffset = None, label_yoffset = None, font_size = 10,
                             side_list = None):
        '''Formats numerical axis by fixing scale and adding ticks and tick labels.

        Inputs:
        panel_alias: the panel alias for the chart to be affected.
        axis: int specifying which axis should be the numerical axis
              Defaults to 1 (vertical axis), which is what should be used for vertical bar charts. If making a horizontal bar chart, 0 (horizontal axis) should be used instead.
        num_range: list or tuple of 2 floats or ints specifying lower and upper bound of axis scale
                   Defaults to bounds automatically determined by matplotlib
        tick_pos: list, tuple, or generator of ints or floats specifying axis values where ticks should be placed.
                  Defaults to set of tick positions automatically determined by matplotlib
        skip_ticks: list of coordinates from tick_pos where ticks should not be drawn
                    If an element is in tick_pos and this list, a label will still be placed at that element.
                    Defaults to [0] if axis = 1 to avoid ticks coinciding with a 0-line, especially in the case of non-black ticks.
                    Otherwise, defaults to [].
        invert: Boolean indicating whether the vertical axis should be inverted. Inverted axes are typically used only for forex charts.
                Defaults to False. Inverted horizontal axes are heavily discouraged.
        color: str specifying color to use for vertical axis, ticks, and labels
               Defaults to "black"
        minor_length: float specifying length of minor ticks in points
                      Defaults to 3.5
        minor_width: float specifying width of minor ticks in points
                     Defaults to 1
        major_at_end: Boolean indicating whether end of numerical axis should be marked with a major tick
                      Defaults to True if axis = 1 and to False otherwise
        major_length: float specifying length of major tick in points
                      Defaults to 7
        major_width: float specifying width of major tick in points
                     Defaults to 1.3
        add_minor_labels: Boolean indicating whether labels should be added at minor-tick positions
                          Defaults to True
        add_major_labels: Boolean indicating whether labels should be added at the major-tick position
                          Defaults to True. Only relevant if major_at_end = True.
        label_skip: positive int indicating how many ticks should come between labels
                    Defaults to 1 (every tick has a label). The first tick is always labeled.
        label_fmt: str specifying number format to use when printing tick labels
                   https://mkaz.blog/code/python-string-format-cookbook/ is a good resource for options
                   Defaults to "{:g}", which omits trailing 0's that come after the decimal point (ie 1.40 becomes 1.4)
        label_xoffset: float specifying adjustment in fixed-axis units of label position relative to x-axis from what this functions calculates as the strict center
                       Defaults to .02 if axis = 1 and to 0 otherwise.
        label_yoffset: float specifying adjustment in fixed-axis units of label position relative to y-axis from what this functions calculates as the strict center
                       Defaults to .02 if axis = 1 and to .07 otherwise.
        font_size: int specifying fontsize to use for tick labels
                   Defaults to 10
        side_list: list of str specifying which sides should be affected.
                   Defaults to ["right", "left"] if axis = 1 and to ["bottom"] if axis = 0 (excludes "top"). 
                   If a two-element list is provided, adds ticks to both sides but labels only the primary side ("right" for the y-axis, "bottom" for the x-axis).

        Output:
        format_panel_numaxis(): None, but formats numerical axis/axes as described for the specified panel in-place.
        ''' 

        curr_ax = self.panel_dict[panel_alias]
        if axis == 1:
            if label_xoffset is None:
                label_xoffset = .02
            if label_yoffset is None:
                label_yoffset = .02
            if major_at_end is None:
                major_at_end = True

            if side_list is None:
                side_list = ["right", "left"]
            side_dict = {"right": [1 + label_xoffset, "left"],
                         "left": [-label_xoffset, "right"]}
            
            if num_range is None:
                num_range = curr_ax.get_ylim()
            if tick_pos is None:
                tick_pos = list(curr_ax.get_yticks())
            else:
                tick_pos = list(tick_pos) #Make sure this is a list object so remove() method is available
            curr_ax.set_ylim(num_range)
            
            if skip_ticks is None:
                skip_ticks = [0] #Don't want tick coinciding with a 0-line
            
            if invert:
                curr_ax.invert_yaxis()
                actual_tick_pos = copy.deepcopy(tick_pos) #Don't want tick coinciding with x-axis
                try:
                    actual_tick_pos.remove(num_range[1])
                except:
                    pass
                major_pos = [num_range[0]]
            else:
                label_yoffset = -label_yoffset
                actual_tick_pos = copy.deepcopy(tick_pos)
                try:
                    actual_tick_pos.remove(num_range[0]) #Don't want tick coinciding with x-axis
                except:
                    pass
                major_pos = [num_range[1]]
            
            actual_tick_pos = [x for x in actual_tick_pos if x not in skip_ticks]
                
            curr_ax.tick_params(axis = 'y', which = 'both', right = ("right" in side_list), left = ("left" in side_list), color = color)
            curr_ax.tick_params(axis = 'y', which = 'major', length = major_length, width = major_width)
            curr_ax.tick_params(axis = 'y', which = 'minor', length = minor_length, width = minor_width)
            curr_ax.yaxis.set_minor_locator(ticker.FixedLocator(actual_tick_pos))
            for side in side_list:
                curr_ax.spines[side].set_color(color)
                for i in range(len(tick_pos)):
                    if ((i % label_skip) == 0) and (tick_pos[i] != major_pos or not major_at_end):
                        if add_minor_labels and not (len(side_list) == 2 and side == "left"):
                            curr_ax.text(side_dict[side][0], data2fixed(tick_pos[i] + (label_yoffset * (num_range[1] - num_range[0])), curr_ax, 1), 
                                         label_fmt.format(tick_pos[i]), horizontalalignment = side_dict[side][1], color = color, 
                                         fontproperties = self.font_dict['normal'], fontsize = font_size, transform = curr_ax.transAxes)
                if major_at_end:
                    curr_ax.yaxis.set_major_locator(ticker.FixedLocator(major_pos))
                    if ((major_pos in tick_pos and (i % label_skip) == 0) or (major_pos not in tick_pos and ((i + 1) % label_skip) == 0)) and add_major_label and not (len(side_list) == 2 and side == "left"):
                        curr_ax.text(side_dict[side][0], data2fixed(major_pos[0] + (label_yoffset * (num_range[1] - num_range[0])), curr_ax, 1), 
                                     label_fmt.format(major_pos[0]), horizontalalignment = side_dict[side][1], color = color, 
                                     fontproperties = self.font_dict['normal'], fontsize = font_size, transform = curr_ax.transAxes)
                else:
                    curr_ax.yaxis.set_major_locator(ticker.NullLocator())
        else:
            if label_xoffset is None:
                label_xoffset = 0
            if label_yoffset is None:
                label_yoffset = .05
            if major_at_end is None:
                major_at_end = False

            if side_list is None:
                side_list = ["bottom"]
            side_dict = {"bottom": [-label_yoffset, "top"],
                         "top": [1 + label_yoffset, "bottom"]}
            
            if num_range is None:
                num_range = curr_ax.get_xlim()
            if tick_pos is None:
                tick_pos = list(curr_ax.get_xticks())
            else:
                tick_pos = list(tick_pos) #Make sure this is a list object so remove() method is available
            curr_ax.set_xlim(num_range)
            
            if skip_ticks is None:
                skip_ticks = []
            
            if invert:
                curr_ax.invert_xaxis()
                label_xoffset = -label_xoffset
                actual_tick_pos = copy.deepcopy(tick_pos) #Don't want tick coinciding with y-axis
                try:
                    actual_tick_pos.remove(num_range[1])
                except:
                    pass
                major_pos = [num_range[0]]
            else:
                actual_tick_pos = copy.deepcopy(tick_pos) #Don't want tick coinciding with y-axis
                try:
                    actual_tick_pos.remove(num_range[0])
                except:
                    pass
                major_pos = [num_range[1]]
            
            actual_tick_pos = [x for x in actual_tick_pos if x not in skip_ticks]
                
            curr_ax.tick_params(axis = 'x', which = 'both', bottom = ("bottom" in side_list), top = ("top" in side_list), color = color)
            curr_ax.tick_params(axis = 'x', which = 'major', length = major_length, width = major_width)
            curr_ax.tick_params(axis = 'x', which = 'minor', length = minor_length, width = minor_width)
            curr_ax.xaxis.set_minor_locator(ticker.FixedLocator(actual_tick_pos))
            for side in side_list:
                curr_ax.spines[side].set_color(color)
                for i in range(len(tick_pos)):
                    if (i % label_skip == 0) and (tick_pos[i] != major_pos or not major_at_end):
                        if add_minor_labels and not (len(side_list) == 2 and side == "top"):
                            curr_ax.text(data2fixed(tick_pos[i] + (label_xoffset * (num_range[1] - num_range[0])), curr_ax, 0), side_dict[side][0],
                                         label_fmt.format(tick_pos[i]), horizontalalignment = "center", verticalalignment = side_dict[side][1], color = color, 
                                         fontproperties = self.font_dict['normal'], fontsize = font_size, transform = curr_ax.transAxes)
                if major_at_end:
                    curr_ax.xaxis.set_major_locator(ticker.FixedLocator(major_pos))
                    if ((major_pos in tick_pos and (i % label_skip) == 0) or (major_pos not in tick_pos and ((i + 1) % label_skip) == 0)) and add_major_label and not (len(side_list) == 2 and side == "top"):
                        curr_ax.text(data2fixed(major_pos[0] + (label_xoffset * (num_range[1] - num_range[0])), curr_ax, 0), side_dict[side][0],
                                     label_fmt.format(major_pos[0]), horizontalalignment = "center", verticalalignment = side_dict[side][1], color = color, 
                                     fontproperties = self.font_dict['normal'], fontsize = font_size, transform = curr_ax.transAxes)
                else:
                    curr_ax.xaxis.set_major_locator(ticker.NullLocator())
        return(None)


    def format_panel_ts_xaxis(self, panel_alias, minor_pos = None, major_pos = None, mark_years = False, label_dates = None, color = "black", 
                              minor_length = 3.5, minor_width = 1, major_length = 7, major_width = 1.3, label_fmt = None, irregular_month_fmt = False,
                              center_labels = True, tick_based_label_centering = True, label_dates_freqs = None, infer_freq_from_fmt = True,
                              label_xoffset = 0, label_yoffset = .07, font_size = 10):
        '''Adds ticks and date labels to horizontal axis of specified time-series panel. 
        By default, date labels are centered between the first and last tick positions relevant for the time period (the bounds of the x-axis are treated as additional tick positions for this purpose).
        Users can instead center ticks based on the numerical date values that appear on the x-axis (ie not limited to tick positions).
        The tick-based centering is the default in order to address strange situations that can arise when a label should go between an x-axis tick and the right end of a chart.

        The gen_ts_tick_label_range is a convenient way for generating lists to use for the minor_pos, major_pos, and label_dates arguments.
        However, that function always returns a "regular" date range (ie annual, monthly, monthly but skipping every other month, etc), but these arguments can accept arbitrary lists of pd.Timestamps, so long as they all have accurate freq attributes.

        Inputs:
        panel_alias: the panel alias for the chart to be affected
        minor_pos: list of date objects (or their numeric equivalents) where minor ticks should be placed
        major_pos: list of date objects (or their numeric equivalents) where major ticks should be placed
        mark_years: Boolean indicating whether major ticks should be placed at the beginning of each year in the x-axis range.
                    Defaults to False. Is ignored when major_pos != None.
        label_dates: list of pd.Timestamp objects where date labels should be placed
        color: str specifying color to use for x-axis, ticks, and labels
               Defaults to "black"
        minor_length: float specifying length of minor ticks in points
                      Defaults to 3.5
        minor_width: float specifying width of minor ticks in points
                     Defaults to 1
        major_length: float specifying length of major ticks in points
                      Defaults to 7
        major_width: float specifying width of major ticks in points
                     Defaults to 1.3
        label_fmt: str specifying date format to use for printing labels
                   Must be specified if label_dates != None
                   Common choices are "%Y" for 4-digit year and "%b" for 3-letter month. 
                   See https://stackabuse.com/how-to-format-dates-in-python/ for additional options.
        irregular_month_fmt: boolean indicating whether the date labels should be formatted using irregular month abbreviations (3-letters and a period, except for May, June, July, and Sept.)
                             Defaults to False, in which case label_fmt is used. Otherwise, this special format will take precendence over whatever label_fmt is.
        center_labels: Boolean indicating whether labels should be centered above the x-axis region relevant to it
                       Defaults to True
        tick_based_label_centering: Boolean indicating label centering regime
                                    Defaults to True, in which case labels are placed between the first and last ticks associated with the relevant time period.
                                    If False, labels are placed between minimum and maximum x-axis values associated with the relevant timestamp.
                                    The tick-based behavior is the default in order to address strange situations when the last x-axis label goes between a tick mark and the right end of the axis.
        label_dates_freqs: List of str indicating the intended freq of each element of label dates. This argument was added to help deal with the removal of pd.Timestamps' freq attribute.
                           Expected to be an element of ["S", "MIN", "H", "D", "B", "W", "M", "Q", "A", "Y"] (not case-sensitive).
                           If the provided list is only 1 element long, all label_dates are assumed to share this freq. Otherwise, the list provided should be the same length as label_dates.
                           Defaults to None, in which case the function tries to infer the freqs by first checking for freq attributes in label_dates, then based on the label format if infer_freq_from_fmt (explained below) is True, and then finally by using pd.infer_freq.
        infer_freq_from_fmt: Boolean indicating whether the function should infer label_dates' elements' frequencies (for centering purposes) based on label_fmt or irregulat_month_fmt (as in %Y would imply annual)
                             This argument is ignored if label_dates_freqs is specified or label_dates' elements already provide a freq parameter to read
                             Defaults to True, in which case the function will decide label frequency based on the chosen label format.
        label_xoffset: float specifying adjustment in fixed-axis units to horizontal position of labels from what this functions calculates as the strict center
                       Defaults to 0 (ie assumes no error)
        label_yoffset: float specifying vertical distance of date labels from horizontal axis in fixed-axis units
                       Defaults to .07
        font_size: float specifying fontsize for labels
                   Defaults to 10

        Output:
        format_panel_ts_xaxis(): None, but formats horizontal axis of specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        curr_ax.spines['bottom'].set_color(color)
        curr_ax.tick_params(axis = 'x', which = 'minor', length = minor_length, width = minor_width, color = color)
        curr_ax.tick_params(axis = 'x', which = 'major', length = major_length, width = major_width, color = color)
        if minor_pos is not None:
            curr_ax.xaxis.set_minor_locator(ticker.FixedLocator(list(mdates.date2num(minor_pos))))
        else:
            curr_ax.tick_params(axis = 'x', which = 'minor', bottom = False)
            minor_pos = []
        if major_pos is not None:
            curr_ax.xaxis.set_major_locator(ticker.FixedLocator(list(mdates.date2num(major_pos))))
        elif mark_years:
            major_pos = gen_ts_tick_label_range(mdates.num2date(curr_ax.get_xlim()[0]), mdates.num2date(curr_ax.get_xlim()[1]), "Y")
            curr_ax.xaxis.set_major_locator(ticker.FixedLocator(list(mdates.date2num(major_pos))))
        else:
            curr_ax.tick_params(axis = 'x', which = 'major', bottom = False)
            major_pos = []
        if label_dates is not None:
            if label_fmt is None and not irregular_month_fmt:
                print("label_fmt must be specified or irregular_month_fmt set to True if label_dates argument is provided.")
                return(None)
            else:
                if label_dates_freqs is None:
                    redo = False
                    if min([hasattr(x, "freq") for x in label_dates]):
                        label_dates_freqs = [x.freq for x in label_dates]
                        if None in label_dates_freqs:
                            redo = True

                    if label_dates_freqs is None or redo:
                        if infer_freq_from_fmt:
                            if irregular_month_fmt:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "M").freq] * len(label_dates)
                            elif label_fmt.find("%S") > -1:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "s").freq] * len(label_dates)
                            elif label_fmt.find("%M") > -1:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "min").freq] * len(label_dates)
                            elif label_fmt.find("%H") > -1:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "h").freq] * len(label_dates)
                            elif label_fmt.find("%d") > -1:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "D").freq] * len(label_dates)
                            elif max([label_fmt.find("%m"), label_fmt.find("%b"), label_fmt.find("%B")]) > -1:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "M").freq] * len(label_dates)
                            else:
                                label_dates_freqs = [pd.Period("1970-01-01", freq = "Y").freq] * len(label_dates)
                            
                        else:
                            assert len(label_dates) >= 3, "label_dates does not have stored freq information and is too short for pd.infer_freq(), so you must specify a freq using label_dates_freqs or infer_freq_from_fmt. See docstring for details."
                            label_dates_freqs = [pd.infer_freq(label_dates)] * len(label_dates)
                else:
                    assert len(label_dates_freqs) in [1, len(label_dates)], "label_dates_freqs must be either one-element long or the same length as label_dates."
                    if len(label_dates_freqs) != len(label_dates):
                        label_dates_freqs = label_dates_freqs * len(label_dates)
                    label_dates_freq_dict = {x: x.upper() for x in ["s", "min", "h", "d", "b", "w", "m", "q", "a", "y"]}
                    label_dates_freq_dict["a"] = "Y"
                    for x in ["s", "min", "h"]:
                        label_dates_freq_dict[x] = x
                    label_dates_freqs = [pd.Period("1970-01-01", freq = label_dates_freq_dict[x.lower()]).freq for x in label_dates_freqs]
                
                #Need to create an instance of a high-frequency object relative to the dates to be labeled 
                if max([str(label_dates_freqs[0]).find("Sec"), str(label_dates_freqs[0]).find("Min")]) > -1:
                    dummy_range = pd.date_range("1970-01-01 00:00:00", "1970-12-31 23:59:59", freq = "s")
                elif str(label_dates_freqs[0]).find("Hour") > -1:
                    dummy_range = pd.date_range("1970-01-01 00:00:00", "1970-12-31 23:59:59", freq = "min")
                elif str(label_dates_freqs[0]).find("Day") > -1:
                    dummy_range = pd.date_range("1970-01-01 00:00:00", "1970-12-31 23:59:59", freq = "h")
                else:
                    dummy_range = pd.date_range("1970-01-01 00:00:00", "1970-12-31 23:59:59", freq = "D")
                
                #sig_xpos is only relevant if tick_based_label_centering == True
                sig_xpos = list(mdates.date2num(minor_pos)) + list(mdates.date2num(major_pos))
                sig_xpos.append(curr_ax.get_xlim()[0])
                sig_xpos.append(curr_ax.get_xlim()[1])

                xlabel_pos = []
                for ind in range(len(label_dates)):
                    #Need to manually construct true next period to avoid trouble from skip argument
                    current_date_freq = str(label_dates_freqs[ind])[re.search(r'[a-zA-Z]', str(label_dates_freqs[ind])).start()]
                    if current_date_freq in ["S", "H"]:
                        current_date_freq = current_date_freq.lower()
                    elif str(label_dates_freqs[ind]).lower().find("min") > -1:
                        current_date_freq = "min"
                    
                    tmp_date = pd.Timestamp(str(label_dates[ind]))
                    tmp_period = pd.Period(str(label_dates[ind]), freq = current_date_freq)
                    next_period_number = mdates.date2num(tmp_date + 1 * tmp_period.freq + 1 * dummy_range.freq)
                    if not center_labels:
                        min_mark = mdates.date2num(label_dates[ind])
                        max_mark = mdates.date2num(label_dates[ind])
                    elif tick_based_label_centering:
                        min_mark = min([x for x in sig_xpos if x >= mdates.date2num(label_dates[ind])]) 
                        max_mark = max([x for x in sig_xpos if x <= next_period_number])
                        #Dealing with unusual circumstance that can arise when label needs to be placed between a tick and end of the x-axis
                        if max_mark == min_mark:
                            max_mark = curr_ax.get_xlim()[1]
                    else:
                        min_mark = max([curr_ax.get_xlim()[0], mdates.date2num(label_dates[ind])])
                        max_mark = min([curr_ax.get_xlim()[1], next_period_number])
                    xlabel_pos.append((min_mark + max_mark)/2)
                    if irregular_month_fmt:
                        curr_ax.text(data2fixed(xlabel_pos[ind], curr_ax, 0) + label_xoffset, -label_yoffset, format_month_irregular(label_dates[ind]), 
                                     horizontalalignment = "center", color = color, fontproperties = self.font_dict["normal"], 
                                     fontsize = font_size, transform = curr_ax.transAxes)
                    else:
                        curr_ax.text(data2fixed(xlabel_pos[ind], curr_ax, 0) + label_xoffset, -label_yoffset, label_dates[ind].strftime(label_fmt), 
                                     horizontalalignment = "center", color = color, fontproperties = self.font_dict["normal"], 
                                     fontsize = font_size, transform = curr_ax.transAxes)
        return(None)


    def format_panel_cs_cataxis(self, panel_alias, label_list, axis = 0, limits = None, color = "black", tick_length = 3.5, tick_width = 1.3, 
                                label_catoffset = 0, label_numoffset = -.06, font_size = 10, horizontal_align = None, vertical_align = "center", rotation = 0):
        '''Sets tick and labels for the category axis of the specified cross-sectional data bar chart.
        Labels are centered between the two nearest tick marks. The ends of the given axis are treated as tick positions for this purpose.

        Inputs:
        panel_alias: the panel alias for the chart to be affected
        label_list: list of str specifying the labels to be printed to the graph
        axis: int specifying which axis should be the category axis
              Defaults to 0 (horizontal axis), which is what should be used for vertical bar charts. If making a horizontal bar chart, 1 (vertical axis) should be used instead.
        limits: 2-element tuple or list of ints or floats specifying numeric bounds of the category axis
                Defaults to [-.5, len(label_list) - .5]. Labels are placed at each integer within this range.
        color: str specifying color to use for axis, ticks, and labels
               Defaults to "black"
        tick_length: float specifying length of minor ticks in points
                      Defaults to 3.5
        tick_width: float specifying width of minor ticks in points
                     Defaults to 1.3
        label_catoffset: float specifying adjustment in fixed-axis units of label position relative to category axis from what this functions calculates as the strict center
                         Defaults to 0 (ie assumes no error)
        label_numoffset: float specifying position of labels relative to numerical axis in fixed-axis units
                         Defaults to -.06
        font_size: float specifying fontsize for labels
                   Defaults to 10
        horizontal_align: str specifying horizontal alignment. Can be "left", "center", or "right".
                          Defaults to "center" if axis == 0 and "right" otherwise
        vertical_align: str specifying vertical alignment. Can be "bottom", "center", or "top".
                        Defaults to "center"
        rotation: float or int specifying the rotation (in degrees) to be applied to the axis labels
                  Defaults to 0.

        Output:
        format_panel_cs_cataxis(): None, but formats category axis of specified panel in-place.
        '''

        curr_ax = self.panel_dict[panel_alias]
        tick_pos = [-.5 + inc for inc in range(1, len(label_list) + 1)]
        if limits is None:
            limits = [-.5, len(label_list) - .5]
        if axis == 0:
            if horizontal_align is None:
                horizontal_align = "center"
            
            curr_ax.spines["bottom"].set_color(color)
            curr_ax.tick_params(axis = 'x', which = 'both', top = False)
            curr_ax.tick_params(axis = 'x', which = 'minor', bottom = False)
            curr_ax.tick_params(axis = 'x', which = 'major', length = tick_length, width = tick_width, color = color, bottom = True)
            curr_ax.set_xlim(limits)
            curr_ax.xaxis.set_major_locator(ticker.FixedLocator(tick_pos))
            for ind in range(len(label_list)):
                curr_ax.text(data2fixed(ind, curr_ax, 0) + label_catoffset, label_numoffset, label_list[ind], 
                             color = color, fontproperties = self.font_dict["normal"], 
                             fontsize = font_size, transform = curr_ax.transAxes, ha = horizontal_align, va = vertical_align, rotation = rotation)
        else:
            if horizontal_align is None:
                horizontal_align = "right"
            curr_ax.spines["left"].set_color(color)
            curr_ax.tick_params(axis = 'y', which = 'both', right = False)
            curr_ax.tick_params(axis = 'y', which = 'minor', left = False)
            curr_ax.tick_params(axis = 'y', which = 'major', length = tick_length, width = tick_width, color = color, left = True)
            curr_ax.set_ylim(limits)
            curr_ax.yaxis.set_major_locator(ticker.FixedLocator(tick_pos))
            for ind in range(len(label_list)):
                curr_ax.text(label_numoffset, data2fixed(ind, curr_ax, 1) + label_catoffset, label_list[ind], 
                             color = color, fontproperties = self.font_dict["normal"], 
                             fontsize = font_size, transform = curr_ax.transAxes, ha = horizontal_align, va = vertical_align, rotation = rotation)
        return(None)
