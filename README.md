# Diary

![Icon](/static/icons/64x64.png "Icon")

A simple diary.

## Setup without Docker

1. `sudo apt update`

2. `sudo apt install git python3 python3-pip -y`

3. `git clone https://github.com/dodaucy/diary.git`

4. `cd diary`

5. `python3 -m pip install -r requirements.txt`

6. `cp example_config.env config.env`

7. `nano config.env`

8. Start: `python3 -m uvicorn main:app`

## Setup with Docker

...

## License

**MIT**

Copyright (C) 2022 dodaucy
