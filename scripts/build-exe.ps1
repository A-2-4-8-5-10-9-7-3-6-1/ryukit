# =============================================================================

docker build -f cmd\resources\docker\win.Dockerfile -t ryujinxkit:cmd cmd
docker run -v ".\cmd:C:\workdir" -i ryujinxkit:cmd

# =============================================================================
