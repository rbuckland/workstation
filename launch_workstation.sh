#!/bin/bash

desired_version=${1:-2.4-34a4dff}

docker_image=$( docker images --format '{{ .Repository }}:{{ .Tag }}' \
                              --filter=reference="rbuckland/workstation:${desired_version}" )
image_version=$( echo ${docker_image} | cut -f2 -d: )                              

container_hostname=ws-${image_version//\./-}
relative_curdir=${PWD/$HOME/}
the_uid=$( id -u )
the_gid=$( id -g )
the_shell=$(basename $SHELL)

existing_container=$( docker ps --filter name=${container_hostname} --format "{{ .ID }}" )

if [ -z $existing_container ]; then

    echo ":: Launching new ${docker_image}"
    docker run --rm -ti                              \
        --name ${container_hostname}                 \
        --hostname ${container_hostname}             \
        -p 3000:3000                                 \
        -p 3030:3030                                 \
        -p 8000:8000                                 \
        -p 8080:8080                                 \
        -e USERNAME=${USER}                          \
        -e OUTER_HOME=${HOME}                        \
        -e AS_UID=${AS_UID:-$the_uid}                         \
        -e AS_GID=${AS_GID:-$the_gid}                         \
        -e WITH_SHELL=${the_shell}                   \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v ${HOME}:/home/${USER}                     \
        --workdir /home/${USER}${relative_curdir}    \
        ${docker_image}

else

    echo ":: Launching into running container ${container_hostname} [${existing_container}]"
    docker exec -ti -e USERNAME=${USER}                   \
        --workdir /home/${USER}${relative_curdir}         \
        ${existing_container} /bin/workstation/entrypoint.sh
fi
