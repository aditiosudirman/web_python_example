@echo off
echo Updating the repository in the current directory...

REM Navigate to the directory where the script is run
cd /d %~dp0

REM Ensure this is a Git repository
if not exist .git (
    echo ERROR: This directory is not a Git repository.
    pause
    exit /b 1
)

REM Pull changes from the remote repository
git pull origin main

REM Notify the user that the update is complete
echo Update complete.
timeout /t 3 /nobreak >nul

REM Check if temp_last_hash.txt exists; create if missing
if not exist temp_last_hash.txt (
    echo Creating initial temp_last_hash.txt...
    echo No hash yet. > temp_last_hash.txt
)

REM Calculate a hash of the source files
certutil -hashfile Dockerfile MD5 > temp_current_hash.txt
for %%f in (src\*.* templates\*.* static\*.*) do (
    certutil -hashfile %%f MD5 >> temp_current_hash.txt
)

REM Compare hashes
fc /b temp_last_hash.txt temp_current_hash.txt >nul
if %errorlevel% equ 1 (
    echo Changes detected. Cleaning up old container and image...

    REM Stop and remove the existing container (if running)
    docker stop my_container 2>nul
    docker rm my_container 2>nul

    REM Remove the old image
    docker rmi myweb-api 2>nul

    echo Rebuilding the image...
    docker build -t myweb-api .
    REM if %errorlevel% neq 0 (
        REM echo Build failed. Exiting.
        REM exit /b %errorlevel%
    REM )
    copy temp_current_hash.txt temp_last_hash.txt >nul
) else (
    echo No changes detected. Skipping build...
)

echo Waiting for 2 seconds...
timeout /t 2 /nobreak >nul

docker ps -a -q --filter "name=my_container" | findstr . >nul
if %errorlevel% equ 0 (
    echo Container 'my_container' already exists. Removing it...
    docker rm -f my_container
)

echo Running Docker container...
docker run -p 8000:8000 --name my_container -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=mydb -e POSTGRES_HOST=host.docker.internal myweb-api
if %errorlevel% neq 0 (
    echo Error during container run. Exiting.
    exit /b %errorlevel%
)

echo Docker container is running. Access it at http://localhost:8000/
pause
