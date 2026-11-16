@echo off
rem The same walk-through in a 1920 x 1080 window (for a smaller screen).
start "" "%~dp0Windows\Wieland1527.exe" -ResX=1920 -ResY=1080 -Windowed -ExecCmds="scalability 3,r.ScreenPercentage 67,r.Streaming.PoolSize 4000"
