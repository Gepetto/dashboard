ARG TARGET
ARG REGISTRY=eur0c.laas.fr:4567
ARG FROM=gsaurel/buildfarm/robotpkg

FROM ${REGISTRY}/${FROM}:${TARGET}

ARG ROBOTPKG
ARG ROBOTPKG_DEPS=true
ARG ADDITIONAL_DEPENDENCIES=""

RUN /get_deps.sh robotpkg-${ROBOTPKG}

RUN apt-get update -qq && apt-get install -qqy \
   $(sort -u /system_deps $(${ROBOTPKG_DEPS} && echo /robotpkg_deps)) \
   ${ADDITIONAL_DEPENDENCIES} \
   && rm -rf /var/lib/apt/lists/*
