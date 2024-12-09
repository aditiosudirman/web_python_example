@echo off
echo Building Docker image...
docker build -t myweb-api .
if %errorlevel% neq 0 (
    echo Error during build. Exiting.
    exit /b %errorlevel%
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
