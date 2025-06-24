# File: azure_theme.py
# This file contains the Azure TTK theme for a modern dark look.
# Sourced from https://github.com/rdbende/Azure-ttk-theme

THEME_DATA = """
# Azure-ttk-theme
# Author: rdbende
# License: MIT license
# Version: 2.1.0

package require Tk 8.6

namespace eval ttk::theme::azure {
    variable colors
    array set colors {
        -bg           #ffffff
        -fg           #000000
        -primary      #0078d4
        -active       #005a9e
        -hover        #f0f0f0
        -indicator    #000000
        -disabled     #bebebe
        -inputfg      #000000
        -inputbg      #ffffff
        -border       #adadad
        -accent       #0078d4
        -selectbg     #0078d4
        -selectfg     #ffffff
        -treeheading  #f0f0f0
        -button       #f0f0f0
        -menucolor    #ffffff
    }
    proc LoadImages {dir} {}
    proc LoadTheme {} {
        variable colors
        ttk::style theme create azure -parent clam -settings {
            # Base style
            ttk::style configure . -background $colors(-bg) -foreground $colors(-fg) -bordercolor $colors(-border) -troughcolor $colors(-bg) -focuscolor $colors(-primary) -lightcolor $colors(-bg) -darkcolor $colors(-bg) -font {Segoe\ UI 10}
            
            # TButton
            ttk::style configure TButton -padding {10 5} -anchor center
            ttk::style map TButton -background [list disabled $colors(-button) hover #e5e5e5 active $colors(-active)] -foreground [list disabled $colors(-disabled) active $colors(-selectfg)]
            
            # TLabel
            ttk::style configure TLabel -padding 5

            # TEntry
            ttk::style configure TEntry -padding 5 -fieldbackground $colors(-inputbg)
            ttk::style map TEntry -fieldbackground [list !focus $colors(-inputbg) focus $colors(-inputbg)] -bordercolor [list !focus $colors(-border) focus $colors(-primary)] -lightcolor [list focus $colors(-primary)]

            # TCombobox
            ttk::style map TCombobox -fieldbackground [list !focus $colors(-inputbg) focus $colors(-inputbg)] -background [list !focus $colors(-button) focus $colors(-button) readonly $colors(-button)] -bordercolor [list !focus $colors(-border) focus $colors(-primary)] -lightcolor [list focus $colors(-primary)]
            
            # TSpinbox
            ttk::style map TSpinbox -fieldbackground [list !focus $colors(-inputbg) focus $colors(-inputbg)]
            
            # Treeview
            ttk::style configure Treeview -fieldbackground $colors(-inputbg)
            ttk::style map Treeview -background [list disabled $colors(-button) selected $colors(-selectbg)] -foreground [list disabled $colors(-disabled) selected $colors(-selectfg)]
            ttk::style configure Treeview.Heading -background $colors(-treeheading) -padding 5 -relief flat
            ttk::style map Treeview.Heading -background [list hover $colors(-hover)]
            
            # TNotebook
            ttk::style configure TNotebook.Tab -padding {10 5} -background $colors(-bg)
            ttk::style map TNotebook.Tab -background [list !selected $colors(-button) selected $colors(-bg)] -padding [list selected {10 5}]
            ttk::style configure TNotebook -tabposition n

            # TFrame
            ttk::style configure TFrame -background $colors(-bg)

            # TMenubutton
            ttk::style configure TMenubutton -padding {10 5} -background $colors(-button)

            # TCheckbutton
            ttk::style map TCheckbutton -indicatorcolor [list selected $colors(-primary) disabled $colors(-disabled)]
            
            # TRadiobutton
            ttk::style map TRadiobutton -indicatorcolor [list selected $colors(-primary) disabled $colors(-disabled)]
            
            # TScrollbar
            ttk::style configure TScrollbar -arrowsize 14
            ttk::style map TScrollbar -background [list !disabled $colors(-hover)] -troughcolor [list !disabled $colors(-button)] -arrowcolor [list !disabled $colors(-fg)]
            
            # TScale
            ttk::style configure TScale -sliderlength 20
            
            # TProgressbar
            ttk::style configure TProgressbar -background $colors(-primary)
        }
    }
}
namespace eval ttk::theme::azure-dark {
    variable colors
    array set colors {
        -bg           #1c1c1c
        -fg           #f0f0f0
        -primary      #0078d4
        -active       #434343
        -hover        #434343
        -indicator    #0a84ff
        -disabled     #434343
        -inputfg      #f0f0f0
        -inputbg      #323232
        -border       #434343
        -accent       #0a84ff
        -selectbg     #005a9e
        -selectfg     #f0f0f0
        -treeheading  #282828
        -button       #282828
        -menucolor    #323232
    }
    proc LoadImages {dir} {}
    proc LoadTheme {} {
        variable colors
        ttk::style theme create azure-dark -parent azure -settings {
            # Base style
            ttk::style configure . -background $colors(-bg) -foreground $colors(-fg) -bordercolor $colors(-border) -troughcolor $colors(-inputbg) -focuscolor $colors(-primary) -lightcolor $colors(-bg) -darkcolor $colors(-bg)
            
            # TButton
            ttk::style map TButton -background [list disabled $colors(-disabled) hover $colors(-hover) active $colors(-active)] -foreground [list disabled #7a7a7a]
            
            # TEntry
            ttk::style configure TEntry -fieldbackground $colors(-inputbg)
            ttk::style map TEntry -foreground [list disabled #7a7a7a]

            # TCombobox
            ttk::style map TCombobox -fieldbackground [list !focus $colors(-inputbg) focus $colors(-inputbg) readonly $colors(-inputbg)] -background [list !focus $colors(-button) focus $colors(-button) readonly $colors(-button)] -foreground [list disabled #7a7a7a]
            
            # TSpinbox
            ttk::style map TSpinbox -fieldbackground [list !focus $colors(-inputbg) focus $colors(-inputbg)] -foreground [list disabled #7a7a7a]

            # Treeview
            ttk::style configure Treeview -fieldbackground $colors(-inputbg)
            ttk::style map Treeview -background [list disabled $colors(-button) selected $colors(-selectbg)] -foreground [list disabled #7a7a7a]
            ttk::style configure Treeview.Heading -background $colors(-treeheading)
            ttk::style map Treeview.Heading -background [list hover $colors(-hover)]
            
            # TNotebook
            ttk::style configure TNotebook.Tab -background $colors(-bg)
            ttk::style map TNotebook.Tab -background [list !selected $colors(-button) selected $colors(-bg)]
            
            # TFrame
            ttk::style configure TFrame -background $colors(-bg)

            # TMenubutton
            ttk::style configure TMenubutton -background $colors(-button)
            
            # TCheckbutton
            ttk::style map TCheckbutton -indicatorcolor [list selected $colors(-indicator) disabled $colors(-disabled)] -foreground [list disabled #7a7a7a]
            
            # TRadiobutton
            ttk::style map TRadiobutton -indicatorcolor [list selected $colors(-indicator) disabled $colors(-disabled)] -foreground [list disabled #7a7a7a]
            
            # TScrollbar
            ttk::style map TScrollbar -background [list !disabled #434343] -troughcolor [list !disabled #323232] -arrowcolor [list !disabled #f0f0f0]
        }
    }
}
"""