#!/usr/bin/python3

# bootstrap for a simple 256-char 8-bit encoding

asciinames = [
"NULL",
"START OF HEADING",
"START OF TEXT",
"END OF TEXT",
"END OF TRANSMISSION",
"ENQUIRY",
"ACKNOWLEDGE",
"BELL",
"BACKSPACE",
"HORIZONTAL TABULATION",
"LINE FEED",
"VERTICAL TABULATION",
"FORM FEED",
"CARRIAGE RETURN",
"SHIFT OUT",
"SHIFT IN",
"DATA LINK ESCAPE",
"DEVICE CONTROL ONE",
"DEVICE CONTROL TWO",
"DEVICE CONTROL THREE",
"DEVICE CONTROL FOUR",
"NEGATIVE ACKNOWLEDGE",
"SYNCHRONOUS IDLE",
"END OF TRANSMISSION BLOCK",
"CANCEL",
"END OF MEDIUM",
"SUBSTITUTE",
"ESCAPE",
"FILE SEPARATOR",
"GROUP SEPARATOR",
"RECORD SEPARATOR",
"UNIT SEPARATOR"
]

print("charcode,name,character,comments")
for i in range(0,256):
    charname = ""
    if i < 32:
        charname = asciinames[i]
    print(hex(i)+","+charname+",,")

