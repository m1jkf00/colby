import sys
import os
import pandas as pd
from datetime import datetime
from colby import cb

### The following variables should be set according to individual users' file organization
normal_font_path = "texgyreheros.gyreheros-regular.otf"
bold_font_path = "texgyreheros.gyreheros-bold.otf"
italic_font_path = "texgyreheros.gyreheros-italic.otf"
bold_italic_font_path = "texgyreheros.gyreheros-bolditalic.otf"

first_exhibit = cb.Exhibit([3,2], normal_font = normal_font_path, bold_font = bold_font_path, 
                     italic_font = italic_font_path, bold_italic_font = bold_italic_font_path, h_space = .4) #h_space argument adds vertical space between charts to make room for footnotes
first_exhibit.add_exhibit_title("First Taste")
first_exhibit.add_exhibit_captions("Left Caption", datetime.today().strftime("%Y-%m-%d %H:%M"))
first_exhibit.add_exhibit_text(.05, .05, "Arbitrary figtext position")

q_index = pd.date_range("2015-01-01", "2020-12-31", freq = "QE")
m_index = pd.date_range("2019-01-01", "2020-09-25", freq = "ME")
b_index = pd.date_range("2018-01-01", "2020-09-25", freq = "B")
d_index = pd.date_range("2017-09-01", "2020-09-25", freq = "D")

ser1 = pd.Series(range(len(q_index)), index = q_index)
ser2 = pd.Series(range(len(m_index)), index = m_index)
ser3 = pd.Series(range(-len(q_index), 0), index = q_index)
ser4 = pd.Series(range(-len(m_index), 0), index = m_index)
ser5 = pd.Series(range(len(q_index), 0, -1), index = q_index)
ser6 = pd.Series(range(len(m_index), 0, -1), index = m_index)

#Panel 0
curr_panel = 0
first_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 0, 0)
first_exhibit.add_panel_title(curr_panel, "Dummy plot 1")
first_exhibit.add_panel_captions(curr_panel, "Gratuitous left caption", "Dummy units 1")

first_exhibit.plot_panel_ts_line(curr_panel, ser2)
first_exhibit.plot_panel_ts_line(curr_panel, ser4, line_color = "dodgerblue", line_style = "--")
first_exhibit.plot_panel_ts_line(curr_panel, ser6, line_color = "firebrick", line_style = "-.")

first_exhibit.format_panel_numaxis(curr_panel, num_range = [-25, 25], tick_pos = range(-25, 30, 5))
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                    label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_dates_freqs = ["A"])

first_exhibit.add_panel_keylines(curr_panel, "2019-11-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"], style_list = ["-", "--"])
first_exhibit.add_panel_text(curr_panel, "2020-02-01", 8, "Firebrick $line$", color = "firebrick")
first_exhibit.add_panel_text(curr_panel, .1, .33, "Fixed position label", color = "black", scale = "fixed")

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_vline(curr_panel, pd.Timestamp("2020-09-15"), color = "forestgreen", line_style = "--")
first_exhibit.add_panel_shading(curr_panel, ["2020-09-27", "2020-12-31"], alpha = .3, face_color = "dodgerblue", edge_color = "dodgerblue")

#Panel 1
curr_panel += 1
first_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 0, 1)
first_exhibit.add_panel_sec_yaxis(curr_panel, f'{str(curr_panel)}_left')
first_exhibit.add_panel_title(curr_panel, "Dummy plot 2")
first_exhibit.add_panel_captions(curr_panel, "Dummy units 2 (inverted)", "Dummy units 1", left_color = "firebrick")
first_exhibit.add_panel_footnotes(curr_panel, ["$^{1}$ Footnote 1", "$^{2}$ Footnote 2"], y_pos = -.08)

first_exhibit.plot_panel_ts_scatter(curr_panel, ser2)
first_exhibit.plot_panel_ts_scatter(curr_panel, ser4, scatter_color = "dodgerblue")
first_exhibit.plot_panel_ts_scatter(f'{str(curr_panel)}_left', ser6, scatter_color = "firebrick")

first_exhibit.format_panel_numaxis(curr_panel, axis = 1, side_list = ["right"])
first_exhibit.format_panel_numaxis(f'{str(curr_panel)}_left', axis = 1, skip_ticks = [10], invert = True, side_list = ["left"], color = "firebrick")
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                    label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_keydots(curr_panel, "2020-03-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"])
first_exhibit.add_panel_text(curr_panel, "2020-06-01", 7, "Firebrick\n(left axis)", color = "firebrick")

first_exhibit.add_panel_arrow(curr_panel, ["2019-03-31", "2019-03-31"], [-10,-5], color = "firebrick")

#Panel 2
curr_panel += 1
first_exhibit.add_panel_ts(curr_panel, ["2016-11-01", "2021-02-28"], 1, 0)
first_exhibit.add_panel_title(curr_panel, "Dummy plot 3")
first_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

first_exhibit.plot_panel_ts_barstack(curr_panel, [ser1["2017":"2020"], ser3["2017":"2020"], ser5["2017":"2020"]], face_color_list = ["black", "dodgerblue", "firebrick"])

first_exhibit.format_panel_numaxis(curr_panel, axis = 1)
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2017-01-01", "2020-12-31", "Q"), mark_years = True,
                                 label_dates = cb.gen_ts_tick_label_range("2017-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_keyboxes(curr_panel, "2019-08-01", -10, ["Black", "Dodgerblue", "Firebrick"], face_color_list = ["black", "dodgerblue", "firebrick"])


#Panel 3
curr_panel += 1
first_exhibit.add_panel_ts(curr_panel, ["2016-11-01", "2021-02-28"], 1, 1)
first_exhibit.add_panel_title(curr_panel, "Dummy plot 4")
first_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

first_exhibit.plot_panel_ts_barstack(curr_panel, [ser1["2017":"2020"], ser3["2017":"2020"], ser5["2017":"2020"]], 
                                     face_color_list = ["black", "dodgerblue", "white"], edge_color_list = ["black", "black", "firebrick"], 
                                     hatch_list = ["", "", "//"])

first_exhibit.format_panel_numaxis(curr_panel, axis = 1)
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2017-01-01", "2020-12-31", "Q"), mark_years = True,
                                 label_dates = cb.gen_ts_tick_label_range("2017-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_keyboxes(curr_panel, "2019-08-01", -10, ["Black", "Dodgerblue", "Firebrick"], face_color_list = ["black", "dodgerblue", "white"], 
                                 edge_color_list = ["black", "black", "firebrick"], hatch_list = ["", "", "////"])


#Panel 4
curr_panel += 1
first_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 2, 0, v_end = 1)
first_exhibit.add_panel_title(curr_panel, "Dummy plot 5")
first_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

first_exhibit.plot_panel_ts_barstack(curr_panel, [ser1], number_stacks = 2, curr_stack = 1, face_color_list = ["black"], edge_color_list = ["black"], hatch_list = [""], bar_width_coef = .7)
first_exhibit.plot_panel_ts_barstack(curr_panel, [ser5], number_stacks = 2, curr_stack = 2, face_color_list = ["white"], edge_color_list = ["firebrick"], hatch_list = ["//"], bar_width_coef = .7, line_width_list = [.7], pos_adj = -3)

first_exhibit.format_panel_numaxis(curr_panel, axis = 1)
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                 label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_keyboxes(curr_panel, "2019-04-01", 23, ["Black"], face_color_list = ["black"], hatch_list = [""])
first_exhibit.add_panel_keyboxes(curr_panel, "2019-11-01", 23, ["Firebrick"], edge_color_list = ["firebrick"], hatch_list = ["////"])

#Panel 5
#Glitch found - chart includes numeric equivalent of a date as an x-axis label if no series is plotted (getting around by plotting blank line (linestyle = "None"))
curr_panel += 1
first_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 2, 1)
first_exhibit.add_panel_title(curr_panel, "Dummy plot 6")
first_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

first_exhibit.plot_panel_ts_line(curr_panel, ser2, line_style = "None")

first_exhibit.format_panel_numaxis(curr_panel, axis = 1, num_range = [-25, 25], tick_pos = range(-25, 30, 5))
first_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                    label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

first_exhibit.add_panel_hline(curr_panel, 0)
first_exhibit.add_panel_shading(curr_panel, ser4.index, ser4, ser6, alpha = .3, face_color = "grey", hatch = "")

first_exhibit.save_exhibit("tmp_page1.ps")
first_exhibit.save_exhibit("tmp_page1.pdf")

#Starting second exhibit
second_exhibit = cb.Exhibit([2,3], normal_font = normal_font_path, bold_font = bold_font_path, 
                     italic_font = italic_font_path, bold_italic_font = bold_italic_font_path, orientation = "landscape")
second_exhibit.add_exhibit_title("Sequel")
second_exhibit.add_exhibit_captions("Left Caption", datetime.today().strftime("%Y-%m-%d %H:%M"))

#Panel 0
curr_panel = 0
second_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 0, 0)
second_exhibit.add_panel_title(curr_panel, "Dummy plot 1")
second_exhibit.add_panel_captions(curr_panel, "Gratuitous left caption", "Dummy units 1")

second_exhibit.plot_panel_ts_line(curr_panel, ser2)
second_exhibit.plot_panel_ts_line(curr_panel, ser4, line_color = "dodgerblue", line_style = "--")
second_exhibit.plot_panel_ts_line(curr_panel, ser6, line_color = "firebrick", line_style = "-.")

second_exhibit.format_panel_numaxis(curr_panel, axis = 1, num_range = [-25, 25], tick_pos = range(-25, 30, 5))
second_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                 label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

second_exhibit.add_panel_keylines(curr_panel, "2019-11-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"], style_list = ["-", "--"])
second_exhibit.add_panel_text(curr_panel, "2020-02-01", 8, "Firebrick", color = "firebrick")
second_exhibit.add_panel_text(curr_panel, .07, .33, "Fixed position label", color = "black", scale = "fixed")

second_exhibit.add_panel_hline(curr_panel, 0)
second_exhibit.add_panel_vline(curr_panel, pd.Timestamp("2020-09-15"), color = "forestgreen", line_style = "--")
second_exhibit.add_panel_shading(curr_panel, ["2020-09-27", "2020-12-31"], alpha = .3, face_color = "dodgerblue")

#Panel 1
curr_panel += 1
second_exhibit.add_panel_ts(curr_panel, ["2014-10-01", "2021-02-28"], 0, 1, v_end = 3)
second_exhibit.add_panel_title(curr_panel, "Dummy plot 2")
second_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

second_exhibit.plot_panel_ts_barstack(curr_panel, [ser1, ser3, ser5], face_color_list = ["black", "dodgerblue", "firebrick"])

second_exhibit.format_panel_numaxis(curr_panel)
second_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2014-10-01", "2020-12-31", "Q"), mark_years = True,
                                 label_dates = cb.gen_ts_tick_label_range("2015-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

second_exhibit.add_panel_hline(curr_panel, 0)
second_exhibit.add_panel_keyboxes(curr_panel, "2019-01-01", -13, ["Black", "Dodgerblue", "Firebrick"], face_color_list = ["black", "dodgerblue", "firebrick"])

#Panel 2
curr_panel += 1
second_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 1, 0)
second_exhibit.add_panel_sec_yaxis(curr_panel, f'{str(curr_panel)}_left')
second_exhibit.add_panel_title(curr_panel, "Dummy plot 3")
second_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1", left_caption = "Dummy units 2 (inverted)", left_color = "firebrick")

second_exhibit.plot_panel_ts_scatter(curr_panel, ser2)
second_exhibit.plot_panel_ts_scatter(curr_panel, ser4, scatter_color = "dodgerblue")
second_exhibit.plot_panel_ts_scatter(f'{str(curr_panel)}_left', ser6, scatter_color = "firebrick")

second_exhibit.format_panel_numaxis(curr_panel, side_list = ["right"])
second_exhibit.format_panel_numaxis(f'{str(curr_panel)}_left', skip_ticks = [10], invert = True, side_list = ["left"], color = "firebrick")
second_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                 label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

second_exhibit.add_panel_hline(curr_panel, 0)
second_exhibit.add_panel_keydots(curr_panel, "2020-03-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"])
second_exhibit.add_panel_text(curr_panel, "2020-06-01", 7, "Firebrick\n(left axis)", color = "firebrick")

second_exhibit.add_panel_arrow(curr_panel, ["2019-03-31", "2019-03-31"], [-10,-5], color = "firebrick")

second_exhibit.save_exhibit("tmp_page2.ps")
second_exhibit.save_exhibit("tmp_page2.pdf")

#Starting exhibit 3 (table exhibit)
third_exhibit = cb.Exhibit([3,2], normal_font = normal_font_path, bold_font = bold_font_path, 
                     italic_font = italic_font_path, bold_italic_font = bold_italic_font_path, h_space = .4) #h_space argument adds vertical space between charts to make room for footnotes
third_exhibit.add_exhibit_title("Table Exhibit")
third_exhibit.add_exhibit_captions("Left Caption", datetime.today().strftime("%Y-%m-%d %H:%M"))

#Panel 0
curr_panel = 0
third_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 0, 0)
third_exhibit.add_panel_title(curr_panel, "Dummy plot 1")
third_exhibit.add_panel_captions(curr_panel, "Gratuitous left caption", "Dummy units 1")
third_exhibit.add_panel_footnotes(curr_panel, ["* Footnote 1", "** Footnote 2 has a  \n    break-line character in it"], y_pos = -.075)

third_exhibit.plot_panel_ts_line(curr_panel, ser2)
third_exhibit.plot_panel_ts_line(curr_panel, ser4, line_color = "dodgerblue", line_style = "--")
third_exhibit.plot_panel_ts_line(curr_panel, ser6, line_color = "firebrick", line_style = "-.")

third_exhibit.format_panel_numaxis(curr_panel, num_range = [-25, 25], tick_pos = range(-25, 30, 5))
third_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                    label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

third_exhibit.add_panel_keylines(curr_panel, "2019-11-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"], style_list = ["-", "--"])
third_exhibit.add_panel_text(curr_panel, "2020-02-01", 8, "Firebrick", color = "firebrick")
third_exhibit.add_panel_text(curr_panel, .1, .33, "Fixed position label", color = "black", scale = "fixed")

third_exhibit.add_panel_hline(curr_panel, 0)
third_exhibit.add_panel_vline(curr_panel, pd.Timestamp("2020-09-15"), color = "forestgreen", line_style = "--")
third_exhibit.add_panel_shading(curr_panel, ["2020-09-27", "2020-12-31"], alpha = .3, face_color = "dodgerblue")

#Panel 1
curr_panel += 1
third_exhibit.add_panel_ts(curr_panel, ["2019-01-01", "2020-12-31"], 0, 1)
third_exhibit.add_panel_sec_yaxis(curr_panel, f'{str(curr_panel)}_left')
third_exhibit.add_panel_title(curr_panel, "Dummy plot 2")
third_exhibit.add_panel_captions(curr_panel, "Dummy units 2 (inverted)", "Dummy units 1", left_color = "firebrick")
third_exhibit.add_panel_footnotes(curr_panel, ["$^1$ Footnote 1", "$^2$ Footnote 2"], y_pos = -.075)

third_exhibit.plot_panel_ts_scatter(curr_panel, ser2)
third_exhibit.plot_panel_ts_scatter(curr_panel, ser4, scatter_color = "dodgerblue")
third_exhibit.plot_panel_ts_scatter(f'{str(curr_panel)}_left', ser6, scatter_color = "firebrick")

third_exhibit.format_panel_numaxis(curr_panel, side_list = ["right"])
third_exhibit.format_panel_numaxis(f'{str(curr_panel)}_left', skip_ticks = [10], invert = True, side_list = ["left"], color = "firebrick")
third_exhibit.format_panel_ts_xaxis(curr_panel, minor_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "Q"), major_pos = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"),
                                 label_dates = cb.gen_ts_tick_label_range("2019-01-01", "2020-12-31", "A"), label_fmt = "%Y", label_yoffset = .07)

third_exhibit.add_panel_hline(curr_panel, 0)
third_exhibit.add_panel_keydots(curr_panel, "2020-03-01", -13, ["Black", "Dodgerblue"], color_list = ["black", "dodgerblue"])
third_exhibit.add_panel_text(curr_panel, "2020-06-01", 7, "Firebrick\n(left axis)", color = "firebrick")

third_exhibit.add_panel_arrow(curr_panel, ["2019-03-31", "2019-03-31"], [-10,-5], color = "firebrick")

#Panel 2
curr_panel += 1
cat1 = ["Row 1", "Row 2"]
cat2 = ["Row 1", "Row 2"]
row1_1 = [1, 2, 3, 4]
row2_1 = [5, 6, 7, 8]
row1_2 = [1, 2]
row2_2 = [3, 4]
#Placing text
third_exhibit.add_panel_table(curr_panel, 1, 0, h_end = 2, v_end = 2)
third_exhibit.add_panel_text(curr_panel, .5, .93, "Dummy Data", font_size = 13, font_style = "bold", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .20, .82, "Label", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .37, .82, "Row 1", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .5, .82, "Row 2", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .37, .72, "Col 1", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .50, .72, "Col 2", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .02, .65, "Label")
third_exhibit.add_panel_text(curr_panel, .20, .62, "Dummy method", horizontal_align = "center")
x_pos = .335
for period in ["Q1", "Q2", "Q1", "Q2"]:
    third_exhibit.add_panel_text(curr_panel, x_pos, .60, period, horizontal_align = "center")
    x_pos += .065

third_exhibit.add_panel_text(curr_panel, .02, .44, "China")
y_pos = .44
for cat in cat1:
    third_exhibit.add_panel_text(curr_panel, .28, y_pos, cat, horizontal_align = "right")
    y_pos += -.07

x_pos = .335
for ind in range(len(row1_1)):
    third_exhibit.add_panel_text(curr_panel, x_pos, .44, row1_1[ind], horizontal_align = "center")
    third_exhibit.add_panel_text(curr_panel, x_pos, .37, row2_1[ind], horizontal_align = "center")
    x_pos += .065

third_exhibit.add_panel_text(curr_panel, .64, .65, "Something")
third_exhibit.add_panel_text(curr_panel, .64, .44, "New")
third_exhibit.add_panel_text(curr_panel, .81, .62, "Another test", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .9325, .72, "Col 1", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .90, .60, "H1", horizontal_align = "center")
third_exhibit.add_panel_text(curr_panel, .965, .60, "H2", horizontal_align = "center")
y_pos = .44
for cat in cat2:
    third_exhibit.add_panel_text(curr_panel, .85, y_pos, cat, horizontal_align = "right")
    y_pos += -.07

x_pos = .9
for ind in range(len(row1_2)):
    third_exhibit.add_panel_text(curr_panel, x_pos, .44, row1_2[ind], horizontal_align = "center")
    third_exhibit.add_panel_text(curr_panel, x_pos, .37, row2_2[ind], horizontal_align = "center")
    x_pos += .065

third_exhibit.add_panel_text(curr_panel, 0, .20, "Note: The code for these tables is outdated. It is heavily suggested you construct tables using the cb.form_partition()\n          framework (see fifth page).", horizontal_align = "left")

#Table borders
third_exhibit.add_panel_hline(curr_panel, .82, 0, .56)
third_exhibit.add_panel_hline(curr_panel, .70, .305, .56)
third_exhibit.add_panel_hline(curr_panel, .55, 0, .56)

third_exhibit.add_panel_vline(curr_panel, 0, .55, .82)
third_exhibit.add_panel_vline(curr_panel, .305, .55, .82)
third_exhibit.add_panel_vline(curr_panel, .435, .55, .82)
third_exhibit.add_panel_vline(curr_panel, .56, .55, .82)


third_exhibit.add_panel_hline(curr_panel, .82, .62, .9925)
third_exhibit.add_panel_hline(curr_panel, .70, .87, .9925)
third_exhibit.add_panel_hline(curr_panel, .55, .62, .9925)

third_exhibit.add_panel_vline(curr_panel, .62, .55, .82)
third_exhibit.add_panel_vline(curr_panel, .87, .55, .82)
third_exhibit.add_panel_vline(curr_panel, .9925, .55, .82)

third_exhibit.add_panel_shading(curr_panel, [.305, .435], .35, .82, alpha = .3)

#Panel 3
curr_panel += 1
x_obs = [-1, 3, 5, 9]
yline_obs = [2*x for x in x_obs]
yscatter_obs = [-1.5, 10, 7, 7]

third_exhibit.add_panel_nonts(curr_panel, 2, 0)
third_exhibit.add_panel_title(curr_panel, "Dummy plot 3")
third_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

third_exhibit.plot_panel_num_line(curr_panel, x_obs, yline_obs)
third_exhibit.plot_panel_num_scatter(curr_panel, x_obs, yscatter_obs, scatter_color = "dodgerblue")

third_exhibit.format_panel_numaxis(curr_panel, axis = 1)
third_exhibit.format_panel_numaxis(curr_panel, axis = 0)

third_exhibit.add_panel_hline(curr_panel, 0)
third_exhibit.add_panel_keylines(curr_panel, -1, 18, ["Black"], color_list = ["black"])
third_exhibit.add_panel_keydots(curr_panel, -1, 15, ["Dodgerblue"], color_list = ["dodgerblue"])

third_exhibit.save_exhibit("tmp_page3.ps")
third_exhibit.save_exhibit("tmp_page3.pdf")


#Starting exhibit 4 (cross-section graphs)
fourth_exhibit = cb.Exhibit([3,2], normal_font = normal_font_path, bold_font = bold_font_path, 
                     italic_font = italic_font_path, bold_italic_font = bold_italic_font_path, h_space = .4) #h_space argument adds vertical space between charts to make room for footnotes
fourth_exhibit.add_exhibit_title("Cross-section Exhibit")
fourth_exhibit.add_exhibit_captions("Left Caption", datetime.today().strftime("%Y-%m-%d %H:%M"))

#Panel 0
curr_panel = 0
cat_obs = ["a", "b", "c", "d"]
y1 = [-1.5, 10, 7, 7]
y2 = [3, -1, 2, 0]

fourth_exhibit.add_panel_nonts(curr_panel, 0, 0)
fourth_exhibit.add_panel_title(curr_panel, "Dummy plot 1")
fourth_exhibit.add_panel_captions(curr_panel, right_caption = "Dummy units 1")

fourth_exhibit.plot_panel_cs_barstack(curr_panel, [y1, y2], bar_width_coef = .8, face_color_list = ["black", "dodgerblue"])
fourth_exhibit.plot_panel_cs_scatter(curr_panel, y2, bar_width_coef = .8, scatter_color = "firebrick")

fourth_exhibit.format_panel_numaxis(curr_panel, axis = 1)
fourth_exhibit.format_panel_cs_cataxis(curr_panel, cat_obs, axis = 0)

fourth_exhibit.add_panel_hline(curr_panel, 0)
# Repeating scatter line so that the hline does not camouflage one of the points
fourth_exhibit.plot_panel_cs_scatter(curr_panel, y2, bar_width_coef = .8, scatter_color = "firebrick")

fourth_exhibit.add_panel_keyboxes(curr_panel, -.2, 9, ["Black", "Blue"], face_color_list = ["black", "dodgerblue"])
fourth_exhibit.add_panel_keydots(curr_panel, -.15, 7, ["Red"], color_list = ["firebrick"])

fourth_exhibit.add_panel_footnotes(curr_panel, ["* Important to add 0-line before scatter to avoid camouflage."], y_pos = -.09)


#Panel 1
curr_panel += 1
fourth_exhibit.add_panel_nonts(curr_panel, 1, 0, invis_axis_list = ["right"])
fourth_exhibit.add_panel_title(curr_panel, "Dummy plot 2")
fourth_exhibit.add_panel_text(curr_panel, 4, -1.12, "Dummy units", horizontal_align = "center")

fourth_exhibit.plot_panel_cs_barstack(curr_panel, [y1], number_stacks = 2, curr_stack = 1, bar_width_coef = .8, face_color_list = ["black"], orientation = "horizontal")
fourth_exhibit.plot_panel_cs_barstack(curr_panel, [y2], number_stacks = 2, curr_stack = 2, bar_width_coef = .8, face_color_list = ["dodgerblue"], orientation = "horizontal")
fourth_exhibit.plot_panel_cs_scatter(curr_panel, y2, number_stacks = 2, curr_stack = 2, bar_width_coef = .8, scatter_color = "firebrick", orientation = "horizontal")

fourth_exhibit.format_panel_numaxis(curr_panel, axis = 0, side_list = ["bottom", "top"])
fourth_exhibit.format_panel_cs_cataxis(curr_panel, cat_obs, axis = 1)

fourth_exhibit.add_panel_vline(curr_panel, 0, line_style = "-")
fourth_exhibit.add_panel_keyboxes(curr_panel, 6, .35, ["Black", "Blue"], face_color_list = ["black", "dodgerblue"])
fourth_exhibit.add_panel_keydots(curr_panel, 6.4, -.13, ["Red"], color_list = ["firebrick"])

fourth_exhibit.add_panel_footnotes(curr_panel, ["* Separate top axis is possible.", "** Easy to keep right axis -> see code."], y_pos = -.17, y_delta = -.058)


#Panel 2
curr_panel += 1
fourth_exhibit.add_panel_table(curr_panel, 2, 0, v_end = 2)
fourth_exhibit.add_panel_text(curr_panel, .5, 1, "Faux Color Matrix", horizontal_align = "center", font_style = "bold", font_size = 14)

fourth_exhibit.add_panel_text(curr_panel, 0, .55, "Jul 2020", vertical_align = "center")
fourth_exhibit.add_panel_text(curr_panel, 0, .38, "Jan 2020", vertical_align = "center")

x_pos = .115
for lab in ["Canada", "France", "Germany", "Italy", "Japan", "Switzerland", "United\nKingdom",
            "Brazil", "China", "Hong Kong", "Korea", "Mexico", "Turkey"]:
    fourth_exhibit.add_panel_text(curr_panel, x_pos, .65, lab, rotation = 55)
    x_pos += .065 - .015 * (lab == "Switzerland") + .05 * (lab == "United\nKingdom")

color_list = (["orange", "dodgerblue", "red", "forestgreen", "purple"] * 6)[:-4]
color_dict = {"orange": "T", "dodgerblue": "C", "red": "H", "forestgreen": "N", "purple": "M"}

x_pos = .1
y_pos = .475
for ind in range(len(color_list)):
    fourth_exhibit.add_panel_shading(curr_panel, [x_pos, x_pos + .055], y_pos, y_pos + .15, face_color = color_list[ind], alpha = .3)
    fourth_exhibit.add_panel_text(curr_panel, x_pos + .055/2, y_pos + .15/2, color_dict[color_list[ind]], horizontal_align = "center", vertical_align = "center")
    x_pos += .065 + .035 * (ind in [6, 19]) - .88 * (ind == 12)
    y_pos += -.17 * (ind == 12)

fourth_exhibit.add_panel_text(curr_panel, .1, .155, "Key:", horizontal_align = "center", vertical_align = "center")

text_list = ["These", "Colors", "Have", "No", "Meaning"]
x_pos = .13
for ind in range(5):
    fourth_exhibit.add_panel_shading(curr_panel, [x_pos, x_pos + .157], .115, .195, face_color = color_list[ind], alpha = .3)
    fourth_exhibit.add_panel_text(curr_panel, x_pos + .157/2, .05, text_list[ind], horizontal_align = "center", vertical_align = "center")
    x_pos += .167

fourth_exhibit.add_panel_footnotes(curr_panel, ["The whimsical key is meant to emphasize this dummy table's lack of substance only.",
                                                "Note: The code for this table is outdated. It is heavily suggested you construct tables using the cb.form_partition()\n          framework (see fifth page)."])

fourth_exhibit.save_exhibit("tmp_page4.ps")
fourth_exhibit.save_exhibit("tmp_page4.pdf")

#Starting exhibit 5 (pie chart and form_partition() table)
fifth_exhibit = cb.Exhibit([3,2], normal_font = "texgyreheros.gyreheros-regular.otf", bold_font = "texgyreheros.gyreheros-bold.otf", 
                     italic_font = "texgyreheros.gyreheros-italic.otf", bold_italic_font = "texgyreheros.gyreheros-bolditalic.otf")
fifth_exhibit.add_exhibit_title("Final Exhibit")
fifth_exhibit.add_exhibit_captions("Left Caption", datetime.today().strftime("%Y-%m-%d %H:%M"))

#Panel 0
curr_panel = 0
fifth_exhibit.add_panel_nonts(curr_panel, 0, 0)
fifth_exhibit.plot_panel_cs_pie(curr_panel, [.25, .5, .75, 1], ["red", "green", "blue", "orange"], label_list = ["Red", "Green", "Blue", "Orange"], auto_pct = '%1.1f%%', radius = .7)
fifth_exhibit.add_panel_text(curr_panel, .05, .9, "Title", font_style = "bold", scale = "fixed")

# Panel 1
curr_panel += 1

table_ser_dict = {1: pd.Series([.5355, .2784, .3333], index = pd.period_range("2021-01-01", "2021-01-03", freq = "D")),
                  2: pd.Series([.6789, .9987, .4213], index = pd.period_range("2021-01-01", "2021-01-03", freq = "D"))}

fifth_exhibit.add_panel_table(curr_panel, 0, 1)
table_partition = cb.form_partition(h_start = .01, h_end = .99, v_start = .4, v_end = .95, nrow = 7, ncol = 3, relative_col_sizes = [1.2, 1, 1])

# Title
fifth_exhibit.add_panel_text(curr_panel, (table_partition["cols"][0] + table_partition["cols"][-1])/2, (table_partition["rows"][0] + table_partition["rows"][1])/2, 
                             "cb.form_partition() Table", font_style = "bold", horizontal_align = "center", vertical_align = "center")

# Column headers
series_names = ["Ser1", "Ser2"]
for ind in range(len(series_names)):
    fifth_exhibit.add_panel_text(curr_panel, (table_partition["cols"][ind + 1] + table_partition["cols"][ind + 2])/2, (table_partition["rows"][2] + table_partition["rows"][3])/2, 
                                 series_names[ind], horizontal_align = "center", vertical_align = "center")

# Row labels
for ind in range(len(table_ser_dict[1])):
    fifth_exhibit.add_panel_text(curr_panel, (table_partition["cols"][0] + table_partition["cols"][1])/2, (table_partition["rows"][3 + ind] + table_partition["rows"][4 + ind])/2,
                                 table_ser_dict[1].index[ind], horizontal_align = "center", vertical_align = "center")

# Populate body of table with data
for col_ind in table_ser_dict.keys():
    for row_ind in range(len(table_ser_dict[col_ind])):
        fifth_exhibit.add_panel_text(curr_panel, (table_partition["cols"][col_ind] + table_partition["cols"][col_ind + 1])/2, (table_partition["rows"][3 + row_ind] + table_partition["rows"][4 + row_ind])/2,
                                     '{:5.3f}'.format(table_ser_dict[col_ind].values[row_ind]), horizontal_align = "center", vertical_align = "center")

# Adding borders
for ind in [3, 6]:
    fifth_exhibit.add_panel_hline(curr_panel, table_partition["rows"][ind], table_partition["cols"][0], table_partition["cols"][-1])

for ind in [1]:
    fifth_exhibit.add_panel_vline(curr_panel, table_partition["cols"][ind], table_partition["rows"][3], table_partition["rows"][6])

# Footnote
fifth_exhibit.add_panel_text(curr_panel, (7 * table_partition["cols"][0] + table_partition["cols"][1])/8, (table_partition["rows"][-2] + table_partition["rows"][-1])/2,
                             "Note: This table was constructed using the\n          cb.form_partition() framework (recommended).", horizontal_align = "left", vertical_align = "top")

fifth_exhibit.save_exhibit("tmp_page5.ps")
fifth_exhibit.save_exhibit("tmp_page5.pdf")


cb.concat_pdf(["tmp_page1.pdf", "tmp_page2.pdf", "tmp_page3.pdf", "tmp_page4.pdf", "tmp_page5.pdf"], "sample_exhibits.pdf")

if sys.platform.startswith("win"):
    os.system("timeout 5")
    os.system("del tmp_page*pdf")
else:
    os.system("rm tmp_page*pdf")

cb.concat_ps(["tmp_page1.ps", "tmp_page2.ps", "tmp_page3.ps", "tmp_page4.ps", "tmp_page5.ps"], "ps_trial.ps")
os.system("ps2pdf ps_trial.ps")

if sys.platform.startswith("win"):
    os.system("timeout 5")
    os.system("del tmp_page*.ps")
    os.system("del ps_trial.ps")
else:
    os.system("rm tmp_page*.ps")
    os.system("rm ps_trial.ps")