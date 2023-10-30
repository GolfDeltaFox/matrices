FROM mambaorg/micromamba
COPY --chown=$MAMBA_USER:$MAMBA_USER matrices.yml /tmp/matrices.yml
# RUN micromamba create -n matrices
RUN micromamba install -y -n base -f /tmp/matrices.yml && \
    micromamba clean --all --yes
ADD . /app
WORKDIR /app
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENV FLASK_APP=matrices
ENV FLASK_ENV=development
CMD flask run