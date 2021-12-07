#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@ Test Bed for Alpha Advantage
GUI Developed by Karen Fireman
Based on Code by Dr eJones and with his help

GUI asks user to select a STOCK by using "SpinBox"
Then Clicking on the PRICE Button
Then Can click on the Closing Price or the Volume or Narrative
 
Note - when you click on "Narrative" it provides the Company Overview as well as 
The 'Categories' and the 'Confidence' for each categories 
And puts those into a TEXTBOX

Key Notes:
Note0:
    KSF: Object Oriented Programming Notes:
        "self.variables...  are "SETTER & GETTER"... Therefore:
        to SET the value:  self.varName.set(____)  (put new value inside '()' )
        to GET the value:  self.varName.get()  (i.e. the parens are EMPTY)
        These vars are Automatically GLOBAL
        Each f() must have "self" as it's 1st variable AND
        When "calling the f()"   self must be a prefix e.g.
        to call a f() named KSF_stock   must say  self.KSF_stock()  
        And note that the "self" variable does NOT show up in the call !! 
Note1:
    in order to get the stock ticker to be USABLE !!
    from the SPINBOX - you must 
    go into the Stock f() and self.symbol.set(ticker)
    i.e.:   ticker = self.stock_selection.get()
    THUS: self.symbol.set(self.stock_selection.get())
Note2:
    GUI is finichy regarding the rows (and the columnspan must be SAME)
    e.g. when using the PLOT - the columnspan = SAME as for TEXTBOX
    ... otherwise PROBLEMS
    ALSO
    If you tell it ROW = 9
    BUT there was ONLY ROW = 4 before... it might butt-it-right up there
    YET if LATER you have ROW = 6 -- the order may get FUNKY... so
    USE THE SAME ROW = consistently across items going into same spaces
Note3:
    In order to OVERLAY the SpinBox ONTOP of the PICTURE, 
    Must put the Picture Image in FIRST
    THEN put in the SPINBOX, (i.e. it STACKS THEM from Bottom-> to Top)
    ... if you do it the other way - SpinBox is hidden underneath !!
Note4:
    Use padx=10 etc to slide the SpinBox over a little bit to line it up w PIC
Note5:
    VERY FINICKY:
    I had to use the HEIGHT=32  (NOT 60 !) for the TextBox
    b/c when I used 60, it would PUSH DOWN the Graph of Closing Price
    Note 18 worked nicely, HOWEVER, JNJ and MANT company descriptions were so 
    Long, that with only height=18, there was no room for the CAT & CONF
Note6:
    You need to  use the INSERT METHOD  i.e. self.t.insert(...) 
    TO GET THE TEXT TO GO INTO THE TEXT BOX !!!!!
    
    You also need to use the self.t.delete(...) 
    to ERASE the Text before you do the Graphs
Note7: 
    I'm aware that I could have used the index of the location of the 
    pointer in the TextBox to determine where to place the CAT+CONF, 
    but for me, it was so 
    EASY to just concatenate the pieces and then put them all in at once.
Dr Jones - I learned a lot from your helping me. Thank you very much, Karen
"""

import requests, json 
import pandas as pd
import numpy  as np
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning
#########################  OK to do it here ?

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import ImageTk, Image
###
import os, io, json, argparse, six

import google.auth
from   google.cloud import language_v1 as language
from   google.cloud import translate_v2 as translate
from   google.cloud import storage

class StockGUI:
    def __init__(self, guiWin, lang_dict, api_key, cred):
        self.guiWin_ = guiWin
        self.guiWin_.title("Monica & Juan Carlos & Karen's Stock Price API")
        self.guiWin_.geometry("1650x950+100+15")  ## 2100 replacing 100 will dual puts on 2nd screen;  100=here from left side //KSF Apr 2021 - make it bigger than 930x950
        self.api_key = api_key
        self.lang_dict = lang_dict
        self.credentials = cred
        
        # Declares root canvas is a grid of only one row and one column
        self.guiWin_.columnconfigure(0, weight=1)
        self.guiWin_.rowconfigure(0, weight=1)
        
        # Set styles for TK Label, Entry and Button Widgets
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial",  20),foreground='black')
        self.style.configure("TEntry", font=("Arial",  25),foreground='maroon')
        self.style.configure("TCheckbutton",font=("Arial", 20),
                             foreground='maroon')
        self.style.configure("TButton",font=("Arial",  20),foreground='maroon')
        
        # Create Frame inside GUI canvas
        self.mainframe = ttk.Frame(self.guiWin_, padding="15 15 15 15")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        
        # Add Label Widgets to mainframe
        ttk.Label(self.mainframe, text="Symbol").grid(column=1,row=1, sticky=W)
        ttk.Label(self.mainframe, text="Close Price (USD)"). \
                                              grid(column=1, row=2, sticky=W)
        ttk.Label(self.mainframe, text="Previous Close"). \
                                              grid(column=1, row=3, sticky=W)
        ttk.Label(self.mainframe, text="Percent Change"). \
                                              grid(column=1, row=4, sticky=W)
        ttk.Label(self.mainframe, text="Volume"). \
                                             grid(column=1, row=5, sticky=W) 
                                             
        ttk.Separator(self.mainframe, orient=HORIZONTAL).\
                               grid(column=1, row=7, columnspan=4, sticky="EW")
 
        ttk.Label(self.mainframe,text="Timing Selected"). \
                                              grid(column=1, row=8, sticky=W)
        
        self.imgwin = ttk.Label(self.mainframe, image=""). \
                        grid(column=1, row=9, columnspan=4, sticky=W)
        
        col2wdt = 8
        # Add Entry Widget for Entering the Stock Symbol
        self.symbol = StringVar()
        self.symbol_entry = ttk.Entry(self.mainframe, width=col2wdt,justify=CENTER,
                        textvariable=self.symbol, font=("Arial", 20, "bold"))
        self.symbol_entry.grid(column=2, row=1, sticky=(W, E))
        print("*** 134: SETUP ENTRY_WiDGEt for SYMBOL")                   
        # Add Entry Widget for Display of the Last Stock Close Price           
        self.close_price = StringVar()
        self.close_price_entry = ttk.Entry(self.mainframe, width=col2wdt, 
                    textvariable=self.close_price, justify=CENTER, font=("Arial", 20, "bold"))
        self.close_price_entry.grid(column=2, row=2, sticky=(W, E))
        
        # Add Entry Widget for Display of the Previous Stock Close Price
        self.p_close_price = StringVar()
        self.p_close_price_entry = ttk.Entry(self.mainframe, width=col2wdt, 
                    textvariable=self.p_close_price, justify=CENTER, font=("Arial", 20, "bold"))
        self.p_close_price_entry.grid(column=2, row=3, sticky=(W, E))
        
        # Add Entry Widget for Display of the Percent Change in Price
        self.change = StringVar()
        self.change_entry = ttk.Entry(self.mainframe, width=col2wdt, 
                    textvariable=self.change, justify=CENTER, font=("Arial", 20, "bold"))
        self.change_entry.grid(column=2, row=4, sticky=(W, E))
        
        # Add Entry Widget for Display of Trading Volume for Last Day
        self.vol = StringVar()
        self.vol_entry = ttk.Entry(self.mainframe, width=col2wdt, 
                    textvariable=self.vol, justify=CENTER, font=("Arial", 20, "bold"))
        self.vol_entry.grid(column=2, row=5, sticky=(W, E))

        # Add Button Widget for Calling stock_close() to Display Quote 
        ttk.Button(self.mainframe, text="Price", cursor="hand2", width=10,
                   command=self.stock_close).grid(column=2, row=6, sticky=W)
        
        ### KSF: Add TextBox Widget for storing the DESCRIPTION:
        # SETUP a textVar
        # Later use---  self.KSF_co_desc  ---to load the DESC into textVar
        ### remove ### self.textVar = StringVar()
        # ###############  I loaded the value below - line # 480 ############

        
        ####################################################################
        self.c = IntVar()
        self.c.set(0)
        self.c1 = ttk.Checkbutton(self.mainframe, text="Closing Price", 
                                  variable=self.c, command=self.plt_close, 
                                  onvalue=1, offvalue=0).\
                                  grid(column=3, row=8, sticky=W)
        self.v = IntVar()
        self.v.set(0)
        self.v1 = ttk.Checkbutton(self.mainframe, text="Volume", 
                                  variable=self.v, command=self.plt_vol, 
                                  onvalue=1, offvalue=0). \
                                  grid(column=4, row=8, sticky=W)
        self.narr = IntVar()
        self.narr.set(0)
        self.narr1 = ttk.Checkbutton(self.mainframe, text="Narrative", 
                                  variable=self.narr, command=self.DispNarr, 
                                  onvalue=1, offvalue=0). \
                                  grid(column=2, row=8, sticky=W)
                                  
        ##################### Create a FRAME "stock_frame" for the stocks ####                                    
        self.stock_frame = ttk.Frame(self.mainframe, padding=(5, 5, 5, 5),
                                      relief='sunken', borderwidth=5)
        self.stock_frame.grid(column=3, columnspan=2, row=1, rowspan=6, 
                                      sticky=(N, W, E, S))
        ###############################################################################


        ################################# add in image and button #####################
        #######  (Note - the "button ended up not needed, but I left it there
        #######  I had patterned it after the "BUTTON that was the Picture from the "TELLO Drone GUI)
        ######################################################################################
        # img_path      = "C:\TAMU\Semester 5\Fundamentals of Busness programing\Group project/" # Path to GUI images
        img_path      = "KSF_GUI_img/" # Path to GUI images
        newsize     = (480, 240)
        self.boat_img = Image.open(img_path+"Boat_Skiier.png")
        self.boat_img = self.boat_img.resize(newsize)
        self.boat_img = ImageTk.PhotoImage(self.boat_img)        
        self.boat_b   = Button(self.stock_frame, image=self.boat_img, 
                            cursor="hand2", command=self.stock_stat,
                            width=480, height=240)    ### needed to make gui image bigger
        self.boat_b.grid(column=1, row=1, rowspan=4)
        ##############################################################################
        #################################  TRY  SPIN BOX ####################################################
        ttk.Label(self.stock_frame, text="PICK A STOCK, then CLICK 'Price' Button").grid(column=1,row=0)
        stocktickers=("IBM", "AAPL", "JNJ", 'AZN', "GS", "MSFT", "NFLX", "GE", "GM",   "MANT", "F", "TWTR", "BKR", "XOM",
                    "TSLA","GOOG",  "FB","AMZN",  "JMP", "MS", "GD", 
                    'MRNA', 'PFE', 'NVAX')
        self.stock_selected = StringVar()   ## was self.x  *** this Holds STOCK - TICKER 
        self.stock_spinbox = Spinbox(self.stock_frame, values=stocktickers, width=6, 
                             textvariable=self.stock_selected, font=("Arial", 20), 
                             justify=CENTER, fg='white', bg='black', 
                             buttonbackground='black')  
        self.stock_spinbox.grid(column=1, row=1, sticky=W, padx=10, rowspan=1)
        self.stock_selected.set('IBM')  
        #################################  FOR ALL YEARS: TRY  SPIN BOX ####################################################
        ttk.Label(self.stock_frame, text="PICK A TIMEFRAME").grid(column=1,row=4)
        timedurations=("100 days", "One Yr", "2 Years", "3 Years", "5 Years", "10 Years", "all yrs")        
        # timedurations=("One Yr", "100 days", "all yrs")
        self.ksftime_selected = StringVar()   ## was self.x  *** this Holds TIME DURATION selection 
        self.timedur_spinbox = Spinbox(self.stock_frame, values=timedurations, width=8, 
                             textvariable=self.ksftime_selected, font=("Arial", 15), 
                             justify=CENTER, fg='black', bg='white', 
                             buttonbackground='white')  
        self.timedur_spinbox.grid(column=1, row=4, sticky=W, padx=10, rowspan=1)
        self.ksftime_selected.set("100 days")  ## this selects ALL the YEARS
        

        ##  KSF frame_b  placed in right frame    ###############################################################################################
        # Create Frame_right  inside GUI canvas
        
        # frame for frame b & c
        self.frame_right = ttk.Frame(self.guiWin_, padding="15 15 15 15")   ## 2nd = NORTH ! wnes /or in guiWin_  instead ?  mainframe
        self.frame_right.grid(column=1, row=0, sticky=(W, N, E, S))  
        
        
        self.frame_b = ttk.Frame(self.frame_right, padding="15 15 15 15")   ## 2nd = NORTH ! wnes /or in guiWin_  instead ?  mainframe
        self.frame_b.grid(column=0, row=0, sticky=(N, W))     ## was sticky=(N, W, E, S)
        

        
        
        # Add Label Widgets to frame_b
        ttk.Label(self.frame_b, text="PEG Ratio").grid(column=1,row=1, sticky=W)
        ttk.Label(self.frame_b, text="Div Yld"). \
                                              grid(column=1, row=2, sticky=W)
        ttk.Label(self.frame_b, text="Analyst Tgt $"). \
                                              grid(column=1, row=3, sticky=W)
        ttk.Label(self.frame_b, text="Trail PE"). \
                                              grid(column=1, row=5, sticky=W)
        ttk.Label(self.frame_b, text="Payout Ratio"). \
                                              grid(column=1, row=4, sticky=W) 

                                             
        #ttk.Separator(self.frame_b, orient=HORIZONTAL).grid(column=1, row=7, columnspan=4, sticky="EW")
 
        ## was self.x  *** this Holds STOCK - TICKER 
        

        
        


        col2wdt = 8
        # Add Entry Widget for PEG Ratio
        self.peg_rat = StringVar()
        self.peg_rat_entry = ttk.Entry(self.frame_b, width=col2wdt,justify=CENTER,
                        textvariable=self.peg_rat, font=("Arial", 20, "bold"))
        self.peg_rat_entry.grid(column=2, row=1, sticky=(W, E))
        print("*** 255: SETUP ENTRY_WiDGEt for PEG_Ratio")   
                
        # Add Entry Widget for Display of the Div Yld           
        self.div_yld = StringVar()
        self.div_yld_entry = ttk.Entry(self.frame_b, width=col2wdt, 
                    textvariable=self.div_yld, justify=CENTER, font=("Arial", 20, "bold"))
        self.div_yld_entry.grid(column=2, row=2, sticky=(W, E))
        print("*** 262: SETUP ENTRY_WiDGEt for div_yld") 
        
        # Add Entry Widget for Display of the Analyst _tgt Price
        self.anal_tgt = StringVar()
        self.anal_tgt_entry = ttk.Entry(self.frame_b, width=col2wdt, 
                    textvariable=self.anal_tgt, justify=CENTER, font=("Arial", 20, "bold"))
        self.anal_tgt_entry.grid(column=2, row=3, sticky=(W, E))
        print("*** 269: SETUP ENTRY_WiDGEt for analyst_tgt_price") 
        
        # Add Entry Widget for Display of the tr_pe Trailing PE Ratio
        self.tr_pe = StringVar()
        self.tr_pe_entry = ttk.Entry(self.frame_b, width=col2wdt, 
                    textvariable=self.tr_pe, justify=CENTER, font=("Arial", 20, "bold"))
        self.tr_pe_entry.grid(column=2, row=5, sticky=(W, E))
        print("*** 276: SETUP ENTRY_WiDGEt for trailing_pe")
        
        # Add Entry Widget for Payout Ratio
        self.payout_rat = StringVar()
        self.payout_rat_entry = ttk.Entry(self.frame_b, width=col2wdt, 
                    textvariable=self.payout_rat, justify=CENTER, font=("Arial", 20, "bold"))
        self.payout_rat_entry.grid(column=2, row=4, sticky=(W, E))
        print("*** 283: SETUP ENTRY_WiDGEt for payout_ratio")

        # # ############## end of frame_b ############   
        
        ##  KSF frame_c  -placed in right frame- starts here  ######################################################################################
        ##  KSF frame_c  ###############################################################################################
        # Create Frame inside GUI canvas
        self.frame_c = ttk.Frame(self.frame_right, padding="15 15 15 15")   ## or in guiWin_  instead ?  mainframe
        self.frame_c.grid(column=1, row=0, sticky=(N, W))     ## was sticky=(N, W, E, S)
        

        
        
        # Add Label Widgets to frame_b
        ttk.Label(self.frame_c, text="Profit Margin").grid(column=1,row=1, sticky=W)
        ttk.Label(self.frame_c, text="Operating Margin"). \
                                              grid(column=1, row=2, sticky=W)
        ttk.Label(self.frame_c, text="ROE"). \
                                              grid(column=1, row=3, sticky=W)
        ttk.Label(self.frame_c, text="Qtrly Rev Gro"). \
                                              grid(column=1, row=4, sticky=W)
        # ttk.Label(self.frame_c, text="% Insiders"). \
        #                                      grid(column=1, row=5, sticky=W) 
        ttk.Label(self.frame_c, text="ForwardPE"). \
                                             grid(column=1, row=5, sticky=W) 
                                         
        ttk.Separator(self.frame_right, orient=HORIZONTAL).grid(column=0, row=1, columnspan=2, sticky="EW")
 

        
        col2wdt = 8
        # Add Entry Widget for "Profit Margin")
        self.ProfitMargin = StringVar()
        self.ProfitMargin_entry = ttk.Entry(self.frame_c, width=col2wdt,justify=CENTER,
                        textvariable=self.ProfitMargin, font=("Arial", 20, "bold"))
        self.ProfitMargin_entry.grid(column=2, row=1, sticky=(W, E))
        print("*** 318: SETUP ENTRY_WiDGEt for PEG_Ratio")   
                
        # Add Entry Widget for Display of the "Operating Margin"          
        self.OperatingMarginTTM = StringVar()
        self.OperatingMarginTTM_entry = ttk.Entry(self.frame_c, width=col2wdt, 
                    textvariable=self.OperatingMarginTTM, justify=CENTER, font=("Arial", 20, "bold"))
        self.OperatingMarginTTM_entry.grid(column=2, row=2, sticky=(W, E))
        print("*** 325: SETUP ENTRY_WiDGEt for Operating Margin") 
        
        # Add Entry Widget for Display of the ROE
        self.ReturnOnEquityTTM = StringVar()
        self.ReturnOnEquityTTM_entry = ttk.Entry(self.frame_c, width=col2wdt, 
                    textvariable=self.ReturnOnEquityTTM, justify=CENTER, font=("Arial", 20, "bold"))
        self.ReturnOnEquityTTM_entry.grid(column=2, row=3, sticky=(W, E))
        print("*** 332: SETUP ENTRY_WiDGEt for ROE") 
        
        # Add Entry Widget for Display of the QuarterlyRevenueGrowthYOY
        self.QuarterlyRevenueGrowthYOY = StringVar()
        self.QuarterlyRevenueGrowthYOY_entry = ttk.Entry(self.frame_c, width=col2wdt, 
                    textvariable=self.QuarterlyRevenueGrowthYOY, justify=CENTER, font=("Arial", 20, "bold"))
        self.QuarterlyRevenueGrowthYOY_entry.grid(column=2, row=4, sticky=(W, E))
        print("*** 369: SETUP ENTRY_WiDGEt for qtrly Rev Growth YOY")
        
        # Add Entry Widget for ForwardPE
        self.ForwardPE = StringVar()
        self.ForwardPE_entry = ttk.Entry(self.frame_c, width=col2wdt, 
                    textvariable=self.ForwardPE, justify=CENTER, font=("Arial", 20, "bold"))
        self.ForwardPE_entry.grid(column=2, row=5, sticky=(W, E))
        print("*** 346: SETUP ENTRY_WiDGEt for ForwardPE")
                
        
        # # Add Entry Widget for % Insiders
        # self.PercentInsiders = StringVar()
        # self.PercentInsiders_entry = ttk.Entry(self.frame_c, width=col2wdt, 
        #             textvariable=self.PercentInsiders, justify=CENTER, font=("Arial", 20, "bold"))
        # self.PercentInsiders_entry.grid(column=2, row=5, sticky=(W, E))
        # print("*** 346: SETUP ENTRY_WiDGEt for Percent Insiders")
        
        # Add Entry Widget for ForwardPE
        self.ForwardPE = StringVar()
        self.ForwardPE_entry = ttk.Entry(self.frame_c, width=col2wdt, 
                    textvariable=self.ForwardPE, justify=CENTER, font=("Arial", 20, "bold"))
        self.ForwardPE_entry.grid(column=2, row=5, sticky=(W, E))
        print("*** 346: SETUP ENTRY_WiDGEt for ForwardPE")

 
        
                
#----------------------------------Frame-right   made new frame to  fit everything ---------------------------------------------------------------
        
        self.frame_d = ttk.Frame(self.frame_right, padding="5 5 5 5")   ## or in guiWin_  instead ?  mainframe
        self.frame_d.grid(column=0, row=2, columnspan = 2, sticky=(W, N, E, S)) 
        
        ttk.Label(self.frame_d, text="Select A Language").grid(column=0,row=0, sticky = W)
        
        self.lang_key = list(self.lang_dict.keys())#needed .keys to use the dictionary

        
        self.lang_selected = StringVar() 
        self.lang_spinbox = Spinbox(self.frame_d, values=self.lang_key, width=10, 
                             textvariable=self.lang_selected, font=("Arial", 20), 
                             justify=CENTER, fg='white', bg='red', 
                             buttonbackground='black')  
        self.lang_spinbox.grid(column=1, row=0, sticky=W, padx=10, rowspan=1)
        self.lang_selected.set('English')  
        
        #  made a button to retrieve the narrative
        ttk.Button(self.frame_d, text = "Get Narrative", cursor = "hand2", \
                   #width = col2wdth, \
                   command = self.get_narrative)\
            .grid(row = 0, column = 2, columnspan = 1, sticky = (W, E))
            
            ## created a text box to enter narrative
        self.narrative_box = Text(self.frame_right, relief = "solid", \
                            padx = 5, pady = 5,font = ("Cambria", 12), \
                            width = 45, height = 30, wrap = WORD)
                            #with and height are for size of box
                            
        self.narrative_box.grid(row=3, column=0, columnspan = 2, sticky=(N, W, E, S))
        

        ##  making lang select a string variable
        self.lang_selected = StringVar()   ## was self.x  *** this Holds STOCK - TICKER 


        
        
        
    def lang_translate(self):
        """Translates text into the target language.
    
        Target must be an ISO 639-1 language code.
        See https://g.co/cloud/translate/v2/translate-reference#supported_languages
        """
        translate_client = translate.Client(credentials=self.credentials)
    
        if isinstance(self.input_text, six.binary_type):
            self.input_text = self.input_text.decode("utf-8")
    
        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = translate_client.translate(self.input_text, 
                                            target_language=self.target)
    
        #print(u"Text: {}".format(result["input"]))
        self.translation = result["translatedText"]
        #print(u"Translation: {}".format(result["translatedText"]))
        #print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))




    def stock_clear(self):
        temp = 0
        
    # Function to get stock closing price (at the end of each day) information 
    def stock_close(self):
        self.stock_clear()
        self.stock_stat()
        
    def ksfOVERVIEW_FrameB(self):
        self.symbol.get()  ## redundant
        ## no - we have symbol ! don't need NEXT LINE:
        # self.symbol.set(self.stock_selected.get())
        
        
        ## the plan: get this done -- repeat for FRAME C - with its Variables
        
        ## first store the symbol  ***** KEY !!! 
        # check for missing stock symbol
        # base url
        # main url - whole thing- - adding the OVERVIEW SECTION
        # get method of requests module returns response object  
        # then load each variable
        
        
        ## first store the symbol  ***** KEY !!! 
        #--- make sure I did this similar to the SECTION IN HW6 *************************
        c_symbol = self.symbol.get().upper()
        ####  self.symbol.set(c_symbol)
        print("*** # 317 symbol....  ",c_symbol)
        # base_url variable store base url  
        base_url = \
        r"https://www.alphavantage.co/query?function=OVERVIEW"

        # main_url variable store complete url 
        
        main_url = base_url + "&symbol=" + c_symbol + \
                   "&apikey=" + self.api_key   
        print("*** 326: KSF_test  ",  "   ... main url \n", main_url,"\n")
        
        res_obj = requests.get(main_url) 
        #           json method returns json format data into python dictionary data type.  
        self.result = res_obj.json()    
        ##print keys here   
        KSF_keys = self.result.keys()
        print("*** # 333  keys of Dictionary",KSF_keys)
        #### Now get and process each of the data items retreived for display####
        try:
            
            ####################################3
            self.peg_rat_temp = self.result.get("PEGRatio")  ########## get PEGRatio
            self.peg_rat.set(self.peg_rat_temp)
            # self.peg_rat.set(self.peg_rat_temp+" %")
            print("** 341 -- PEGRatio \n", self.div_yld.get())
            
            self.div_yld_temp = self.result.get("DividendYield")  ########## get div_yld
            self.div_yld.set(self.div_yld_temp)
            # self.div_yld.set(self.div_yld_temp+" %")
            print("** 346 -- div_yld \n", self.div_yld.get())
            
            self.anal_tgt_temp = self.result.get("AnalystTargetPrice")  ########## get anal_tgt
            self.anal_tgt.set("$ "+self.anal_tgt_temp)
            print("** 350 -- analyst_tgt_price \n", self.anal_tgt.get())
            
            self.tr_pe_temp = self.result.get("TrailingPE")  ########## get tr_pe
            self.tr_pe.set(self.tr_pe_temp)
            print("** 354 -- tr_pe \n", self.tr_pe.get())
            
            self.payout_rat_temp = self.result.get("PayoutRatio")  ########## get payout_rat
            self.payout_rat.set(self.payout_rat_temp)
            # self.payout_rat.set(self.payout_rat_temp+" %")
            print("** 359 -- payout_ratio \n", self.payout_rat.get())
            

            
            # NOW use---  self.KSF_co_desc  ---to load the DESC into textVar  
            # WITH .get()  ... might work w/out .get()
            ### NOT THIS HEREself.textVar = self.peg_rat.get()  
            #####################################
            #####################################
            ##########$$$$$$$$$$$$$$$$$$$$$$$$$$
            # self.p_change = self.result["Global Quote"]['10. change percent']
            # self.change.set(self.p_change)
            # ##########$$$$$$$$$$$$$$$$$$$$$$$$$$
            # # CHG this to be TRAILINGPE
            # print("*** 252:  PEGRatio = ", c_symbol)
            # # Get and Display Last Closing Price
            # self.c_price = self.result["Global Quote"]['05. price']
            # f_price = round(float(self.c_price), 2)
            # self.c_price = str(f_price)
            # self.close_price.set("$"+self.c_price)
            
            # # CHG this to be PEGRatio
            # # Get and Display Previous Day's Closing Price
            # self.pc_price = self.result["Global Quote"]['08. previous close']
            # f_price = round(float(self.pc_price), 2)
            # self.pc_price = str(f_price)
            # self.p_close_price.set("$"+self.pc_price)

            # # CHG this to be PayoutRatio
            # # Get and Display Percent Change in Stock Value
            # self.p_change = self.result["Global Quote"]['10. change percent']
            # self.change.set(self.p_change)
            
            # # CHG this to be DividendYield
            # # Get and Display Last Day's Volume for this Stock
            # self.volume = self.result["Global Quote"]['06. volume']
            # v = int(self.volume) # converts the string self.volume to integer
            # v = "{:,}".format(v) # converts int to string with commas
            # self.vol.set(v)
            
            # #ADD IN 
            # # CHG this to be AnalystTargetPrice
            # # Make Room for this one ?? or ask to eliminate it
            # self.volume = self.result["Global Quote"]['06. volume']
            # v = int(self.volume) # converts the string self.volume to integer
            # v = "{:,}".format(v) # converts int to string with commas
            # self.vol.set(v)
            # ###### after format the fixed, rounding etc eliminate 358-395 i.e., the commented out part just above #####################################
            
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "For our Symbol " + c_symbol + " Problem getting items for   frame_b  "
            showwarning(title="*** 411:  Warning", message=warn_msg)
            self.clear_entries()
    
    
    def ksfOVERVIEW_FrameC(self):
        self.symbol.get()  ## redundant
        ## no - we have symbol ! don't need NEXT LINE:
        # self.symbol.set(self.stock_selected.get())
        
        
        
        ## after get this done -- repeat for FRAME C - with its Variables
        
        ## first store the symbol  ***** KEY !!! 
        # check for missing stock symbol
        # base url
        # main url - whole thing- - adding the OVERVIEW SECTION
        # get method of requests module returns response object  
        # then load each variable
        
        
        ## first store the symbol  ***** KEY !!! 
        #--- make sure I did this similar to the SECTION IN HW6 *************************
        c_symbol = self.symbol.get().upper()
        ####  self.symbol.set(c_symbol)
        print("*** # 499 symbol....  ",c_symbol)
        # base_url variable store base url  
        base_url = \
        r"https://www.alphavantage.co/query?function=OVERVIEW"

        # main_url variable store complete url 
        
        main_url = base_url + "&symbol=" + c_symbol + \
                   "&apikey=" + self.api_key   
        print("*** 508: KSF_test  ",  "   ... main url \n", main_url,"\n")
        
        res_obj = requests.get(main_url) 
        #           json method returns json format data into python dictionary data type.  
        self.result = res_obj.json()    
        ##print keys here   
        KSF_keys = self.result.keys()
        print("*** # 515  keys of Dictionary",KSF_keys)
        #### Now get and process each of the data items retreived for display####
        try:
            
            ####################################3
            self.ProfitMargin_temp = self.result.get("ProfitMargin")  ########## get PEGRatio
            self.ProfitMargin.set(self.ProfitMargin_temp)
            # self.ProfitMargin.set(self.ProfitMargin_temp+" %")
            print("** 523 -- ProfitMargin \n", self.ProfitMargin.get())
            
            self.OperatingMarginTTM_temp = self.result.get("OperatingMarginTTM")  ########## get div_yld
            self.OperatingMarginTTM.set(self.OperatingMarginTTM_temp)
            # self.div_yld.set(self.OperatingMarginTTM_temp+" %")
            print("** 528 -- OperatingMarginTTM \n", self.OperatingMarginTTM.get())
            
            self.ReturnOnEquityTTM_temp = self.result.get("ReturnOnEquityTTM")  ########## get anal_tgt
            self.ReturnOnEquityTTM.set(self.ReturnOnEquityTTM_temp)
            print("** 532 -- ReturnOnEquityTTM \n", self.ReturnOnEquityTTM.get())
            
            self.QuarterlyRevenueGrowthYOY_temp = self.result.get("QuarterlyRevenueGrowthYOY")  ########## get tr_pe
            self.QuarterlyRevenueGrowthYOY.set(self.QuarterlyRevenueGrowthYOY_temp)
            print("** 536 -- QuarterlyRevenueGrowthYOY \n", self.QuarterlyRevenueGrowthYOY.get())
            
            # self.PercentInsiders_temp = self.result.get("PercentInsiders")  ########## get payout_rat
            # self.PercentInsiders.set(self.PercentInsiders_temp)
            # # self.PercentInsiders.set(self.PercentInsiders_temp+" %")
            # print("** 541 -- PercentInsiders \n", self.PercentInsiders.get())
            # Add Entry Widget for ForwardPE
            ##########################################################################
            # self.ForwardPE = StringVar()
            # self.ForwardPE_entry = ttk.Entry(self.frame_c, width=col2wdt, 
            #             textvariable=self.ForwardPE, justify=CENTER, font=("Arial", 20, "bold"))
            # self.ForwardPE_entry.grid(column=2, row=5, sticky=(W, E))
            # print("*** 346: SETUP ENTRY_WiDGEt for ForwardPE")
            ## fix
            self.payout_rat_temp = self.result.get("PayoutRatio")  ########## get payout_rat
            self.payout_rat.set(self.payout_rat_temp)
            # self.payout_rat.set(self.payout_rat_temp+" %")
            print("** 359 -- payout_ratio \n", self.payout_rat.get())
            ### KSFFIX to be ForwardPE !!!
            
            ####################
            # RIGHT --
            self.ForwardPE_temp = self.result.get("ForwardPE")  ########## get ForwardPE
            self.ForwardPE.set(self.ForwardPE_temp)
            # self.ForwardPE.set(self.ForwardPE_temp+" %")
            print("** 375 -- SETUP ENTRY_WiDGEt for  ForwardPE \n", self.ForwardPE.get())
            #####################
            
            # NOW use---  self.KSF_co_desc  ---to load the DESC into textVar  
            # WITH .get()  ... might work w/out .get()
            ### NOT THIS HEREself.textVar = self.peg_rat.get()  
            #####################################
            #####################################
            ##########$$$$$$$$$$$$$$$$$$$$$$$$$$
            ### done for try part of frame_c items ##################################
            
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "For our Symbol " + c_symbol + " Problem getting items for   frame_c  "
            showwarning(title="*** 556:  Warning", message=warn_msg)
            self.clear_entries()
        ### done ALL OF  frame_c items ###############################################
    
    
    def stock_stat(self) : 
        self.symbol.set(self.stock_selected.get())
        ## first store the symbol  ***** KEY !!! 
        ########### ??? it doesn't seem to get the "SPINBOX VALUE"
        # self.stock_selected.get()             ### NOPE (but good try)...you can't "get" it ... must SET it !!
        # self.symbol.set(self.stock_selected)  ### NOPE, but ALMOST: you must have .get() (see line 238 for correct syntax !!! 
        
        # Check for missing stock symbol
        if self.symbol.get() == "":
            showinfo(title="*** 544   Warning", message="Symbol Missing")
            self.clear_entries()
            return
        c_symbol = self.symbol.get().upper()
        self.symbol.set(c_symbol)
        # base_url variable store base url  
        base_url = \
        r"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"

        # main_url variable store complete url 
        main_url = base_url + "&symbol=" + c_symbol + \
                   "&apikey=" + self.api_key      
        # get method of requests module returns response object  
        res_obj = requests.get(main_url) 
        # json method returns json format data into python dictionary data type. 
        # rates are returned in a list of nested dictionaries 
        self.result = res_obj.json()
        try:
            print("*** 562:  c_symbol = ", c_symbol)
            # Get and Display Last Closing Price
            self.c_price = self.result["Global Quote"]['05. price']
            f_price = round(float(self.c_price), 2)
            self.c_price = str(f_price)
            self.close_price.set("$"+self.c_price)
            
            # Get and Display Previous Day's Closing Price
            self.pc_price = self.result["Global Quote"]['08. previous close']
            f_price = round(float(self.pc_price), 2)
            self.pc_price = str(f_price)
            self.p_close_price.set("$"+self.pc_price)

            # Get and Display Percent Change in Stock Value
            self.p_change = self.result["Global Quote"]['10. change percent']
            self.change.set(self.p_change)
            
            # Get and Display Last Day's Volume for this Stock
            self.volume = self.result["Global Quote"]['06. volume']
            v = int(self.volume) # converts the string self.volume to integer
            v = "{:,}".format(v) # converts int to string with commas
            self.vol.set(v)
            
            # load all the items into   frame_b: **********************************************
            self.ksfOVERVIEW_FrameB()
            self.ksfOVERVIEW_FrameC()
            
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "Symbol " + c_symbol + " Not Found"
            showwarning(title="*** 591:  Warning", message=warn_msg)
            self.clear_entries()

    def clear_entries(self):
        self.stock_clear()
        self.symbol.set("")
        self.close_price.set("")
        self.p_close_price.set("")
        self.change.set("")
        self.vol.set("")
        ##########################  KEY  -- MUST ERASE PRIOR IMAGE:
        self.imgwin = ttk.Label(self.mainframe, text=""). \
                        grid(column=1, row=4, columnspan=8, sticky=W)  ##### USE THIS TO CLEAR THE IMAGE !!!

    def get_series(self):
        # Check for missing stock symbol
        if self.symbol == "":
            showinfo(title="*** 307:  Warning", message="Symbol Missing")
            return
        c_symbol = self.symbol.get().upper()
        # base_url variable store base url  
        base_url = \
          r"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
        All_Year_url =   r"&outputsize=full"  ## KSF added for YEAR... actually 20 years
        #self.ksftime_selected.get()
        #---------------------------------------
        # ksf_ti_sel = self.ksftime_selected.get()
        # if ksf_ti_sel == "One Yr":
        #     Year_url = All_Year_url
        #     KSF_timedur = "One Year"
        #     nn = 249  ## there are 249 stock market trading days in a year
        # elif ksf_ti_sel == "all yrs" :
        #     Year_url = All_Year_url
        #     KSF_timedur = "Last 100 Days"
        #     nn = 0  ## use 100 trading days
        # else:
        #     Year_url = r"&outputsize=compact"
        #     KSF_timedur = "Last 100 Days"
        #     nn = 100  ## use 100 trading days
        #########################################################
        ksf_ti_sel = self.ksftime_selected.get()
        if ksf_ti_sel == "One Yr":
            Year_url = All_Year_url
            KSF_timedur = "One Year"
            nn = 249  ## there are 249 stock market trading days in a year
        elif ksf_ti_sel == "2 Years" :
            Year_url = All_Year_url
            KSF_timedur = "2 Years"  ## KSF--may need to chg this LATER, LEAVE FOR NOW
            nn = 499  ## use  2 yrs = 2*249  of trading days based on len(series) ... it's fixed  25 lines BELOW
        elif ksf_ti_sel == "3 Years" :
            Year_url = All_Year_url
            KSF_timedur = "3 Years"  ## KSF--may need to chg this LATER, LEAVE FOR NOW
            nn = 747  ## use 3 yrs = 3*249  of trading days based on len(series) ... it's fixed  25 lines BELOW  
        elif ksf_ti_sel == "5 Years" :
            Year_url = All_Year_url
            KSF_timedur = "5 Years"  ## KSF--may need to chg this LATER, LEAVE FOR NOW
            nn = 1245  ## use 5 yrs = 5*249  of trading days based on len(series) ... it's fixed  25 lines BELOW 
        elif ksf_ti_sel == "10 Years" :
            Year_url = All_Year_url
            KSF_timedur = "10 Years"  ## KSF--may need to chg this LATER, LEAVE FOR NOW
            nn = 2490  ## use 10 yrs = 10*249  of trading days based on len(series) ... it's fixed  25 lines BELOW  

        elif ksf_ti_sel == "all yrs" :
            Year_url = All_Year_url
            KSF_timedur = "Last 100 Days"  ## KSF--may need to chg this LATER, LEAVE FOR NOW
            nn = 0  ## use real number of trading days based on len(series) ... it's fixed  25 lines BELOW
        else:
            ## this case is the "100 Days" Case
            Year_url = r"&outputsize=compact"
            KSF_timedur = "Last 100 Days"
            nn = 100  ## use 100 trading days        
        #########################################################
        # main_url variable store complete url 
        main_url = base_url + "&symbol="+c_symbol+Year_url+"&apikey="+self.api_key         
        # get method of requests module returns response object  
        res_obj = requests.get(main_url) 
        # json method returns json format data into python dictionary data type. 
        # rates are returned in a list of nested dictionaries 
        result = res_obj.json()
        
        try:
            series = result['Time Series (Daily)']
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "Symbol " + c_symbol + " Not Found"
            showwarning(title="*** 327:  Warning", message=warn_msg)
            self.clear_entries()
            return
        
        
        n = nn ## len is 100 for 100 days // 249 for a Year // 0 for ALL YRS ... full
        if nn == 0:
            n = len(series)
        f_array = np.array([[0.0]*4]*n)
        i_array = pd.Series([0]*n)
        t_array = pd.Series([pd.to_datetime("2020-01-01")]*n)
        i = n-1
        
        for key in series:
            t_array.loc[i] = pd.to_datetime(key, utc=False)
            i_array.loc[i] = int(series[key]['6. volume'])
            f_array[i][0] = float(series[key]['5. adjusted close'])
            f_array[i][1] = float(series[key]['4. close'])
            f_array[i][2] = float(series[key]['3. low'])
            f_array[i][3] = float(series[key]['2. high'])
            i-=1
            if i < 0:
                 break
            
        df0 = pd.DataFrame(t_array, columns=['date'])
        df1 = pd.DataFrame(f_array, columns = \
                          ['adjusted_close', 'close', 'low', 'high'])
        df2 = pd.DataFrame(i_array, columns=['volume'])
    
        self.df  = pd.concat([df0, df1, df2], axis=1).set_index('date')
    
    def graph_ts(self):
        self.get_series()
        # Check for missing stock symbol
        if self.symbol.get() == "":
            showinfo(title="*** 357:  Warning", message="Symbol Missing")
            self.clear_entries()
            return

        if self.c.get() == 1:
            # plot close price
            title = "Closing Price"
            x     = 'close'
        elif self.v.get() == 1:
            # plot volume
            title = "Volume"
            x     = 'volume'
        elif self.narr.get() == 1:
            # plot change
            title = "Narrative"
            x     = "narrative"
        ############################################################
                    
        self.fig = plt.figure(figsize=(9, 6), dpi=100)
        self.fig.patch.set_facecolor('gray')
        self.fig.patch.set_alpha(0.3)
        font1 = {'family':'Arial','color':'maroon','size': 16,
                 'weight':'normal'}
        font2 = {'family':'Arial','color':'maroon','size': 14,
                 'weight':'normal'}
        gp = self.fig.add_subplot(1,1,1)
        gp.set_facecolor('maroon')
        gp.plot(self.df[x], color='white')
        
        start_date = str(self.df.index[0].date())
        n          = len(self.df.index)-1
        end_date   = str(self.df.index[n].date())
        
        c_symbol   = self.symbol.get().upper() + \
                             " ("  + start_date + " to "  + end_date+")"
                             
        base_url = \
          r"https://www.alphavantage.co/query?function=SYMBOL_SEARCH"
    
        # main_url variable store complete url 
        main_url = base_url + "&keywords="+self.symbol.get()+ \
                        "&apikey="+self.api_key         
        # get method of requests module returns response object  
        res_obj = requests.get(main_url) 
        # json method returns json format data into python dictionary data type. 
        # rates are returned in a list of nested dictionaries 
        result = res_obj.json()
        
        try:
            series = result['bestMatches']
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "Symbol " + c_symbol + " Not Found"
            showwarning(title="*** 410:  Warning", message=warn_msg)
            self.clear_entries()
            return
        first_company = result["bestMatches"][0]
        name = first_company["2. name"]
        score = float(first_company["9. matchScore"])
        print(score)
        #plt.title(c_symbol, fontdict=font1)
        plt.title(name,   fontdict=font1)
        plt.ylabel(title, fontdict=font2)
        plt.grid(True)
        plt.savefig('ts_plot.png')
        plt.show()
        self.imgobj = ImageTk.PhotoImage(Image.open('ts_plot.png'))  ## reformat image to be acceptable
        self.imgwin = ttk.Label(self.mainframe, image=self.imgobj). \
                        grid(column=1, row=9, columnspan=4, sticky=W)
        ############################################################



    def plt_close(self):
        self.c.set(1)
        self.v.set(0)
        try:
            self.t.delete(1.0, "end")           
        except:
            # If Narrative has not yet been called there is no self.t
            temp = 0
        self.graph_ts()
            
        
    def plt_vol(self):
        self.c.set(0)
        self.v.set(1)
        try:
            self.t.delete(1.0, "end")           
        except:
            # If Narrative has not yet been called there is no self.t
            temp = 0       
        self.graph_ts()
    ###############################################
    def classify(self, client, text, verbose=True):
        """Classify the input text into categories. """
    
        document = language.Document(
            content=text, type_=language.Document.Type.PLAIN_TEXT
        )
        response   = client.classify_text(request={'document': document})
        categories = response.categories
    
        result = {}
    
        for category in categories:
            # Turn the categories into a dictionary of the form:
            # {category.name: category.confidence}, so that they can
            # be treated as a sparse vector.
            result[category.name] = category.confidence
    
        if verbose:
            print(text)
            for category in categories:
                print(u"=" * 20)
                print(u"{:<16}: {}".format("category", category.name))
                print(u"{:<16}: {}".format("confidence", category.confidence))
    
        return result        
    ###############################################    
    def DispNarr(self):   ##this is the narrative that is plaved in the left box
        """### DISPLAY NARRATIVE  ... in a TEXTBOX  ### """ 
        #################### CLEAR PRIOR GRAPH ####################
        self.imgwin = ttk.Label(self.mainframe, text=""). \
                grid(column=1, row=9, columnspan=4, sticky=W)
        ######## Setup for narrative - KSF - skip plot ################  
        x     = "narrative"
        if x     != "narrative":    
            self.fig = plt.figure(figsize=(6, 4), dpi=100)
            self.fig.patch.set_facecolor('gray')
            self.fig.patch.set_alpha(0.3)
            font1 = {'family':'Arial','color':'maroon','size': 16,
                     'weight':'normal'}
            font2 = {'family':'Arial','color':'maroon','size': 14,
                     'weight':'normal'}
            gp = self.fig.add_subplot(1,1,1)
            gp.set_facecolor('maroon')
            gp.plot(self.df[x], color='white')
            
            start_date = str(self.df.index[0].date())
            n          = len(self.df.index)-1
            end_date   = str(self.df.index[n].date())
        
            c_symbol   = self.symbol.get().upper() + \
                             " ("  + start_date + " to "  + end_date+")"
        

        elif x     == "narrative": 
            KSF_plot = 0
            print("\n*** #505 - KSF- no plot for Narrative ****\n")
            
        base_url = \
          r"https://www.alphavantage.co/query?function=SYMBOL_SEARCH"
    
        # main_url variable store complete url 
        main_url = base_url + "&keywords="+self.symbol.get()+ \
                        "&apikey="+self.api_key         
        # get method of requests module returns response object  
        res_obj = requests.get(main_url) 
        # json method returns json format data into python dictionary data type. 
        # rates are returned in a list of nested dictionaries 
        result = res_obj.json()
        
        try:
            series = result['bestMatches']
            print("*** # 521 - Stock symbol 'self.symbol.get()'", self.symbol.get())
        except:
            # If Stock Symbol is Invalid Display a Warning
            warn_msg = "Symbol " + c_symbol + " Not Found"
            showwarning(title="*** 525:  Warning", message=warn_msg)
            self.clear_entries()
            return
        first_company = result["bestMatches"][0]
        name = first_company["2. name"]
        score = float(first_company["9. matchScore"])
        print(score)
        ######################################################
        x = "narrative"
        if x     != "narrative":   
            #plt.title(c_symbol, fontdict=font1)
            plt.title(name,   fontdict=font1)
            plt.ylabel(title, fontdict=font2)
            plt.grid(True)
            plt.savefig('ts_plot.png')
            plt.show()
            self.imgobj = ImageTk.PhotoImage(Image.open('ts_plot.png'))
            self.imgwin = ttk.Label(self.mainframe, image=self.imgobj). \
                            grid(column=1, row=9, columnspan=4, sticky=W)
        elif x     == "narrative": 
            ## process narrative coing here ##########################
            print("\n*** #546 - KSF- setup Narrative here ****\n")
            print("*** # 547 - Stock symbol 'self.symbol.get()'", self.symbol.get())
            ## change this to be narrative get...

            ## use KSF_test to try out the results of just using the "demo" to see if Description works
            KSF_test = 0
            if KSF_test == 1:
                
                # base_url = \
                # r"https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=CK8FNM4QB629PDZL"
                # main_url = base_url
                #_________________________________________________
                base_url = \
                "https://www.alphavantage.co/query?function=OVERVIEW&symbol="
                ext = "IBM&apikey=CK8FNM4QB629PDZL"
                main_url = base_url + ext
                #main_url  = ''.join([base_url, ext])
                # #__________________________________________________
                print("*** 413__: KSF_test  ", KSF_test,"\nmain_url \n", main_url)
                #    r"https://www.alphavantage.co/query?function=OVERVIEW"  ### PUT THIS BACK
            elif KSF_test == 0: 
                
                #########################################################################
                c_symbol = self.symbol.get().upper()
                ####  self.symbol.set(c_symbol)
                print("*** # 571 symbol....  ",c_symbol)
                # base_url variable store base url  
                base_url = \
                r"https://www.alphavantage.co/query?function=OVERVIEW"
        
                # main_url variable store complete url 
                
                main_url = base_url + "&symbol=" + c_symbol + \
                           "&apikey=" + self.api_key   
                print("*** 580: KSF_test  ", KSF_test,"\nmain url \n", main_url)
                #########################################################################



            # get method of requests module returns response object  
            res_obj = requests.get(main_url) 
            # json method returns json format data into python dictionary data type. 
            # rates are returned in a list of nested dictionaries 
            result = res_obj.json()
            
            self.input_text = result['Description']
            ### no keys for dict ??? 
        
            
            # with open("narrative.txt","w")as f:
            #     f.write(result["Description"])
            #     f.close()
            try:    
                KSF_keys = result.keys()
                print("*** # 601  keys of Dictionary",KSF_keys)
            except:
                print("***  #470:  KSF error - this dictionary has error when try to get KEYS")
            
            try:
                self.KSF_co_desc = result.get("Description")  ################# get nar
                print("Description \n", self.KSF_co_desc)
                
                ####### KSF-ask-INSERT THIS HERE ? or (? didn't work up top) ##################
                # NOW use---  self.KSF_co_desc  ---to load the DESC into textVar (FOR TEXTBOX)
                # w/o .get()
                self.textVar = self.KSF_co_desc  ### KSF - do I need .get() ?
                print("***  605:  KSF - dont need .get()\n", self.textVar)  
                # WITH .get()
                self.textVar = self.KSF_co_desc.get()  ### KSF - do I need .get() ?
                print("***  608  KSF - dont need .get()\n", self.textVar) 
                
            except:
                print('*** # 611: KSF  result.get("Description")  does not work to get description') 
                  
            ################################################################
            
        #####################  XXX NOT THIS: NARRATIVE WINDOW (as a LABEL  ##################################
        KSF_Label = 0   ## KSF_Label=1  means use Label Widget; if == 0 then use TEXTbox Widget instead
        if KSF_Label == 1:
            self.narrwindow = ttk.Label(self.mainframe, text=self.KSF_co_desc). \
                grid(column=1, row=9, columnspan=4, sticky=W)
                
        
        ####################### YES: THIS: NARRATIVE AS A TEXT BOX ################################
        if KSF_Label == 0:
            # 1st Create Text Box
            self.t = Text(self.mainframe, relief='sunken', wrap='word', width=33,
                          height=32, bg='maroon', fg='white', font=('Arial', 12))
            self.t.grid(column=1, columnspan=4, row=9, rowspan=1, 
                      sticky=(N, W, S, E))
            
            # 2nd CLEAR the text box:
                        # Clear the Text Box  (from 1st Char to the END)
            self.t.delete(1.0, "end")        
            #########################  INSERT THE TEXT INTO TEXT BOX !!!!!!!!!!   ##########
            ## 3rd "use 'method' to .insert() the text, starting at 1st character "1"
            self.t.insert(1.0, self.KSF_co_desc)
        #######################  eo NARRATIVE AS A TEXT BOX ################################

        ## Now Get Categories & Confidence ##
        text = self.KSF_co_desc
        google_project_file = "GoogleTranslateCredentials.json" ## FILE MUST BE IN SAME DIRECTORY
        credentials, project_id = google.auth.\
                          load_credentials_from_file(google_project_file)
                          
        client = language.LanguageServiceClient(credentials=credentials)
        
        
        ### CALL CLASSIFICATION F() ########
        #self.classify(client, text, verbose=True)  ## instead: embed f() below:
        
        
        #############################################################
        #def classify(self, client, text, verbose=True):  (based on f() def)
        """Classify the input text into categories. """
    
        document = language.Document(
            content=text, type_=language.Document.Type.PLAIN_TEXT
        )
        response   = client.classify_text(request={'document': document})
        categories = response.categories
    
        result = {}
    
        for category in categories:
            # Turn the categories into a dictionary of the form:
            # {category.name: category.confidence}, so that they can
            # be treated as a sparse vector.
            result[category.name] = category.confidence
        
        ## Concatenate the Description and the Category+Conf using a loop:
        verbose = True      ## 'switch': borrowed this from f() def
        if verbose:
            print(text)
            Desc         = self.KSF_co_desc
            Desc_and_Cat = Desc + "\n"
            for category in categories:
                a = "\n********************"
                b = "category:  " + category.name
                c = str(round(category.confidence,2))
                d = "confidence:  " +  c
                Cat = "\n" + a +"\n" + b +"\n" + d
                Desc_and_Cat = Desc_and_Cat + Cat
        #### Erase existing Narrative & rewrite it w Desc & Categories+Conf:
        self.t.delete(1.0, "end")  
        #This would have worked if there were only 1 category:
        #Desc         = self.KSF_co_desc
        #Desc_and_Cat = Desc  + "\n" + a +"\n" + b +"\n" + d
        
        ###########  PUT THE TEXT (i.e. INSERT IT !!) INTO TEXTBOX #############
        self.t.insert(1.0, Desc_and_Cat)
        
        
        ##############################################################
        
        ##  SETUP for SENTIMENT  (ALTHOUGH NOT NEEDED FOR THIS HOMEWORK)
        document = language.Document(content=text, language='en',
                              type_=language.Document.Type.PLAIN_TEXT)
        response  = client.analyze_sentiment(document=document)
        ## We Can get sentiment --score  & --magnitude
        sentiment = response.document_sentiment
        ### FOR NOW --- DON"T PRINT THESE, so set 'switch' off:
        KSF_Sent_Print = False
        if KSF_Sent_Print:
            print(sentiment.score)
            print(sentiment.magnitude)


    # function to translate narrative and place in left text box
    def get_narrative(self):
          # gets language from spinbox 
        self.language = self.lang_spinbox.get() 
        #used dictionary to get language
        self.target = self.lang_dict[self.language]
        
        self.DispNarr()
        # print("\n\n\n")
        # print("Narrative Printed from get_narrative \t:", self.input_text)
        # print("\n\n\n")
        self.lang_translate()
        self.narrative_box.delete(1.0, "end")
        #self.narrative_box["state"] = NORMAL
        self.narrative_box.insert(1.0, self.translation)
"""     
    ############################################  add in SENTIMENT (not needed here) #######################
    import pandas as pd
    import google.auth
    from   google.cloud import language_v1 as language
    
    def get_text_sentiment(client, text):
        document = language.Document(content=text, language='en',
                                 type_=language.Document.Type.PLAIN_TEXT)
        
        response = client.analyze_sentiment(
                        document=document,
                        encoding_type = 'UTF32'
                    )
        sentiment = response.document_sentiment
        return sentiment.score
    
    def get_text_classification(client, text):
        document = language.Document(content=text, language='en',
                                     type_=language.Document.Type.PLAIN_TEXT)
        response = client.classify_text(request={'document':document})
        for category in response.categories:
            print("Category Name: {}".format(category.name))
            print("Confidence:    {}".format(category.confidence))
            
    def KSF_Sent(self):
        ### Google Credentials ###
        google_project_file = "GoogleTranslateCredentials.json"
        credentials, project_id = google.auth.\
                              load_credentials_from_file(google_project_file)
                              
        client = language.LanguageServiceClient(credentials=credentials)
        
        ############### KSF - create Text file.from    self.symbol   .. NOT just IBM (was demo)
        #text_file = "text/IBM.txt" # Sentiment = 0, Magnitude = 1.6
        text_file = '"text/'+ self.symbol.get() + '.txt"'
        try:
            with open(text_file, "r") as file_contents:
                    contents = file_contents.read()
        except Exception as e:
            print("Unable to open ", text_file)
            print(e)
                
        # The text to analyze
        ########################### KSF - change the PRINT... NOT IBM
        text = contents
        print("\nIBM: {}\n".format(text))
        document = language.Document(content=text, language='en',
                                 type_=language.Document.Type.PLAIN_TEXT)
        response = client.analyze_sentiment(document=document,encoding_type = 'UTF8')
        sentiment = response.document_sentiment
        print("Entire Text Sentiment & Magnitude: {}, {}\n".\
           format(sentiment.score, sentiment.magnitude))
        
        # Detects the sentiment of the text
        encoding_type = language.EncodingType.UTF8
        sentiment     = client.analyze_sentiment(request={
                        'document': document,
                        'encoding_type': encoding_type}).document_sentiment
        print("Entire Text Sentiment & Magnitude: {}, {}\n".\
           format(sentiment.score, sentiment.magnitude))
        
        score = get_text_sentiment(client, text)
        print("Entire Text Sentiment: {}\n".format(score))
        
        print("Language", response.language)
        senti  = 0.0
        mag    = 0.0
        n      = 0
        l      = 0
        sentil = 0.0
        magl   = 0.0
        print("\nIndividual Sentences\n")
        for sentence in response.sentences:   # therefore can look at each sentence separately (google set it up)
            n += 1
            l += len(sentence.text.content)
            senti  += sentence.sentiment.score
            sentil += sentence.sentiment.score * len(sentence.text.content)
            mag    += sentence.sentiment.magnitude
            magl   += sentence.sentiment.magnitude * len(sentence.text.content)
            print("\nSentence: {}".format(sentence.text.content))
            print("Sentiment Score: {}".format(sentence.sentiment.score))
        
        print("Summary")
        print("N", n, "Total Sentiment", senti, "Total Magnitude", mag)
        print("Avg. Sentiment: ", senti/n)
        print("Avg. Magniture: ", mag/n)
        print("Wtg. Avg. Sentiment: ", sentil/l)
        print("Wtg. Avg. Magnitude: ", magl/l)
        return
        ########################################## eo Function Def #######################
    ############################################## eo SENTIMENT ##########################"""
# Instantiate GUI Canvas Using Tk   

# Language dictionary
language_dictionary = {
    "English"    : "en",
    "Spanish"    : "es",
    "German"     : "de",
    "French"     : "fr",
    "Italian"    : "it",
    "Afrikaans"  : "af",
    "Zulu"       : "zu",
    "Arabic"     : "ar",
    "Persian"    : "fa",
    "Chinese"    : "zh",
    "Japanese"   : "ja",
    "Korean"     : "ko",
    "Vietnamese" : "vi",
    "Latin"      : "la",
    "Hindi"      : "hi",
    "Russian"    : "ru",
    "Tamil"      : "ta",
    "Punjabi"    : "pa",
    "Serbian"    : "sr",
    "Polish"     : "pl",
    "Malay"      : "ms",
    "Turkish"    : "tr",
    "Finnish"    : "fi",
    "Hebrew"     : "he",
    "Urdu"       : "ur",
    "Thai"       : "th",
    "Kannada"    : "kn",
    "Malayalam"  : "ml",
    "Bengali"    : "bn",
    "Greek"      : "el",
    "Gujarati"   : "gu",
    "Indonesian" : "id",
    "Portuguese" : "pt",
    "Telugu"     : "te",
    "Marathi"    : "mr",
    "Norwegian"  : "no",
    "Danish"     : "da",
    "Dutch"      : "nl",
    "Swedish"    : "sv",
    "Welsh"      : "cy",
    "Irish"      : "ga",
    "Yiddish"    : "yi",
    "Mongolian"  : "mn",
    "Nepali"     : "ne",
    "Filipino"   : "fil",
    }

root = Tk()
root.title("Karen Fireman's Stock Price GUI")
api_key         = "demo"
api_key         = "CK8FNM4QB629PDZL"
# Paint Canvas Using Class StockGUI __init__()

# google_project_file = "C:\TAMU\Semester 5\Fundamentals of Busness programing\Group project/GoogleTranslateCredentials.json"
google_project_file = "GoogleTranslateCredentials.json"
credentials, project_id = google.auth.load_credentials_from_file(google_project_file)

my_gui = StockGUI(root, language_dictionary, api_key, credentials)
# Display GUI
root.mainloop()

