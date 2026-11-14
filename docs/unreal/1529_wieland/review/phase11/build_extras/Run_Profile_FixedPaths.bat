@echo off
rem Plays the fixed camera paths of the profile (60 s street walk, holds S1 S2 S6, triplex 30 s, hold D5, penthouse 20 s, hold D2, roof deck 10 s, each after an 8 s settle) in a loop,
rem records 60000 frames with the engine frame-time recorder and closes by itself (about 10 minutes).
rem The record is written to Windows\Wieland1527\Saved\Profiling\CSV\. Uncapped frame rate, as measured for the delivery notes.
start "" "%~dp0Windows\Wieland1527.exe" /Game/Wieland1529/Delivery/L_W1529_Profile -ResX=2560 -ResY=1440 -FullScreen -ExecCmds="scalability 3,r.ScreenPercentage 67,r.Streaming.PoolSize 4000,t.MaxFPS 0,r.VSync 0" -csvCaptureFrames=60000 -ExitAfterCsvProfiling -csvGpuStats
