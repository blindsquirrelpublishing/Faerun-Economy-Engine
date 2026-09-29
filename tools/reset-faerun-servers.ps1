Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
  Where-Object { $_.CommandLine -like '*Faerun-Economy-Engine*' -or $_.CommandLine -like '*faerun.cli*serve*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Process `
  -FilePath 'C:\repos\Source\Faerun-Economy-Engine\.venv\Scripts\python.exe' `
  -ArgumentList '-u','-m','faerun.cli','--no-seasonal-inventory','serve','--host','127.0.0.1','--port','8883','--no-browser' `
  -WorkingDirectory 'C:\repos\Source\Faerun-Economy-Engine' `
  -WindowStyle Hidden
