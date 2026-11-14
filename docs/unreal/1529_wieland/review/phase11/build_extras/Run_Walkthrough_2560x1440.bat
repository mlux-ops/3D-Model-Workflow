@echo off
rem 1529 N. Wieland St. walk-through, full screen 2560 x 1440, with the real-time settings measured in Phase 9 (profile M7)
rem and in the packaged build (Phase 11): every quality group at Epic, 67 percent of the pixels computed and enlarged
rem by Temporal Super Resolution, texture pool 4000 MB. Mouse looks; W A S D move; E or Space up, Q or C down; Esc does not quit: Alt+F4 quits.
start "" "%~dp0Windows\Wieland1527.exe" -ResX=2560 -ResY=1440 -FullScreen -ExecCmds="scalability 3,r.ScreenPercentage 67,r.Streaming.PoolSize 4000"
