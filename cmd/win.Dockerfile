# =============================================================================

FROM mcr.microsoft.com/windows/servercore:ltsc2022 AS poetry
ENV PYTHON_URI=https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe

RUN curl %PYTHON_URI% -o python-installer.exe
RUN python-installer.exe /quiet

RUN setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python313"
RUN setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python313\Scripts"

RUN pip install pipx
RUN pipx ensurepath

RUN pipx install poetry

# -----------------------------------------------------------------------------

FROM poetry
WORKDIR /workdir

COPY . .

RUN poetry install
RUN poetry run pyinstaller resources/configs/ryujinxkit.spec

# =============================================================================
