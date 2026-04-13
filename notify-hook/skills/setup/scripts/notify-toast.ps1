# notify-toast.ps1 - Shows BurntToast notification, click body to focus window
# If target window is foreground, skip notification silently.
# HWND is encoded in protocol URL to avoid multi-instance file race.

param(
    [long]$Hwnd = 0,
    [string]$Message = '需要你的输入',
    [switch]$Force
)

function Write-Log {
    param([string]$Msg)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts] [notify-toast] $Msg"
    Add-Content -Path (Join-Path $env:TEMP 'claude-notify-debug.log') -Value $line -ErrorAction SilentlyContinue
}

Import-Module BurntToast

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WindowState {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);
}
"@

Write-Log "Triggered: Hwnd=$Hwnd Message='$Message' Force=$Force"

$targetHwnd = [IntPtr]::new($Hwnd)
if (-not [WindowState]::IsWindow($targetHwnd)) {
    Write-Log "SKIP: Invalid window handle $Hwnd"
    exit 0
}

$foregroundHwnd = [WindowState]::GetForegroundWindow()
Write-Log "Foreground=$($foregroundHwnd.ToInt64()) Target=$Hwnd"

if ((-not $Force) -and ($foregroundHwnd -eq $targetHwnd)) {
    Write-Log "SKIP: Target window is already foreground"
    exit 0
}

# Encode HWND in protocol URL (no file-based state sharing)
$launchUrl = "claude-focus://activate?hwnd=$Hwnd"

# Build toast with body-click protocol activation (no button)
$text1 = New-BTText -Text 'Claude Code'
$text2 = New-BTText -Text $Message
$binding = New-BTBinding -Children $text1, $text2
$visual = New-BTVisual -BindingGeneric $binding
$content = New-BTContent -Visual $visual -ActivationType Protocol -Launch $launchUrl -Audio (New-BTAudio -Source 'ms-winsoundevent:Notification.IM')

Submit-BTNotification -Content $content
Write-Log "Toast shown with launch URL: $launchUrl"
