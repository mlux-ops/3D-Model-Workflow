# Phase 11: after a crash or a forced close the editor shows a window "Restore Packages" and runs no tool
# until it is answered. This closes that window without restoring anything (a close message, as if the X
# were clicked) and lists the editor's visible windows before and after. It presses no key.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File close_restore_window.ps1
Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class WielandWindows {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  public static List<string> Run(uint target, string close) {
    var o = new List<string>();
    EnumWindows((h, l) => { uint pid; GetWindowThreadProcessId(h, out pid);
      if (pid == target && IsWindowVisible(h)) { var s = new StringBuilder(256); GetWindowText(h, s, 256); string t = s.ToString();
        if (t.Length > 0) { o.Add(t); if (t.Trim() == close) { PostMessage(h, 0x0010, IntPtr.Zero, IntPtr.Zero); o.Add("  -> close sent"); } } }
      return true; }, IntPtr.Zero);
    return o; }
}
'@
$editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $editor) { "no editor process"; exit 1 }
"before:"; [WielandWindows]::Run([uint32]$editor.Id, "Restore Packages")
[System.Threading.Thread]::Sleep(4000)
"after:"; [WielandWindows]::Run([uint32]$editor.Id, "")
