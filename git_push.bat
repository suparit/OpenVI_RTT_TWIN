@echo off
setlocal EnableDelayedExpansion

REM =========================================================================
REM git_push.bat  —  OpenVI_TR1100_CELL_TWIN
REM Stage, commit, and push all changes to the personal GitHub repo.
REM Runs inside TE corporate network (sets HTTP(S) proxy automatically).
REM =========================================================================

REM --- Corporate network proxy (TE) ---
set HTTP_PROXY=http://restrictedproxy.connect.te.com:80
set HTTPS_PROXY=http://restrictedproxy.connect.te.com:80

REM --- Ensure Git is on PATH ---
set "PATH=%PATH%;C:\Program Files\Git\cmd"

cd /d "%~dp0"

REM --- Verify git availability ---
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git not found on PATH. Install Git for Windows or add C:\Program Files\Git\cmd to PATH.
    pause
    exit /b 1
)

REM --- Verify gh auth (optional but helpful) ---
gh auth status >nul 2>&1
if errorlevel 1 (
    echo [WARN] gh not authenticated. Run: gh auth login -h github.com
)

REM --- Stage all changes ---
echo [1/4] git add -A
git add -A

REM --- Show what will be committed ---
echo.
echo [2/4] git status --short
git status --short

REM --- Commit message (argument or prompt) ---
if "%~1"=="" (
    set /p commitMsg="Enter commit message: "
) else (
    set commitMsg=%*
)

if "!commitMsg!"=="" (
    echo [ERROR] Commit message cannot be empty.
    exit /b 1
)

echo.
echo [3/4] git commit -m "!commitMsg!"
git commit -m "!commitMsg!"

REM --- Push ---
echo.
echo [4/4] git push -u origin master
git push -u origin master

echo.
echo =========================================================================
echo DONE.
echo =========================================================================

endlocal
pause
