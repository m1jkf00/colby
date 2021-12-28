import sys
import colby as cb

exhibit = cb.Exhibit([3,2], normal_font = "texgyreheros-regular.otf", bold_font = "texgyreheros-bold.otf", 
                     italic_font = "texgyreheros-italic.otf", bold_italic_font = "texgyreheros-bolditalic.otf")
exhibit.add_panel_nonts(1, 0, 0)
exhibit.plot_panel_cs_pie(1, [.25, .5, .75, 1], ["red", "green", "blue", "orange"], label_list = ["Red", "Green", "Blue", "Orange"], radius = .7)
exhibit.add_panel_text(1, .05, .9, "Title", scale = "fixed")
exhibit.save_exhibit("pie_chart.pdf")