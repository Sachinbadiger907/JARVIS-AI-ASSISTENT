' Double-click this file to start Jarvis silently in the background,
' with no visible terminal/console window.

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\HP\OneDrive\Desktop\JARVIS AI ASSISTENT"
WshShell.Run """C:\Users\HP\AppData\Local\Programs\Python\Python312\pythonw.exe"" main.py", 0, False
 