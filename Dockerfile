FROM python:alpine
LABEL authors="Petr Blaha petr.blaha@cleverdata.cz"
USER root
RUN apk update
RUN apk add  sdl2_ttf sdl2 build-base libc-dev pkgconfig gstreamer sdl2_mixer sdl2_image sdl2_pango linux-headers mesa-dev py3-virtualenv

RUN addgroup -S myuser && adduser -S -G myuser myuser
USER myuser
WORKDIR /home/myuser

RUN pip install --upgrade pip


ENV PATH="/home/myuser/.local/bin:${PATH}"

################### BEGIN Sideband ###########################################

COPY --chown=myuser:myuser requirements.txt requirements.txt

RUN pip install --user -r requirements.txt


COPY --chown=myuser:myuser . .

#Python create virtual environment
RUN virtualenv /home/myuser/sbapp/venv
RUN source /home/myuser/sbapp/venv/bin/activate

RUN make release

################### END Sideband ###########################################