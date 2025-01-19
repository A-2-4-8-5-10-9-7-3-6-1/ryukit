# =============================================================================

docker build -f cmd\resources\docker\windows.Dockerfile -t ryujinxkit:cmd cmd
docker run -v ".\cmd:C:\workdir" -i ryujinxkit:cmd

# =============================================================================
