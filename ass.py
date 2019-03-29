#!/usr/bin/python

# Archiving SharpShooter - by bzc6p
# This is a program with no warranty. Use it at your own risk.
# See README.md for help and instructions.
# The code is dedicated to the public domain - do whatever you want with it.
# Images included are part of hvg.hu and disqus.com graphical elements.
# They are provided as a test suite for the program. No copyright infringement intended.
# Revision 1 - 2019-03-29


# Prerequisites:
#
# apt-get install python python-pip scrot
# pip install opencv-python-headless pyautogui


# Usage:
#
# Input file (first argument) is a list of URLS
# URLs with errors will be listed in ERRORS file

import pyautogui
import sys
import cv2
import os
import time

###################################################
# USER DATA - FILL IN APPROPRIATELY

max_fails = 2
global_timeout = 900

icon = cv2.imread('icon.png', 0)
comments_icon = cv2.imread('comments_icon.png', 0)
comments_label = cv2.imread('comments_label.png', 0)
morecomments_base = cv2.imread('morecomments_base.png', 0)
morecomments_gray = cv2.imread('morecomments_gray.png', 0)
bottom = cv2.imread('bottom.png', 0)
more_replies = cv2.imread('more_replies.png', 0)

# END OF USER DATA
###################################################

global_timer = time.time()
fails = 0
success = False

def timeout():
    if time.time() - global_timer > global_timeout:
        print "GLOBAL TIMEOUT"
        return True
    else:
        return False
    
def find(template, threshold):
    # makes a screenshot and returns template's location or None
    os.system("scrot -z /dev/shm/scrot.png")
    image = cv2.imread('/dev/shm/scrot.png', 0)
    result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
    minval, maxval, minloc, maxloc = cv2.minMaxLoc(result)
    print "minval:", minval, ", threshold:", threshold
    if minval < threshold: 
        return minloc
    else:
        return None
        
def wait_till(image, threshold, appear, timeout):
    # wait till an image appears or disappears
    timer = time.time()
    delay = 3
    while True:
        if time.time() - timer > timeout:
            print "TIMEOUT"
            return None
        else:
            time.sleep(delay)
            if appear == True:
                loc = find(image, threshold)
                if loc == None:
                    continue
                else:
                    return loc
            else:
                loc = find(image, threshold)
                if loc != None:
                    continue
                else:
                    return 2009
                    
def scroll_click(timeout, exit, *args):
    # scroll until one of (template, timout) args are found; return if exit is found meanwhile
    timer = time.time()
    while True:
        if time.time() - timer > timeout:
            print "TIMEOUT"
            return -1
        if exit != None:
            print "exit template:"
            if find(exit[0], exit[1]) != None:
                return 0
        for a in args:
            print "template", args.index(a)+1, ":"
            loc = find(a[0], a[1])
            if loc != None:
                print "CLICK"
                pyautogui.click(x=loc[0]+a[0].shape[1]/2, y=loc[1]+a[0].shape[0]/2)
                time.sleep(1.5)
                return 1
        pyautogui.press("pagedown")
        pyautogui.press("up")
        time.sleep(0.5)
        
############################################################

# PROGRAM START

if len(sys.argv) != 2:
    print "Missing argument: input file name"
    exit(1)
   
ifile = open(sys.argv[1], 'r')

while True:    
    line = ifile.readline()
    if line == '\n' or line == '':
        ifile.close()
        print "NO MORE URLS"
        exit(0)
    else:
        # SAVING URL STARTS
        
        fails = 0
        success = False
        global_timer = time.time()
        
        while True:
            if success:
                print line[:-1], "successfully scrolled through in", int(round(time.time() - global_timer)), "s"
                break
            else:
                if fails >= max_fails:
                    print "Fatal error with", line[:-1]
                    efile = open('ERRORS', 'a')
                    efile.write(line)
                    efile.close()
                    break
                else:
                    print "---------------------------------------------------"
                    if fails == 0:
                        print "Started scrolling through", line[:-1]
                    else:
                        print "Retrying", line[:-1]
            
            pyautogui.press('f11')
            time.sleep(0.5)
            pyautogui.keyDown('ctrl')
            pyautogui.press('w')
            pyautogui.keyUp('ctrl')
            for c in line:
                if c == '/':
                    pyautogui.keyDown('shift')
                    pyautogui.press('6')
                    pyautogui.keyUp('shift')
                else:
                    pyautogui.press(c)
            pyautogui.press('enter')
            
        
        
            print "Waiting for logo"
            if wait_till(icon, 0.015, True, 60) == None:
                fails += 1
                continue
            
            if timeout():
                fails +=1
                continue
                
            
            pyautogui.press('f11')
            time.sleep(1.5)

            print "Finding comments sign"
            comm = scroll_click(60, (bottom, 0.005), (comments_icon, 0.005))
            if comm == 0:
                success = True
                continue
            elif comm == -1:
                fails += 1
                continue
                
            if timeout():
                fails += 1
                continue
                
            time.sleep(0.5)
            
            print "Waiting for comments"
            if wait_till(comments_label, 0.02, True, 15) == None:
                fails += 1
                continue

            if timeout():
                fails += 1
                continue
            
            pyautogui.click(x=5, y=500)
            
            leave = False
            while True:
                if leave == True:
                    break
                print "Finding more comments"
                more_comm = scroll_click(60, (bottom, 0.005), (morecomments_base, 0.011), (more_replies, 0.01))
                if more_comm == 0:
                    success = True
                    leave = True
                    continue
                elif comm == -1:
                    fails +=1
                    leave = True
                    continue
                
                if timeout():
                    fails += 1
                    leave = True
                    continue
                
                pyautogui.click(x=5, y=500)
                print "Waiting for more comments"
                if wait_till(morecomments_gray, 0.004, False, 30) == None:
                    fails += 1
                    leave = True
                    continue
