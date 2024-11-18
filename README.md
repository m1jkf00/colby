# colby
Python module for line graphs, scatterplots, bar charts, tables, and pie charts.

Github repo: https://github.com/m1jkf00/colby

This package facilitates the construction of chartpackets (single- or multi-page long pdfs of charts or tables).
The code is built on top of matplotlib and imposes certain stylistic choices. See the examples folder.

2024-11-18 Update
Update was necessary to maintain functionality following the removal of freq from pandas Timestamps. 
See details below.

code/cb.py:
Updated latest Python and package versions used for testing

impose_ts_xrange()
Changed freq argument to unit

form_partition()
Corrected typo in docstring

center_ts_obs()
Added support for "y" freq shorthand and expanded acceptable freq str to include str versions of pd.period.freq
Conformed to new conventions for frequency shorthand (case-sensitivity and "Y" for annual)

concat_pdf() 
Switched to using PdfMerger

Exhibit.plot_panel_cs_pie()
Corrected default value for start_angle

Exhibit.gen_ts_tick_label_range()
Added dict to deal with "A" shorthand for annual being deprecated in favor of "Y"
Fixed capitalization for intraday frequencies with dict entries

Exhibit.plot_panel_ts_line()
Added code to check for presence of freq parameter in ser's index. If it's not there, it tries to use pd.infer_freq. 
Conformed to new conventions for frequency shorthand (case-sensitivity and "Y" for annual)

Exhibit.plot_panel_ts_scatter()
Added code to check for presence of freq parameter in ser's index. If it's not there, it tries to use pd.infer_freq. 
Conformed to new conventions for frequency shorthand (case-sensitivity and "Y" for annual)

Exhibit.plot_panel_ts_barstack()
Added code to check for presence of freq parameter in ser's index. If it's not there, it tries to use pd.infer_freq. 
Conformed to new conventions for frequency shorthand (case-sensitivity and "Y" for annual)

Exhibit.format_panel_ts_xaxis()
Switched dummy_date to dummy_range using pd.date_range to ensure freq attribute is available
Added optional label_dates_freqs and infer_freq_from_fmt (preferred) to help give more control over placement of labels
  If these arguments are not given, the function tries to infer frequencies from label_dates if possible
Conforms to new conventions for frequency shorthand (case-sensitivity and "Y" for annual))


examples/pie_chart.py
Corrected default for auto_pct parameter
Marked this file as obsolete since a pie chart has been added to sample_exhibits.py


examples/sample_exhibits.py
Adjusted panel aliases to be more convenient (recommended use)
Added use of label_date_freqs argument for Exhibit 1's panel 0 format_panel_ts_xaxis() call
Added footnotes to tables on pages 3 and 4 to mark their code as obsolete
Added fifth page featuring a pie chart and a table made with cb.form_partition() (recommended)