# Definitions

## Botnet concepts

* **botnet:** botnet is a concept which have the following principles:
1. botnet is a group of bots which are configured with a parameter `botnet: True`.
2. IntelMQ system provides a mechanism to execute just in one command (e.g start/stop/restart/reload/status) actions to all bots which belong to botnet (independently of the `run_mode` parameter). Please check additional information related to this process on each botnet action.
2. all bots that belong to botnet will automatically be started on boot. This means that stream and scheduled bots will behave as normal: stream run indefinitely and scheduled bots will be properly defined on crontab in order to be ready to start on the scheduled time defined in runtime configuration.


## Runtime configuration concepts

* **runtime configuration:** term to mention the configuration file of the bots without specifying if internal or admin runtime configuration because is not required for the explanation since it's transversal.
* **user runtime configuration:** `runtime.conf`, a configuration file used by user to configure bots and also used by intelmqctl to manage the bots.
* **internal runtime configuration:** `.runtime.conf`, a hidden configuration file only used by intelmqctl to track the last successfully configuration used to run bot(s). This file is located in same directory as admin runtime configuration.

Having two runtime configurations as mentioned before is important to scenarios such as:

1. Admin execute the command to start the botnet. In this case there are 10 bots configured as `botnet: True`.
2. Admin accidently remove mannually a bot with `bot_id: my-bot-1` from admin runtime configuration without stopping it previously.
3. Admin add mannually a new bot with `bot_id: my-bot-2` to admin runtime configuration.
4. Admin execute the command to start the botnet which will do the following:
 1. do nothing to the bots which were already started in the first execution of the command to start the botnet
 2. start normally the `bot_id: my-bot-2`
 3. will let the `bot_id: my-bot-1` running but will also add the configuration stored in internal runtime configuration to the admin runtime configuration in order to prevent possible lost of bot configuration by this user mistake.
 4. will log a message providing information to the admin explaining the procedure followed.

 The correct procedure is stop bot first and then remove bot configuration from admin runtime configuration.


**Note:** as mentioned on this section, in order to keep track of bots that are running and their configurations, `intelmqctl` will always keep a currently running state version of admin runtime configuration which is always generated after every `intelmqctl` action command such as `start`, `stop`, etc. However, from an user perspective, there is no need to be aware of this because is just an internal file used by intelmqctl to manage the system and everytime it requires action will ask the user.


## Runtime configuration parameters

* **`botnet: True`** is a parameter on configuration per each bot to define is a bot is part of the botnet or not
* **`onboot`**: TBD
* **`process_manager`**: TBD
* **`run_mode: <scheduled/stream>`** is a parameter on configuration per each bot to define how bot should run.
 - **`stream`:** run indefintely
 - **`scheduled`:** use crontab to start on a specific schedule time (`schedule_time` parameter).
* **`schedule_time`:** is a parameter on configuration, only applicable to bots configured as `scheduled` run mode, to define when the bot MUST start and run one time successfully and then exit.


# Bot commands

Bot commands are commands which can only apply to one bot therefore requires a `<bot_id>`. The commands start/stop/restart/reload/status are the usual commands, however there are more commands implemented such as `enable`, `disable`, `add-to-botnet`, `remove-from-botnet`, `debug` and `scheduler-exec` which have a specific context explained in the following description of each command.


## Usual commands

### intelmqctl start `<bot_id>`

#### Command

```
intelmqctl start `<bot_id>`
```

#### General procedure

`intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
    
#### Specific procedure

* **Run mode: stream**
 - **Process manager: PID** - execute bot and write PID file
 - **Process manager: systemd** - execute `systemctl start <module@bot_id>`
* **Run mode: scheduled**
        add config line on crontab with `intelmqctl scheduler-exec <bot_id>` (message: bot is schedule and will run at `* * * * * `)

### intelmqctl stop `<bot_id>`


    In case that the bot configuration was removed from the runtime.conf and is still running, the bot will be stopped using the old `.runtime.conf` and additionally the runtime configuration of the (previously removed) bot will be again written to the current `runtime.conf`. The principle here is the user first MUST to stop and then remove the configuration, not the opposite.

#### Command

```
intelmqct stop <bot_id>
```

#### General procedure


#### Specific procedure

    stream
        PID - send SIGKILL to bot and remove PID file
        SYSTEMMD - execute `systemctl stop <module@bot_id>`
    scheduled
        send SIGKILL to `intelmqctl scheduler-exec <bot_id>` and delete config line on crontab (message: bot is unscheduled)

intelmqctl restart `<bot_id>`
    call intelmqctl stop `<bot_id>`
    call intelmqctl start `<bot_id>`

intelmqctl reload `<bot_id>`
    read the past runtime.conf (`.etc/.runtime.conf`) and compare with the new one (`.etc/runtime.conf`). Before execute reload, intelmqctl MUST proceed with the following checks:

    if `<bot_id>` is removed from config AND `<bot_id>` is running:
        raise message "`<bot_id>` is no longer on config therefore cannot be reload. Do you want to stop it? [N/y]" \
        "[Y] intelmqctl will remove the bot from all entries on the IntelMQ (e.g. management systems and crontab)" \
        "[N] intelmqctl will add the bot configuration to the new one that you configured."
    
    if `<bot_id>` has a new `run_mode` value AND `<bot_id>` is running:
        raise message "`<bot_id>` is configured with a `run_mode` thefore cannot be reload and it needs to be restarted." \
        "Do you want to restart the bot to apply the new `run_mode`? [Y/n]" \
        "[Y] `intelmqctl` will restart the bot automatically and the bot will be configured with new configuration" \
        "[N] `intelmqctl` will remove and ignore the new `run_mode` value and will add to the configuration the current bot `run_mode`"

    stream
        PID - bot reload config
        SYSTEMD - execute `systemctl reload `<module@bot_id>`
    scheduled
        send SIGHUP to `intelmqctl scheduler-exec <bot_id>`??!?!?! or send a message saying that will only apply to the next execution if there is current one executing.
        check specfic scheduled config and compare with current one, change it if needs (may be the best thing is just overwrite)

    Note: in case run_mode changes, it will require a restart, therefore, nothing should be done except raise a message "run_mode was changed, reload command cannot perform. Please restart the bot to change the run_mode and reload with other possible configurations"

intelctl status `<bot_id>`
    stream
        PID - check if pid exists
        SYSTEMD - execute `systemctl status `<module@bot_id>`
    scheduled
        check if crontab bot config is on crontab

    PRINT bot_id | run_mode | scheduled_time (if applicable) | is on botnet | status | enabled_on_boot
    PRINT last 10 log lines


### On-boot related commands

intelmqctl enable <bot-id>
    put parameter `onboot: True`

intelmqctl disable <bot-id>
    put parameter `onboot: False`

### Botnet related commands

intelmqctl add-to-botnet `<bot_id>`
    stream
        PID - change botnet parameter to True
        SYSTEMD - change botnet parameter to True and execute `systemctl enable <module@bot_id.service>` (belonging to botnet also means enable on-boot except if `init_system: intelmq`)
    scheduled
        change botnet parameter to True and ....  NEED TO REWRITE THIS  .... execute `systemctl enable intelmq.botnet.crontab.service` to enable on boot with systemd like the rest of the botnet

    NOTE: adding a bot to botnet means two important things:
        1. you will be able to execute start/stop/restart/reload/status botnet commands which will apply to all bots that belong to the botnet including this one that you are adding to the botnet.

    **IMPORTANT**: intelmqctl with `init_system: systemd` will always start all botnet on-boot, therefore, there is an issue related to bots configured as scheduled mode that needs to be solve. Read the folllowing scenario/explanation:
        Let's assume that botnet is running but there is a bot which is not part of the botnet also running with run_mode configured as scheduled. In this case it means that there is a crontab entry for that bot. However, since crontab entries are permanent, even when system reboot, the all idea about only bots that belong to botnet with `init_system: systemd` will start on-boot is broken with this scenario. So, to prevent this I propose:

        Assumptions:
            on-boot only applies, as mentioned on this documentation, to bots that belong to botnet where the botnet is configured as `init_system: systemd`. Therefore, we can use systemd to manage this issue without any problem.
        Technical details:
             In order to do this we can create a specific service named `intelmq.crontab_check.service` which will be configured to only run on-boot BEFORE crontab service starts. This service will be responsible to when the operating-system starts, to check if the current runtime configuration regarding scheduled bots matches with the current configuration on crontab. With this, bots that were running as scheduled mode before operating system restarts will be automatically removed from crontab before crontab have a chance to run them.

intelmqctl remove-from-botnet `<bot_id>`
    stream
        PID - change botnet parameter to False
        SYSTEMD - change botnet parameter to False
    scheduled
        change botnet parameter to False

    NOTE: removing a bot from botnet means two important things:
        1. you will continue to be able to execute start/stop/restart/reload/status botnet commands but these commands will NOT be applied to this bot that you removing from the botnet.
        2. if your IntelMQ is not configured with `init_system: intelmq`, instead is configured with `init_system: systemd`, this bot which you are removing from botnet will NOT start automatically on operating system boot (on-boot) in case operating system restarts for some reason.


### Debug related command

intelmqctl debug `<bot_id>`
    ignore run_mode and do:
        check if `intelmqctl status `<bot_id>` and:
            if True:
                raise message "cannot debug bot because bot_id is running or is scheduled", also say that bot needs to be removed from botnet with `intelmqctl del <bot_id>` (just to prevent issues that we don't expect)
            else:
                execute the bot using ONLY the PID approach, log the lines to stdout and wait for CTRL+C


### Scheduling Execution related command

intelmqctl scheduler-exec `<bot_id>`
    scheduled - will execute the usual self.__bot_start() as a bot configured with `run_mode: stream`. Although, before execute, it will perform the following checks:

        if the process who's execute (PPID) this command is crontab process (we need to guarantee that this command can only be executed successfully by crontab since its the scheduler-executor):
            continue
        else: 
            raise a message "`intelmqctl scheduler-exec `<bot_id>` can only be execute by scheduler system (crontab)".

        if `<bot_id>` is still running from the last scheduler execution:
            log a message "`<bot-id>` could not execute at `* * * * *` due the last scheduled execution is still running."


# Botnet commands

## Overview

Only bots which are part of the botnet can be start/stop/restart/reload/status with botnet commands. Also, botnet concept also assumes that all bots which belong to botnet will start on-boot in case operating system start/restarts. Please note that if IntelMQ is configured with `init_system: intelmq`, botnet cannot start on-boot because it relies on PID files, not on init system management like systemd.

## Commands

Principles:
1. .runtime.conf always have the last successfully runtime configuration
2. the user first MUST to stop and then remove the configuration, not the opposite


intelmqctl start
    iterate over all bots in .runtime.conf with `botnet: True`
        if in runtime.conf
            pass
        if not in runtime.conf and running
            the bot will be stopped using the old `.runtime.conf` and additionally the runtime configuration of the (previously removed) bot will be again written to the current `runtime.conf`. 
    iterate over all bots in runtime.conf with `botnet: True`
        if running:
            pass
        if not running:
            start
            update .runtime.conf
        add bot to .runtime.conf

intelmqctl stop
    iterate over all bots in .runtime.conf with `botnet: True`
        stop bot
        if not in runtime.conf
            the runtime.conf configuration of the (previously removed) bot will be again written to the current `runtime.conf`. .
    iterate over all bots in runtime.conf with `botnet: True`
        if running:
            stop

intelmqctl restart
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl restart `<bot_id>`

intelmqctl reload
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl reload `<bot_id>`

intelmqctl status
    bot_id | run_mode | scheduled_time (if applicable) | is on botnet | status | enabled_on_boot


# On-boot commands

intelmqctl enable
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl enable `<bot_id>`

intelmqctl disable
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl disable `<bot_id>`

# Other commands

intelmqctl check-config
    will perform usual checks on config, including compare the past runtime.conf with the new one and see if bots which are running were removed from the new runtime.conf without being stopped properly.

intelmqctl list
    bot_id | run_mode | scheduled_time (if applicable) | is on botnet






# Issues

## Issue 1 - Where to store `init_system` config parameter

**Issue:** where and how we will store the configuration parameter `init_system`? on runtime.conf? per each bot? 

**Proposal:** TBD
