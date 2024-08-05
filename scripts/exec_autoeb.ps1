$ExecuteDir = (Get-Location).Path
$ShellDir = [System.IO.Path]::GetDirectoryName($MyInvocation.MyCommand.Path)

Set-Location $ShellDir
Set-Location ..\src\

# enter venv
.venv\Scripts\activate

# execute AUTOEB
Set-Location $ExecuteDir
python.exe -m autoeb $args
# exit venv
deactivate
