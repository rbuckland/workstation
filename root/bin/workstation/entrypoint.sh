#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

#
# expected environment variables
#

username=${USERNAME:?Missing the USERNAME}
desired_shell=${WITH_SHELL:?Missing the desired WITH_SHELL}
the_uid=${AS_UID:?Missing the AS_UID}
the_gid=${AS_GID:?Missing the AS_GID}


#
# We do a once off setup if they are not configured, as a user in the container
#

if ! id "${username}" &> /dev/null; then
    echo ":: Configuring new user ${username} UID=${the_uid} GID=${the_gid}"
    groupadd -g ${the_gid} ${username}
    useradd \
        --uid ${the_uid} \
        --gid ${the_gid} \
	--no-create-home \
	--home-dir /home/${username} \
	--shell /bin/zsh \
	--no-log-init \
	--uid ${the_uid} \
	--gid ${the_gid} \
	--groups sudo,docker \
	${username}

    chmod 666 /var/run/docker.sock

    echo "${username} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

    ${DIR}/shell_setup_${desired_shell}.sh

fi

exec sudo --set-home --preserve-env --login --user=${username} /bin/${desired_shell}
