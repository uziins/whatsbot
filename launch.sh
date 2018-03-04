#!/usr/bin/env bash
# change virtualenv path below and suit to yours
VIRTUAL_ENV=${HOME}/.virtualenvs/whatsbot

THIS_DIR=$(cd $(dirname $0); pwd)
APP_NAME=${PWD##*/}
cd ${THIS_DIR}
. ${VIRTUAL_ENV}/bin/activate

install(){
    pip install --upgrade setuptools
    pip install -r requirements.txt
    echo "Requirements installed successfully"
}

update(){
    pip install -r ${THIS_DIR}/requirements.txt -U
    echo "Updated"
}

clean(){
    sudo find / -name 'axolotl.db' -exec rm -rf {} \;
}

deploy(){
    cp etc/systemd.service etc/${APP_NAME}.service
    sed -i "s/yourusername/$(whoami)/g" etc/${APP_NAME}.service
    sed -i "s_thisdir_${THIS_DIR}_g" etc/${APP_NAME}.service
    sudo mv etc/${APP_NAME}.service /etc/systemd/system/
    sudo systemctl enable ${APP_NAME}
    sudo systemctl start ${APP_NAME}
    echo "Bot deployed!"
    echo "Try: sudo systemctl status $APP_NAME"
}

undeploy(){
    if [ -f "/etc/systemd/system/${APP_NAME}.service" ]; then
        sudo systemctl stop ${APP_NAME}
        sudo systemctl disable ${APP_NAME}
        sudo rm /etc/systemd/system/${APP_NAME}.service
        echo "Bot service removed"
    else
        echo "No bot service. Skipping..."
    fi
}
if [ "$1" = "install" ]; then
    install
elif [ "$1" = "update" ]; then
    update
elif [ "$1" = "clean" ]; then
    clean
elif [ "$1" = "deploy" ]; then
    deploy
elif [ "$1" = "undeploy" ]; then
    undeploy
elif [ "$1" = "register" ]; then
    echo "Input phone number (ex. 62851234567) and press [ENTER]"
    read number_input
    if [ -z ${number_input} ]; then
        echo "Please input the phone number"; exit 1
    else
        re='^[0-9]+$'
        if ! [[ ${number_input} =~ $re ]] ; then
            echo "Must be number" >&2; exit 1
        fi
        PN=${number_input}
        CC=${PN:0:2}
        yowsup-cli registration --requestcode sms --phone ${PN} --cc ${CC} -E android
        echo "Input code sent via sms and press [ENTER]:"
        read code_input
        if ! [[ ${code_input} =~ $re ]] ; then
            echo "Must be number" >&2; exit 1
        fi
        yowsup-cli registration --register ${code_input} --phone ${PN} --cc ${CC} -E android
    fi
else
    python main.py $@
fi