FROM mcr.microsoft.com/windows/servercore:ltsc2022 AS poetry
RUN curl https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe -o installer.exe
RUN installer.exe /quiet
RUN setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python313"
RUN setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python313\Scripts"
RUN pip install poetry

FROM poetry
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "powershell", "-c", "poetry install; if ($?) { poetry run pyinstaller pyinstaller.spec }" ]
