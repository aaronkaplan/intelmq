Table of Contents
=================

   * [Table of Contents](#table-of-contents)
   * [Definitions](#definitions)
   * [Concepts](#concepts)
      * [Process management](#process-management)
      * [Botnet](#botnet)
      * [Onboot](#onboot)
      * [Run mode](#run-mode)
      * [Run Modes with Process Management](#run-modes-with-process-management)
      * [Configurations (admin vs internal)](#configurations-admin-vs-internal)
         * [Configurations Check Procedure](#configurations-check-procedure)
   * [intelmqctl](#intelmqctl)
      * [intelmqctl start &lt;bot_id&gt;](#intelmqctl-start-bot_id)
      * [intelmqctl stop &lt;bot_id&gt;](#intelmqctl-stop-bot_id)
      * [intelmqctl restart &lt;bot_id&gt;](#intelmqctl-restart-bot_id)
         * [General procedure](#general-procedure)
      * [intelmqctl reload &lt;bot_id&gt;](#intelmqctl-reload-bot_id)
         * [General procedure](#general-procedure-1)
         * [Specific procedure](#specific-procedure)
      * [intelmqctl configtest ](#intelmqctl-configtest-)
         * [General procedure](#general-procedure-2)
      * [intelctl status &lt;bot_id&gt;](#intelctl-status-bot_id)
         * [General procedure](#general-procedure-3)
         * [Specific Procedure](#specific-procedure-1)
      * [intelmqctl enable &lt;bot_id&gt;](#intelmqctl-enable-bot_id)
         * [General procedure](#general-procedure-4)
         * [Specific Procedure](#specific-procedure-2)
      * [intelmqctl disable &lt;bot_id&gt;](#intelmqctl-disable-bot_id)
         * [General procedure](#general-procedure-5)
         * [Specific Procedure](#specific-procedure-3)
      * [intelmqctl add-to-botnet &lt;bot_id&gt;](#intelmqctl-add-to-botnet-bot_id)
         * [General procedure](#general-procedure-6)
         * [Specific Procedure](#specific-procedure-4)
      * [intelmqctl remove-from-botnet &lt;bot_id&gt;](#intelmqctl-remove-from-botnet-bot_id)
         * [General procedure](#general-procedure-7)
         * [Specific Procedure](#specific-procedure-5)
   * [Botnet commands](#botnet-commands)
      * [Overview](#overview)
      * [Commands](#commands)
         * [Flags](#flags)
         * [FIXME](#fixme)
   * [On-boot commands](#on-boot-commands)
   * [Other commands](#other-commands)
   * [Scenarios](#scenarios)
         * [Scenario 1 - botnet start command after bot configuration was manually removed](#scenario-1---botnet-start-command-after-bot-configuration-was-manually-removed)
         * [Scenario 2 - botnet stop command after bot configuration was manually removed](#scenario-2---botnet-stop-command-after-bot-configuration-was-manually-removed)
         * [Scenario 3 - botnet reload command after bot configuration was manually removed](#scenario-3---botnet-reload-command-after-bot-configuration-was-manually-removed)
         * [Scenario 4 - botnet status command after bot configuration was manually removed](#scenario-4---botnet-status-command-after-bot-configuration-was-manually-removed)
   * [Issues](#issues)
      * [Issue 1 - Where to store init_system configuration parameter](#issue-1---where-to-store-init_system-configuration-parameter)
   * [TODO](#todo)
      * [Issues related to TODO that need to be discussed](#issues-related-to-todo-that-need-to-be-discussed)
         * [Debug related command](#debug-related-command)



# Definitions

* **system:** system on this proposal means IntelMQ system.
* **operating system:** operating system on this proposal means the operating systems currently supported by IntelMQ.
* **production environment:** system that belongs to production environment is considered a system that should never stop and should work properly all the time.
* **{runtime, defaults, pipeline} configuration:** term to mention the configuration without specifying if internal or admin configuration because is not required for the explanation since it's not revelevant.
* **admin {runtime, defaults, pipeline} configuration:** a configuration file used by IntelMQ sysadmin and also used by intelmqctl.
* **internal {runtime, defaults, pipeline} configuration:** a hidden configuration file only used by intelmqctl to track of the last successfully configuration used to perform some action through intelmqctl. This file is located in `/var/run/intelmq/` and should not be manually changed.
* **`process_manager: "pid/systemd"`**: is a parameter on defaults configuration which will define the process manager that IntelMQ will use to manage the bots.
* **`botnet: true/false`** is a parameter of runtime configuration per each bot to define if a bot is part of the botnet or not.
* **`onboot: true/false`** is a parameter of runtime configuration per each bot to define if a bot will start on boot.
* **`botnet_onboot: true/false`** is a parameter of defaults configuration which will define if the bots configured as part of the botnet will start onboot.
* **`run_mode: <scheduled/stream>`** is a parameter of runtime configuration per each bot to define how bot should run.
 - **`stream`:** this value will allow the bot to run and process messages indefinitely.
 - **`scheduled`:** this value will allow the bot to start at `schedule_time` (bot parameter), run one successfully time and then exit.
* **`schedule_time`:** is a parameter of runtime configuration per each bot to define in which specific scheduled time the bot should run  This parameter needs to be defined using crontab syntax. Please note that this parameter is only applicable to bots configured as `scheduled` run_mode.

# Concepts

## Process management

Process management on IntelMQ has two modes on this proposal: systemd and PID. Changing on IntelMQ configuration the process management to PID will work as always worked before. Using systemd to do process management will rely on systemd to manage the IntelMQ system.

**on defaults configuration:**
```
{
    ...
    "process_manager": "< pid / systemd >"
    ...
}
```

## Botnet

Botnet is a concept which have the following principles:

* botnet is a group of bots which are configured with a parameter `botnet: True`.
* each bot that belongs to botnet should be considered as a bot working and running properly in a organization production environment.

**Note:** IntelMQ system provides a mechanism to execute just in one command (e.g start/stop/restart/reload/status) actions to all bots which belong to botnet (independently of the `run_mode` parameter). Please check additional information related to this process on each botnet action.

**on runtime configuration:**
```
    "abusech-domain-parser": {
        ...
        "parameters": {
            "botnet": true
        }
    }
```

## Onboot

An IntelMQ bot or botnet configured with onboot enabled will start automatically when operating system starts.

**Note:** only using systemd as process management will allow bots to run onboot, therefore, if IntelMQ system is configured with PID as process management, the `onboot` runtime configuration parameter will be completely ignored by the system. The reason why PID process management on boot is not including on this proposal is due the lack of reliability of PID files being used in a production system.

**Bot onboot on runtime configuration**
```
    "abusech-domain-parser": {
        ...
        "parameters": {
            "onboot": true
        }
    }
```

**Botnet onboot on defaults configuration:**
```
{
    ...
    "botnet_onboot": true
    ...
}
```

## Run mode

Each bot can be configured with a specific run mode such as:
* **Stream:** bot will run and process messages indefinitely.
* **Scheduled:** bot will start at the defined `schedule_time`, run one successfully time and then exit.

**on runtime configuration:**
```
    "abusech-domain-parser": {
        ...
        "parameters": {
            "run_mode": "< stream / scheduled >"
        }
    }
```

## Run Modes with Process Management

`FIXME`: will be fun to explain this uuhuhuh - is required to explain how bots configured with scheduled mode and NOT onboot will be not be start onboot, even after a system crash when these bots were on crontab because someone started them without wanting them to start onboot. TL;DR onboot a special service on systemd will rewrite all crontab configuration before crontab service starts.



## Configurations (admin vs internal)

The usual configurations files will now be copied every time `intelmqctl` successfully run to an hidden files located on `/var/run/intelmq`. The reason why `intelmqctl` will always keep a successfully running state version of admin configurations, as we call it, the internal configurations, is to prevent bad configurations changes on admin configuration files which can put the IntelMQ in a unstable mode. **However**, from a usual admin perspective, there is no need to be aware of this because are just internal files and an internal procedure used by intelmqctl to manage the system. In situations where intelmqctl detects some insconsitence in the current running state and the admin configurations, intelmqctl will require action from admin if intelmqctl is being run in interactive mode or if not, will be available the possibility to specify flags to automatically perform the actions without need interaction.

In a nutshell, intelmqctl will always have a copy of the three main configuration files (runtime.conf, defaults.conf and pipeline.conf) and will use them to detect possible issues, such as, bots which are running but not being managed since they were removed manually from configuration files.


### Configurations Check Procedure
intelmqctl will always perform the normal checks between internal runtime configuration and admin runtime configuration for all bots even if the `intelmqctl` command was executed just to only one bot. This checks will allow the sysadmin to be aware that something is wrong with the configuration even if sysadmin is executing other command with intelmqctl, therefore, a warning message will always show in the end of the command output.


# intelmqctl

By default, all commands will perform the action in background, not in foreground.

**Note:** `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed. 

**Flags:**

* `--now`: this parameter will execute the bot automatically when the start action is perform, respecting the `run_mode`. This means:
 * if bot is configured with runtime parameter `run_mode: stream`, the bot will start and execute indefinetly, if 
 * if bot is configured with runtime parameter `run_mode: scheduled`, the bot will start and execute one time successfully (oneshot) and exit. 
* `--debug`: debug is a mode to run the bot in foreground. `FIXME`: need to think about the schedule mode scenario.


## intelmqctl start `<bot_id>`

**Command:**

```
intelmqctl start `<bot_id>`
```

**Procedure:**

* `intelmqctl` will not perform any action to a bot which is already running.
* if Run mode: stream
  - if Process manager: PID
    - intelmqctl will check if there is a PID file
    - if PID file exists, do nothing
    - if PID file does not exist, execute start action on bot and write PID file
  - if Process manager: systemd
    - execute `systemctl start <module@bot_id>`
* if Run mode: scheduled
  - if Process manager: PID or systemd
    - intelmqctl will check if crontab configuration line for the bot is already on crontab:
     - if crontab configuration line exists, do nothing. In the end, write a log message "bot is already running"
     - if crontab configuration line does not exists, add configuration line on crontab such as `<schedule_time> <intelmq bot module> <bot_id> # <bot_id>`. In the end, write a log message "bot is schedule and will run at this time: `* * * * * `"


## intelmqctl stop `<bot_id>`

**Command:**

```
intelmqct stop `<bot_id>`
```

**Procedure:**

* `intelmqctl` will not perform any action to a bot which is already stopped.
* if Run mode: stream
  - if Process manager: PID
    - intelmqctl will check if there is a PID file
    - if PID file exists, execute stop action on the bot and remove PID file
    - if PID file does not exist, do nothing
  - if Process manager: systemd
    - execute `systemctl stop <module@bot_id>`
* if Run mode: scheduled
  - if Process manager: PID or systemd
    - intelmqctl will check if crontab configuration line for the bot is still on crontab
    - if crontab configuration line exists, remove configuration line on crontab. In the end, write a log message "bot is unschedule."
    - if crontab configuration line does not exists, do nothing. In the end, write a log message "bot is already stopped"


## intelmqctl restart `<bot_id>`

**Command:**

```
intelmqctl restart `<bot_id>`
```

**Procedure:**

* `intelmqctl` will use the stop action command and start action command to perform the restart, therefore, there is no additional information required here, is only to actions commands being executed already explained.



## intelmqctl reload `<bot_id>`

**Command:**

```
intelmqctl reload `<bot_id>`
```

**Procedure:**

* `intelmqctl` will perform additional checks in order to handle some issues related to correct procedures which may not being followed by admin. The checks will be described in this section. 

* if `<bot_id>` has a new `run_mode` value AND `<bot_id>` is running:
  - raise message "`<bot_id>` is configured with a new `run_mode` therefore cannot be reload and it requires to be restarted in order to reload the new configuration. Do you want to restart the bot to apply the new `run_mode`? [Y/n]"
    - "[Y] `intelmqctl` will automatically execute restart action on the bot and the bot will start with the new configuration" \
    - "[N] `intelmqctl` will not perform any action, therefore bot will keep running in the current run state.
* else:
  * Run mode: stream
    - Process manager: PID
      - intelmqctl will check if there is a PID file
      - if PID file exists, execute reload action on the bot
      - if PID file does not exist, do nothing
    - Process manager: systemd
      - execute `systemctl reload <module@bot_id>` (this action will be automatically specified in systemd template service file)
  * Run mode: scheduled
    - Process manager: PID or systemd
      - intelmqctl will check if crontab configuration line for the bot is still on crontab:
        - if crontab configuration line exists, replate it and log a message explaining the update action.
        - if crontab configuration line does not exists, add it and log a message explaining the update action.
      **Note**: if a scheduled bot is running the reload action will be ignored until the next bot execution.

**Please note** the above explanation is exemplifying an interactive mode of intelmqctl, however, there will be available additional parameters to automatically answer the questions which will allow to execute this command by scripts or other tools.


## intelmqctl configtest <bot_id>

**Command:**
```
intelmqctl configtest <bot_id>
```

**Procedure:**

* there are 2 types of checks. check if json is ok and check if parameters of bots are ok.
 * for json check should give a generic message in case of something is failing saying "json is bad"
 * for bot check should give a generic message in case of something is failing saying "bot config is bad because ..."


## intelctl status `<bot_id>`

**Command:**
```
intelctl status `<bot_id>`
```

**Procedure:**

* Run mode: stream
  - Process manager: PID
    - intelmqctl will check if there is a PID file
      - if PID file exists, log message saying the current status is "running"
      - if PID file does not exists, log message saying the current status is "not running"
  - Process manager: systemd
    - execute `systemctl status <module@bot_id>`
* Run mode: scheduled
  - Process manager: PID or systemd
    - intelmqctl will check if bot is configured on crontab
      - if configured on crontab, log message saying the current status is "running"
      - if not configured on crontab, log message saying the current status is "not running"

**Ouput Proposal Example 1:**

| bot_id    | run_mode    | scheduled_time (if applicable) | is on botnet | status             | enabled_on_boot | configtest   |
|-----------|-------------|--------------------------------|--------------|--------------------|-----------------|--------------|
| my-bot-1  | stream      | -                              | true         | running            | yes             | valid        |

Also intelmqctl should print the last 10 log lines from the log of this bot.

**Ouput Proposal Example 2:**

| bot_id    | run_mode    | scheduled_time (if applicable) | is on botnet | status             | enabled_on_boot | configtest   |
|-----------|-------------|--------------------------------|--------------|--------------------|-----------------|--------------|
| my-bot-2  | scheduled   | 1 * * * *                      | false        | running (unstable) | no              | invalid      |

Also intelmqctl should print the last 10 log lines from the log of this bot.


## intelmqctl enable `<bot_id>`

**Command:**
```
intelctl enable `<bot_id>`
```

**Procedure:**

* `intelmqctl` perform the usual checks and if no errors found, `intelmqctl` will configure the runtime configuration for the <bot_id> accordingly to the following procedure:

* Run mode: stream
  - Process manager: PID
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ does not support onboot configuration in PID process management. Please use systemd process management"
  - Process manager: systemd
    - execute `systemctl enable <module@bot_id>`
    - intelmqctl will change `onboot` configuration parameter to `true` value.
* Run mode: scheduled
  - Process manager: PID
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ does not support onboot configuration in PID process management. Please use systemd process management"
  - Process manager: systemd
    - intelmqctl will change `onboot` configuration parameter to `true` value.
    - intelmqctl will not perform any other action because there is a `intelmq.scheduled_bots_on_boot.service` which is always enable and will automatically write the crontab configuration accordingly to the all bots configured as `run_mode: scheduled` and `onboot: true`, therefore will write on crontab configuration the correct crontab entry to this bot enabled onboot. For more information please read "Run Modes with Process Management concept" section.


## intelmqctl disable `<bot_id>`

**Command:**
```
intelctl disable `<bot_id>`
```

**Procedure:**

* `intelmqctl` perform the usual checks and if no errors found, `intelmqctl` will configure the runtime configuration for the <bot_id> accordingly to the following procedure:

* Run mode: stream
  - Process manager: PID
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ does not support onboot configuration in PID process management. Please use systemd process management"
  - Process manager: systemd
    - execute `systemctl disable <module@bot_id>`
    - intelmqctl will change `onboot` configuration parameter to `false` value.
* Run mode: scheduled
  - Process manager: PID
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ does not support onboot configuration in PID process management. Please use systemd process management"
  - Process manager: systemd
    - intelmqctl will change `onboot` configuration parameter to `false` value.
    - intelmqctl will not perform any other action because there is a `intelmq.scheduled_bots_on_boot.service` which is always enable and will automatically write the crontab configuration accordingly to the all bots configured as `run_mode: scheduled` and `onboot: true`, therefore will not write on crontab configuration anything related to this bot disabled onboot. For more information please read "Run Modes with Process Management concept" section.


## intelmqctl add-to-botnet `<bot_id>`

**Command:**
```
intelctl add-to-botnet `<bot_id>`
```

**Procedure:**

* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: true`, independently of the `run_mode` and `process_manager` configuration parameter.
* `intelmqctl` will not perform any other actions because this `add-to-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.
* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to add the bot to the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"


## intelmqctl remove-from-botnet `<bot_id>`

**Command:**
```
intelctl remove-from-botnet `<bot_id>`
```

**Procedure:**

* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: false`, independently of the `run_mode` and `process_manager` configuration parameter.
* `intelmqctl` will not perform any other actions because this `remove-from-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.
* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to remove the bot from the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"



# Botnet commands

## Overview

Only bots which are part of the botnet can be start/stop/restart/reload/status with botnet commands. Please note that if IntelMQ is configured with `init_system: PID`, botnet cannot start on-boot because it relies on PID files, not on init system management like systemd.

**Please, ensure that you have good understand about botnet concept (see Definitions section for more information), otherwise can be misleading.

## Commands

Principles:
1. .runtime.conf always have the last successfully runtime configuration
2. the user first MUST to stop and then remove the configuration, not the opposite


### Flags

* `intelmqctl start --stream-bots`
* `intelmqctl start --scheduled-bots`

### FIXME

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
    bot_id | run_mode | scheduled_time (if applicable) | status | enabled_on_boot | configtest

    DO NOT log the last 10 lines per each bot, too much!!!



`FIXME`: we also need a command to show the status or even other actions to all bots, including the ones that does not belong to botnet.


# On-boot commands

intelmqctl enable
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl enable `<bot_id>`

intelmqctl disable
    iterate over all bots in .runtime.conf with `botnet: True` and for each one execute `intelmqctl disable `<bot_id>`

# Other commands

intelmqctl configtest
     will perform usual checks on configuration, including compare the past runtime.conf with the new one and see if bots which are running were removed from the new runtime.conf without being stopped properly.

intelmqctl list
    bot_id | run_mode | scheduled_time (if applicable) | is on botnet








# Scenarios

### Scenario 1 - botnet start command after bot configuration was manually removed

Please note that this scenario is using botnet commands, therefore, it's crutial to have a good understand about botnet concept. Also, every single mentioned to "bots", except mentioned explicity, means bots which are part of the botnet.

1. In this case there are 10 bots configured as `botnet: True`. Admin execute the command to start the botnet.
2. Admin accidentally remove manually a bot with `bot_id: my-bot-1` from admin runtime configuration without stopping it previously.
3. Admin add manually a new bot with `bot_id: my-bot-2` to admin runtime configuration.
4. Admin execute the command to start the botnet which will do the following:
 1. do nothing to the bots which were already started in the first execution of the command to start the botnet
 2. execute start command following normal procedure to the `bot_id: my-bot-2` and intelmqctl will update the internal runtime configuration accordingly.
 3. keep the bot with `bot_id: my-bot-1` running but will also add the configuration stored in internal runtime configuration to the admin runtime configuration in order to prevent possible loss of bot configuration by this user mistake (not following the correct procedure).
 4. log a warning message providing information to the admin explaining the situation: "intelmqctl detected that bot my-bot-1 is still running but has been removed from user runtime configuration. intelmqctl added it to the user runtime configuration. Please first stop the bot, and remove it afterwards.".

The **correct procedure** is stop bot first and then remove bot configuration from admin runtime configuration.

### Scenario 2 - botnet stop command after bot configuration was manually removed

Please note that this scenario is using botnet commands, therefore, it's crutial to have a good understand about botnet concept. Also, every single mentioned to "bots", except mentioned explicity, means bots which are part of the botnet.

1. In this case there are 10 bots configured as `botnet: True`. Admin execute the command to start the botnet.
2. Admin accidentally remove manually a bot with `bot_id: my-bot-1` from admin runtime configuration without stopping it previously.
3. Admin execute the command stop one of the bots with `bot_id: my-bot-2` already configured bot in runtime configuration.
5. Admin change manually a completely new admin runtime configuration to the bot with `bot_id: my-bot-3` which was already configured with other configuration parameters.
6. Admin execute the command to stop the botnet which will do the following:
 1. do nothing to the bots which were already stopped, in this specific scenario, nothing will perform to the bot with `bot_id: my-bot-2`
 2. do nothing to the bots which never started, in this specific scenario, nothing will perform to the new bot with `bot_id: my-bot-3` which was only added to the admin runtime configuration steps before.
 2. execute stop command following normal procedure to all configured bots on admin runtime configuration which are still running, in this scenario, this action will not be applicable to the bots: `bot_id: my-bot-1`, `bot_id: my-bot-2` and `bot_id: my-bot-3`.
 3. execute stop command to the bot `bot_id: my-bot-1` and also add the configuration stored in internal runtime configuration to the admin runtime configuration in order to prevent possible loss of bot configuration by this user mistake (not following the correct procedure).
 4. log a warning message providing information to the admin explaining the situation: "intelmqctl detected that bot with `bot_id: my-bot-1` is was running but has been removed from admin runtime configuration. intelmqctl stopped it and added it to the admin runtime configuration. Please first stop the bot, and remove it afterwards.".

The **correct procedure** is stop bot first and then remove bot configuration from admin runtime configuration.


### Scenario 3 - botnet reload command after bot configuration was manually removed

Please note that this scenario is using botnet commands, therefore, it's crutial to have a good understand about botnet concept. Also, every single mentioned to "bots", except mentioned explicity, means bots which are part of the botnet.

1. In this case there are 10 bots configured as `botnet: True`. Admin execute the command to start the botnet.
2. Admin execute the command to stop a bot with `bot_id: my-bot-1`.
3. Admin accidentally remove manually a bot with `bot_id: my-bot-2` from admin runtime configuration without stopping it previously.
4. Admin execute the command to reload the botnet which will do the following:
 1. do nothing to the bots which are stopped, in this specific scenario, nothing will perform to the bot with `bot_id: my-bot-1`
 2. execute reload command following normal procedure to all configured bots on admin runtime configuration which are still running, in this specific scenario, will perform to all bots except the bots with `bot_id: my-bot-1` and `bot_id: my-bot-2`.
 3. log a warning message providing information to the admin explaining the situation: "intelmqct detected that bot with `bot_id: my-bot-2` is still running but has been removed from admin runtime configuration."
 4. in interactive mode, intelmqctl will ask the following question: "Do you want to stop the bot with `bot_id: my-bot-2`? [N/y]"

  * if "Y", intelmqctl remove the bot configuration from runtime configuration (internal and admin configurations) and also check in all IntelMQ system if there is some additional internal configurations that are still having configured that bot.
  * if "N", intelmqctl add the bot configuration stored in internal runtime configuration to the admin runtime configuration in order to keep the admin runtime configuration up to date accordingly.

The **correct procedure** is stop bot first and then remove bot configuration from admin runtime configuration.


### Scenario 4 - botnet status command after bot configuration was manually removed

Please note that this scenario is using botnet commands, therefore, it's crutial to have a good understand about botnet concept. Also, every single mentioned to "bots", except mentioned explicity, means bots which are part of the botnet.

1. In this case there are 10 bots configured as `botnet: True`. Admin execute the command to start the botnet.
2. Admin accidentally remove manually a bot with `bot_id: my-bot-1` from admin runtime configuration without stopping it previously.
3. Admin add manually a bot with `bot_id: my-bot-666` to admin runtime configuration with the configuration parameter `botnet: True`.
3. Admin execute the command to status the botnet which will do the following:
 * execute status command and for each specific situation do the following:
  1. log a message providing information to the admin explaining that bot with `bot_id: my-bot-666` is with stopped status.
  2. log a message providing information to the admin explaining that all the other bots, except the bot with `bot_id: my-bot-1`, are with running status.
  3. log a message providing information to the admin explaining that bot with `bot_id: my-bot-1` is with unstable running status, due the missing bot configuration on admin runtime configuration.
  `FIXME`: what do we should suggest to the user to fix the problem? Should we just print the bot configuration from internal runtime configuration and ask the user to copy and paste? OR say to run `intelmqctl stop my-bot-1 --force`
  

The **correct procedure** is stop bot first and then remove bot configuration from admin runtime configuration.












# Issues

## Issue 1 - Where to store `init_system` configuration parameter

**Issue:** where and how we will store the configuration parameter `init_system`? on runtime.conf? per each bot? 

**Proposal:** TBD




# TODO

1. internal runtime configuration MUST be stored in /var/run/ location
2. internal runtime configuration cannot be called as configuration, should be called like 'current effective state of configuration' or other best name in order to not create confusion and be clear to the person who will read this documentation.
3. pipeline.conf MUST also follow the same procedure of backingup because its another point of failure due admin mistakes.
4. Create a diagram of the architecture of all process management systemd e
5. we might need to rename the defaults.conf file. Some parameters on defaults.conf in reality MUST not be possible to overwrite them per each bot or the system will be COMPLETELY UNSTABLE.

## Issues related to TODO that need to be discussed

* re 2. calling the current state is a problem because when admin perform add-to-botnet the botnet parameter will change in admin runtime configuration but the internal runtime configuration still have the old value. So, I think WE MUST add to that commands `add-to-botnet` and `remove-from-botnet` the internal action of update the internal runtime configuration.





NOTE: removing a bot from botnet means two important things:
        1. you will continue to be able to execute start/stop/restart/reload/status botnet commands but these commands will NOT be applied to this bot that you removing from the botnet.
        2. if your IntelMQ is not configured with `init_system: intelmq`, instead is configured with `init_system: systemd`, this bot which you are removing from botnet will NOT start automatically on operating system boot (on-boot) in case operating system restarts for some reason.


### Debug related command

**FIXME**: Do we still need this mode or we just need to add a flag to start action command?
```
intelmqctl debug `<bot_id>`
    ignore run_mode and do:
        check if `intelmqctl status `<bot_id>` and:
            if True:
                raise message "cannot debug bot because bot_id is running or is scheduled", also say that bot needs to be removed from botnet with `intelmqctl del <bot_id>` (just to prevent issues that we don't expect)
            else:
                execute the bot using ONLY the PID approach, log the lines to stdout and wait for CTRL+C
```