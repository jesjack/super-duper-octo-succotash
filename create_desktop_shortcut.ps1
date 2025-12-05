$ErrorActionPreference = "Stop"

$WorkDir = "c:\Users\jesja\PycharmProjects\punto_venta"
$PythonExe = "$WorkDir\.venv\Scripts\pythonw.exe"
$ScriptPath = "$WorkDir\pos_app.py"
$ShortcutPath = "$Home\Desktop\Punto de Venta.lnk"

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = """$ScriptPath"""
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.Description = "Iniciar Punto de Venta"
$Shortcut.IconLocation = "$WorkDir\.venv\Scripts\python.exe,0"
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $ShortcutPath"
