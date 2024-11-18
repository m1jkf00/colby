# The purpose of this file has been taken over by sample_exhibits.py, so please refer to that script instead.

import sys
from colby import cb

### The following variables should be set according to individual users' file organization
normal_font_path = "texgyreheros.gyreheros-regular.otf"
bold_font_path = "texgyreheros.gyreheros-bold.otf"
italic_font_path = "texgyreheros.gyreheros-italic.otf"
bold_italic_font_path = "texgyreheros.gyreheros-bolditalic.otf"

exhibit = cb.Exhibit([3,2], normal_font = normal_font_path, bold_font = bold_font_path, 
                     italic_font = italic_font_path, bold_italic_font = bold_italic_font_path)
exhibit.add_panel_nonts(1, 0, 0)
exhibit.plot_panel_cs_pie(1, [.25, .5, .75, 1], ["red", "green", "blue", "orange"], label_list = ["Red", "Green", "Blue", "Orange"], auto_pct = '%1.1f%%', radius = .7)
exhibit.add_panel_text(1, .05, .9, "Title", scale = "fixed")
exhibit.save_exhibit("pie_chart.pdf")