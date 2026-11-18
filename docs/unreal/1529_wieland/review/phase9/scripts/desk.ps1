# Phase 9: is somebody using the computer? Prints, every 5 seconds for -Seconds seconds, the time since the last
# keyboard or mouse input and the window in front. Reads only; changes nothing.
#   powershell -NoProfile -File desk.ps1 -Seconds 20
# With -WaitIdle N it instead waits until nobody has typed or moved the mouse for N seconds (at most -Seconds), then prints one line.
param([int]$Seconds = 10, [int]$WaitIdle = 0)
Add-Type @'
using System; using System.Runtime.InteropServices; using System.Text;
public class Desk {
  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO info);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  public static double Idle() { LASTINPUTINFO i = new LASTINPUTINFO(); i.cbSize = 8; GetLastInputInfo(ref i); return ((uint)Environment.TickCount - i.dwTime) / 1000.0; }
}
'@
function Line {
  $h = [Desk]::GetForegroundWindow()   # only the program's name is printed, never the window's title
  $p = 0; [void][Desk]::GetWindowThreadProcessId($h, [ref]$p)
  $name = (Get-Process -Id $p -ErrorAction SilentlyContinue).ProcessName
  $editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue | Select-Object -First 1
  $minimised = if ($editor) { [Desk]::IsIconic($editor.MainWindowHandle) } else { 'no editor' }
  "{0} idle {1:N0} s | front: {2} | editor minimised: {3}" -f (Get-Date -Format HH:mm:ss), [Desk]::Idle(), $name, $minimised
}
$end = (Get-Date).AddSeconds($Seconds)
if ($WaitIdle -gt 0) {
  while ((Get-Date) -lt $end -and [Desk]::Idle() -lt $WaitIdle) { Start-Sleep -Seconds 2 }
  Line
} else {
  while ((Get-Date) -lt $end) { Line; Start-Sleep -Seconds 5 }
}
