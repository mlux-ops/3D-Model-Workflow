# Phase 17: close the editor without saving and start it again, the way the watcher does, within the watcher's
# five-minute grace (it relaunches the editor itself only after five minutes down).
# Then close the "Restore Packages" window if it appears (PROJECT_MEMORY, Phase 10), and wait for the agent server.
# Opening L_Site_M4 is done afterwards by script, because the project's start level is the earlier production level.
$Project = 'D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject'
function FreeCommitGB { [math]::Round((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB, 1) }
function PortUp { try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 8000); $c.Close(); $true } catch { $false } }
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W17 { [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr FindWindow(string c, string t);
[DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }
"@
"{0} free commit before: {1} GB" -f (Get-Date -Format HH:mm:ss), (FreeCommitGB)
Get-Process UnrealEditor -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 8
"{0} editor ended; free commit: {1} GB" -f (Get-Date -Format HH:mm:ss), (FreeCommitGB)
Start-Process explorer.exe -ArgumentList ('"' + $Project + '"')
for ($i = 0; $i -lt 80; $i++) {
    Start-Sleep -Seconds 10
    $h = [W17]::FindWindow($null, 'Restore Packages')
    if ($h -ne [IntPtr]::Zero) { [W17]::SendMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "{0} closed 'Restore Packages' without restoring" -f (Get-Date -Format HH:mm:ss) }
    if (PortUp) { "{0} agent server answers" -f (Get-Date -Format HH:mm:ss); break }
}
Start-Sleep -Seconds 30
$h = [W17]::FindWindow($null, 'Restore Packages')
if ($h -ne [IntPtr]::Zero) { [W17]::SendMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "{0} closed 'Restore Packages' without restoring" -f (Get-Date -Format HH:mm:ss) }
"{0} free commit after start: {1} GB" -f (Get-Date -Format HH:mm:ss), (FreeCommitGB)
