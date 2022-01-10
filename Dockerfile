FROM ubuntu:latest

ENV ORIG_DEBIAN_FRONTEND=${DEBIAN_FRONTEND}
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y locales 

RUN sed -i -e 's/# en_AU.UTF-8 UTF-8/en_AU.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

ENV TERM xterm
ENV LANG en_AU.UTF-8
ENV LANGUAGE en_AU:en
ENV LC_ALL en_AU.UTF-8

RUN sed -i 's:^path-exclude=/usr/share/man:#path-exclude=/usr/share/man:' \
        /etc/dpkg/dpkg.cfg.d/excludes


#
# Apt Packages
#
COPY root/bin/workstation/apt-packages.txt /bin/workstation/apt-packages.txt
RUN apt update && \
    apt install -y $( cat /bin/workstation/apt-packages.txt | egrep -v "(^#|^\s*$)" )

#
# Development activities
#
COPY root/bin/workstation/versions /bin/workstation/versions

# Python
COPY root/bin/workstation/development.python3.sh /bin/workstation/
COPY root/bin/workstation/packages.python.txt /bin/workstation/
RUN /bin/workstation/development.python3.sh

# Git
COPY root/bin/workstation/development.git-etc.sh /bin/workstation/
RUN /bin/workstation/development.git-etc.sh

# node
COPY root/bin/workstation/development.node.sh /bin/workstation/
COPY root/bin/workstation/packages.node.txt /bin/workstation/
RUN /bin/workstation/development.node.sh

# docker
COPY root/bin/workstation/development.docker.sh /bin/workstation/
RUN /bin/workstation/development.docker.sh


# General utilities
COPY root/bin/workstation/development.general.sh /bin/workstation/
RUN /bin/workstation/development.general.sh


#
# -- finish most of work
#
ENV DEBIAN_FRONTEND=${ORIG_DEBIAN_FRONTEND}

#
# Launching script
#
COPY root/bin/workstation/entrypoint.sh /bin/workstation/
COPY root/bin/workstation/shell_setup_bash.sh /bin/workstation/
COPY root/bin/workstation/shell_setup_zsh.sh /bin/workstation/
ENTRYPOINT [ "/bin/workstation/entrypoint.sh" ]
