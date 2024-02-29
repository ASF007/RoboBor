<div class="header">
  <p align = "center"><img width="512" src="assets/logo.png"></p>
  <p align = "center"><img width="248" height="248" src="assets/robbor_green(light).png"></p>
</div>

# Update
> I haven't abandoned this project, I'll work on it if I get some free time, feel free to fork it and create PR's , I'll review them in my free time and push them, however create a issue first or [join the support server](https://discord.gg/upTFQ2zRgJ) and ping me there with what issue your adding. Do **note** that this is meant to be community feature driven bot. <br> </br>
To View the current features [Click Here](https://gist.github.com/ASF007/d5299239251a1d128641eebe1a068a07)


# What is this? 
RoboBor is a discord bot which aims to bring you various features to make discord fun for you, most of these are community requested which can be done so by either creating a issue or requesting one in the [support server](https://discord.gg/upTFQ2zRgJ).

- This bot is inspired by [RoboTop](https://robotop.xyz/) and aims to bring back features that will not be maintained anymore (ie moderation, automod etc).
- The code here has been simplified to encourage user contribution.
- This project aims to get your intrests in programming.
- *Psst don't come after me if the code looks messy or bad (after all I wrote it a few yrs back)*
# TODO Features
Following features will be added sooner/later
- Misc commands & features from RoboTop
- Custom Commands
- Strike based automod (powered by AI ??)

# How to run the bot

**Pre-Requisites**

**NOTE**: You must have a active redis server running and also have a mongo DB url as well.

**Step 1**
Fork the bot first, then clone / download the  your copy of the bot.

```sh
$ git clone link-to-my-forked-repo.git # should somewhat look like https://github.com/YourUserName/RoboBor
$ cd RoboBor
```
**Step 2**
Create and Activate the virtual environment, make sure you have python 3.9 (Haven't tested on 3.10 as of now)

*Note:*
- For windows the python command should usually be `py` or `python`
 - For linux based platforms it should be `python3`

```sh
$ python -m venv venv # will create a virtual environment called venv
$ venv/bin/activate # Windows
$ source venv/bin/activate # Linux
```
**Step 3**
Before you proceed make sure to rename `.env.example` to `.env` and fill up the values.

**Step 4**
Once you have activated the venv, you should see its name on the left side (see below), once you see that make sure to install the packages via the pip command, after that simply run the main file and the bot should be up.
```sh
$ (venv) pip install -r requirements.txt # run this if this is your first time running the bot or if the bot got updated 
$ (venv) python __main__.py 
```

# Credits
This project makes use of various OSS which includes: 
- [RoboTop commands.Bot extension (fork)](https://github.com/ASF007/RoboTop) orignally created by [Skelmis](https://github.com/Skelmis)
- [Discord.py](https://github.com/Rapptz/discord.py) created by [Danny](https://github.com/Rapptz)
