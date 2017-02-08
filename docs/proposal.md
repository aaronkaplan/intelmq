

# Proposal

## Configurations Required
```
{
    init_system: `<intelmq / systemd>`
    run_mode: `<stream / scheduled>`
    scheduled_time: "* * * * *"
    botnet: True/False
}
```
**Note:** `enable` parameter as implemented in the current version of IntelMQ was removed in this proposal and was replaced by `botnet` parameter. Please see 'Overview' in 'Botnet Commands' section.


## Bot commands

Bot commands are commands which can only apply to one bot therefore requires a `<bot_id>`. The commands start/stop/restart/reload/status are the usual commands, however there are more commands implemented such as `add`, `rem`, `debug` and `scheduler-exec` which have a specific context explained in the following description of each command.

### Usual commands

intelmqctl start `<bot_id>`
    stream
        PID - execute bot and write PID file
        SYSTEMMD - execute `systemctl start <module@bot_id>`
    scheduled
        add config line on crontab with intelmqscheduler (message: bot is schedule and will run at `<* * * * * >`)

intelmqctl stop `<bot_id>`
    stream
        PID - send SIGKILL to bot and remove PID file
        SYSTEMMD - execute `systemctl stop `<module@bot_id>`
    scheduled
        send SIGKILL to intelmqscheduler and delete config line on crontab (message: bot is unschedule and will run at `<* * * * * >`)

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
        send SIGHUP to intelmqscheduler??!?!?! or send a message saying that will only apply to the next execution if there is current one executing.
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


### Botnet related commands

intelmqctl add `<bot_id>`
    stream
        PID - change botnet parameter to True
        SYSTEMD - change botnet parameter to True and execute `systemctl enable `<module@bot_id.service>` (beloging to botnet also means enable on-boot except if `init_system: intelmq`)
    scheduled
        change botnet parameter to True and ....  NEED TO REWRITE THIS  .... execute `systemctl enable intelmq.botnet.crontab.service` to enable on boot with systemd like the rest of the botnet

    NOTE: adding a bot to botnet means two important things:
        1. you will be able to execute start/stop/restart/reload/status botnet commands which will apply to all bots that belong to the botnet including this one that you are adding to the botnet.
        2. if your IntelMQ is not configured with `init_system: intelmq`, instead is configured with `init_system: systemd`, all bots which belong to botnet will start automatically on operating system boot (on-boot) in case operating system restarts for some reason.

    -- begin DO NOT READ THIS
    Note: always have a service (`intelmq.crontab_check.service`) that only run on boot, before crontab service start, to check if there is any line on crontab with a bot that does no belong to botnet, which means, cannot start on boot, because only bots configured as botnet will automatically and always start on boot.

    intelmqscheduler --on-boot `<module@bot_id>`   # will read runtime.conf, get all scheduled bots and write crontab_scheduled.conf and execute `systemctl enable intelmq.botnet.crontab.service`, and this service will have scheduler run for each bot. Also, we MAY implement the services with %i as service parameter like we are doing with stream bots configured with systemd. ISSUE: there is a problem with this solution because it relies on systemd, which means that crontab on boot will always use the init_system configured on runtime.conf.
    -- end DO NOT READ THIS

intelmqctl rem `<bot_id>`
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
                raise message "cannot debug bot because bot_id is running or is scheduled", also say that bot needs to be removed from botnet with `intelmqctl del `<bot_id>` (just to prevent issues that we don't expect)
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

intelmqctl start
    iterate to all bots and for each one execute `systemctl start `<bot_id>`

intelmqctl stop
    iterate to all bots and for each one execute `systemctl stop `<bot_id>`

intelmqctl restart
    iterate to all bots and for each one execute `systemctl restart `<bot_id>`

intelmqctl reload
    iterate to all bots and for each one execute `systemctl reload `<bot_id>`

intelmqctl status
    bot_id | run_mode | scheduled_time (if applicable) | is on botnet | status | enabled_on_boot




# Other commands

intelmqctl check-config
    will perform usual checks on config, including compare the past runtime.conf with the new one and see if bots which are running were removed from the new runtime.conf without being stopped properly.

intelmqctl list
    bot_id | run_mode | scheduled_time (if applicable) | is on botnet






# Issues

## Issue 1 - Where to store `init_system` config parameter

**Issue:** where and how we will store the configuration parameter `init_system`? on runtime.conf? per each bot? 

**Proposal:** TBD
