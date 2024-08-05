$ExecuteDir = (Get-Location).Path
$ShellDir = [System.IO.Path]::GetDirectoryName($MyInvocation.MyCommand.Path)
$VenvName = ".venv"

function Out-Error {
    Write-Host $args -ForegroundColor Red
}

function Out-Info() {
    Write-Host $args -ForegroundColor Cyan
}

Set-Location $ShellDir
Set-Location "..\src\"
$SearchPath = [System.IO.Path]::Combine((Get-Location).Path, ($VenvName))

if ([System.IO.File]::Exists($SearchPath)) {
    Out-Error "file '${VenvName}' is exists"
    Set-Location $ExecuteDir
    Exit 1
}
if ([System.IO.Directory]::Exists($SearchPath)) {

    Out-Error "folder '${VenvName}' is already exists"
    Set-Location $ExecuteDir
    Exit 2
}

Out-Info "start initializing project..."
# venv
Out-Info "generating python venv"
python -m venv $VenvName
Invoke-Expression "${VenvName}\Scripts\activate"

# update pip
Out-Info "upgrading pip of venv"
python -m pip install --upgrade pip

# install packages
Out-Info "installing required packages"
pip install -r requirements.txt

#fin
Out-Info "initializing finished successful!"
deactivate

Set-Location $ExecuteDir
