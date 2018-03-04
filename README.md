
![CircleCI](https://img.shields.io/circleci/project/github/RedSparr0w/node-csgo-parser.svg?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg?style=flat-square)
![AUR](https://img.shields.io/aur/license/yaourt.svg?style=flat-square)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=JENHGK6EGW55U&lc=US&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)




# WhatsBot

A plugin based whatsapp bot

## Getting Started

WhatsBot is one of my weekend - just for fun projects. Thanks to plugin logic, all you need is write the plugin you want and enable it right on the chat without touching the core code. 

This bot uses Yowsup, a python library that enables you build application which use whatsapp service.

###### Disclaimer
You might find some dirty and ugly code, feel free to make it clean and better.

### Basic
- **Requires python3** mine is 3.6
- **Requires MySQL** Don't ask me why i am using this, it's easy to integrate with my other stuff that uses MySQL too. Simply, i do what i want to do :D
- **Python Virtualenv**
- **Yowsup** [https://github.com/AragurDEV/yowsup](https://github.com/AragurDEV/yowsup) This is a fork of [https://github.com/tgalal/yowsup](https://github.com/AragurDEV/yowsup)

### Installation
- Edit `VIRTUAL_ENV` in **launch.sh** with your virtualenv path, ex: `VIRTUAL_ENV=${HOME}/.virtualenvs/whatsbot`
- Run the install command:
```
./launch.sh install
```

### Register

- Register to whatsapp
```
./launch.sh register
```
Follow the instructions, you will be prompted to input phone number and verification code sent via sms, just follow it. Then you will get password.
- Edit credentials and other configuration detail in `data/config.json`. You need to specify database (make sure it's prepared already). Sudo user is your number in whatsapp user_id format.
```
{
  "bot_name": "Ellissa",
  "download_dir": "/tmp/whatsbot",
  "credentials" : {
    "phone": "62858xxxxxxx",
    "password": "xxxxxxxxxxxxxxxxx="
  },
  "database": {
    "db_host": "localhost",
    "db_user": "xxxx_user",
    "db_password": "xxxxxxxxx",
    "db_name": "xxxx_db"
  },
  "sudo_user": ["62899xxxxxxx@s.whatsapp.net"],
  "plugins": ["admin"],
  "contacts": {
    "62899xxxxxxxxxx": "Botmaster"
  }
}
```

## Run
- Via terminal

`./launch.sh`

- Install as systemd service

`./launch.sh deploy`

It will start automatically

### Start and stop

`sudo systemctl start whatsbot` 

`sudo systemctl stop whatsbot`

To remove from service you can run this command `./launch.sh undeploy`

## Plugins

You can write plugin based on example

`chat_data` is where your conversation done. Can be private message (`chat_data = user data`), or group message (`chat_data = group data`) 

`user_data` is data of user / sender


#### Plugin admin command

- Show plugins available
```
/plugins
```
- Enable plugin (botself)
```
/plugins enable botself
```
- Disable plugin (botself)
```
/plugins disable botself
```
- Reload plugins
```
/plugins reload
```

## Built With

* [Yowsup](https://github.com/tgalal/yowsup) - The python WhatsApp library
* [PyMySQL](https://pymysql.readthedocs.io/en/latest/) - Python MySQL client


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details

## Thanks to

* Hat tip to anyone who's code was used
* mac - [danielcardeenas](https://github.com/danielcardeenas)
* cups of coffee
* etc


## Donation
If you love this project, you can buy me a cup of coffee :) 

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=JENHGK6EGW55U&lc=US&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)