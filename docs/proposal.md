# Definitions

## Generic definitions

`system`: system on this proposal means IntelMQ system.
`operating system`: operating system on this proposal means the operating systems currently supported by IntelMQ.

## Botnet concepts

**botnet:** is a concept which have the following principles:

* botnet is a group of bots which are configured with a parameter `botnet: True`.
* IntelMQ system provides a mechanism to execute just in one command (e.g start/stop/restart/reload/status) actions to all bots which belong to botnet (independently of the `run_mode` parameter). Please check additional information related to this process on each botnet action.

## Process management concept

* Process management on IntelMQ has two modes on this proposal: systemd and PID. Changing on IntelMQ configuration the process management to PID will work as always worked before. Using systemd to do process management will rely on systemd to manage the IntelMQ system.

* **Please note** that only using systemd as process management will allow bots to run onboot, therefore, if IntelMQ system is configured with PID as process management, the `onboot` runtime configuration parameter will be completely ignored by the system. The reason why PID process management on boot is not including on this proposal is due the reliability of PID files being used in a production system.

## Run mode concept

* The run modes of IntelMQ are: stream and scheduled.
 * **Stream:** TBD
 * **Scheduled:** TBD

## Run Modes with Process Management concept

* `FIXME`: will be fun to explain this uuhuhuh


## Configuration concepts

* **runtime configuration:** term to mention the configuration file of the bots without specifying if internal or admin runtime configuration because is not required for the explanation since it's transversal.
* **user runtime configuration:** `runtime.conf`, a configuration file used by user to configure bots and also used by intelmqctl to manage the bots.
* **internal runtime configuration:** `.runtime.conf`, a hidden configuration file only used by intelmqctl to track the last successfully configuration used to run bot(s). This file is located in same directory as admin runtime configuration. Please note that bots configured in this configuration does NOT mean that they are running, it only means that this configuration was successfully used to the last intelmqctl action.
* **defaults configuration:** TBD

Having two runtime configurations as mentioned before is important to scenarios that are present in the following sub-sections. **Please note** that these sub-sections intend to give to the admin a better understanding of how and why intelmqctl keep track of bots that are running and their configurations. The quick explanation is `intelmqctl` will always keep a currently running state version of admin runtime configuration on a specific file named accordingly to definitions section, internal runtime configuration,  which is always generated after every `intelmqctl` action command such as `start`, `stop`, etc. **However**, from a usual admin perspective, there is no need to be aware of this because is just an internal file and an internal procedure used by intelmqctl to manage the system. In situations where intelmqctl detects some insconsitence in the current running state and the admin runtime configuration, intelmqctl will require action from admin if intelmqctl is being run in interactive mode or if not, will be available the possibility to specify flags to automatically perform the actions without need interaction.

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


## Runtime configuration parameters

* **`botnet: true/false`** is a parameter on configuration per each bot to define if a bot is part of the botnet or not.
* **`onboot: true/false`** is a parameter on configuration per each bot to define if a bot will be started on boot.
* **`process_manager: "pid/systemd"`**: is a parameter on defaults configuration to be used internally by intelmqctl.
* **`run_mode: <scheduled/stream>`** is a parameter on configuration per each bot to define how bot should run.
 - **`stream`:** run indefinitely
 - **`scheduled`:** is a parameter on configuration per each bot to define when the bot MUST start and run one time successfully and then exit. This mode will internally use crontab to start the bot.
* **`schedule_time`:** is a parameter on configuration per each bot to define in which specific scheduled time (`schedule_time` parameter) the bot should run  This parameter needs to be defined using crontab syntax. Please note that this parameter is only applicable to bots configured as `scheduled` run_mode.


# Bot commands

Bot commands are commands which can only apply to one bot therefore requires a `<bot_id>`. The commands start/stop/restart/reload/status are the usual commands, however there are more commands implemented such as `enable`, `disable`, `add-to-botnet`, `remove-from-botnet`, `debug` and `scheduler-exec` which have a specific context explained in the following description of each command.


## Usual commands

### intelmqctl start `<bot_id>`

#### Command

```
intelmqctl start `<bot_id>`
```

**Note:** by default, all commands will perform the action in background, not in foreground.

##### Flags

* `--now`: this parameter will execute the bot automatically when the start action is perform, respecting the `run_mode`. This means:
 * if bot is configured with runtime parameter `run_mode: stream`, the bot will start and execute indefinetly, if 
 * if bot is configured with runtime parameter `run_mode: scheduled`, the bot will start and execute one time successfully (oneshot) and exit. 
* `--debug`: debug is a mode to run the bot in foreground. `FIXME`: need to think about the schedule mode scenario.

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will not perform any action to a bot which is already running.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section. For example, if configuration parameters were changed, intelmqctl will detect that and will log a message "To reload the new configuration, please execute reload action command.".

#### Specific procedure

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will check if there is a PID file
    - if PID file exists, do nothing
    - if PID file does not exist, execute start action on bot and write PID file
  - **Process manager: systemd**
    - execute `systemctl start <module@bot_id>`
* **Run mode: scheduled**
  - **Process manager: PID and systemd**
    - intelmqctl will check if crontab configuration line for the bot is already on crontab:
     - if crontab configuration line exists, do nothing. In the end, write a log message "bot is already running"
     - if crontab configuration line does not exists, add configuration line on crontab such as `<schedule_time> intelmq <python binary location> <intelmqctl location>/intelmqctl start <bot_id> --now # <bot_id>`. In the end, write a log message "bot is schedule and will run at this time: `* * * * * `"


### intelmqctl stop `<bot_id>`

#### Command

```
intelmqct stop `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will not perform any action to a bot which is already stopped.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.

#### Specific procedure

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will check if there is a PID file
    - if PID file exists, execute stop action on the bot and remove PID file
    - if PID file does not exist, do nothing
  - **Process manager: systemd**
    - execute `systemctl stop <module@bot_id>`
* **Run mode: scheduled**
  - **Process manager: PID and systemd**
    - intelmqctl will check if crontab configuration line for the bot is still on crontab
    - if crontab configuration line exists, remove configuration line on crontab. In the end, write a log message "bot is unschedule."
    - if crontab configuration line does not exists, do nothing. In the end, write a log message "bot is already stopped"

### intelmqctl restart `<bot_id>`

#### Command

```
intelmqctl restart `<bot_id>`
```

#### General procedure

* `intelmqctl` will use the stop action command and start action command to perform the restart, therefore, there is no additional information required here, is only to actions commands being executed already explained.



### intelmqctl reload `<bot_id>`

#### Command

```
intelmqctl reload `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will perform actions to a bot and/or runtime configuration depending on the checks results (described in `specific procedure`).
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.

#### Specific procedure

* `intelmqctl` will start perform multiple checks in order to prevent tracking issues and other possible issues related to correct procedures which are not being followed by admin. The checks will be described in this section. 

* **Please note** that the explanation is exemplifying an interactive mode of intelmqctl, however, there will be available additional parameters to automatically answer the questions which will allow to execute this command by scripts or other tools.


* **Checks:**

    * if `<bot_id>` has a new `run_mode` value AND `<bot_id>` is running:
      - raise message "`<bot_id>` is configured with a new `run_mode` therefore cannot be reload and it requires to be restarted in order to reload the new configuration. Do you want to restart the bot to apply the new `run_mode`? [Y/n]"
        - "[Y] `intelmqctl` will automatically execute restart action on the bot and the bot will start with the new configuration" \
        - "[N] `intelmqctl` will not perform any action, therefore bot will keep running in the current run state.

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will check if there is a PID file
    - if PID file exists, execute reload action on the bot
    - if PID file does not exist, do nothing
  - **Process manager: systemd**
    - execute `systemctl reload <module@bot_id>` (this action will be automatically specified in systemd template service file)
* **Run mode: scheduled**
  - **Process manager: PID and systemd**
    - intelmqctl will check if crontab configuration line for the bot is still on crontab:
      - if crontab configuration line exists, replate it and log a message explaining the update action.
      - if crontab configuration line does not exists, add it and log a message explaining the update action.
    `FIXME`: dont know what should be our procedure if a scheduled bot is running when this reload action is performing. Should reload normally like stream bots? should we just ignore it? log a message about this "finding"?
    **Sebastian said**: ignore it because the current behavior is always ignore the SIGHUP and finish the process() method, then, when it goes to the next iteration, it gets the SIGHUP and reload. HOWEVER, since schedule bots are --oneshot internally, it will always ignore, therefore, WE NEED TO DOCUMENT THIS CORRECTLY.

### intelmqctl configtest <bot_id>

#### Command
```
intelmqctl configtest <bot_id>
```

#### General procedure

* there are 2 types of checks. check if json is ok and check if parameters of bots are ok.
 * for json check should give a generic message in case of something is failing saying "json is bad"
 * for bot check should give a generic message in case of something is failing saying "bot config is bad because ..."


### intelctl status `<bot_id>`

#### Command
```
intelctl status `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.


#### Specific Procedure

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will check if there is a PID file
      - if PID file exists, log message saying the current status is "running"
      - if PID file does not exists, log message saying the current status is "not running"
  - **Process manager: systemd**
    - execute `systemctl status <module@bot_id>`
* **Run mode: scheduled**
  - **Process manager: PID and systemd**
    - intelmqctl will check if bot is configured on crontab
      - if configured on crontab, log message saying the current status is "running"
      - if not configured on crontab, log message saying the current status is "not running"

* **Ouput Proposal Example 1:**

| bot_id    | run_mode    | scheduled_time (if applicable) | is on botnet | status             | enabled_on_boot | configtest   |
|-----------|-------------|--------------------------------|--------------|--------------------|-----------------|--------------|
| my-bot-1  | stream      | -                              | true         | running            | yes             | valid        |

Also intelmqctl should print the last 10 log lines from the log of this bot.

* **Ouput Proposal Example 2:**

| bot_id    | run_mode    | scheduled_time (if applicable) | is on botnet | status             | enabled_on_boot | configtest   |
|-----------|-------------|--------------------------------|--------------|--------------------|-----------------|--------------|
| my-bot-2  | scheduled   | 1 * * * *                      | false        | running (unstable) | no              | invalid      |

Also intelmqctl should print the last 10 log lines from the log of this bot.


## On-boot related commands

### intelmqctl enable `<bot_id>`

#### Command
```
intelctl enable `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.


#### Specific Procedure

* `intelmqctl` perform the usual checks and if no errors found, `intelmqctl` will configure the runtime configuration for the <bot_id> accordingly to the following procedure:

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ is configured with process managent as PID, therefore enable a bot onboot is not supported. Please use systemd process management instead."
  - **Process manager: systemd**
    - execute `systemctl enable <module@bot_id>`
    - intelmqctl will change `onboot` configuration parameter to `true` value.
* **Run mode: scheduled**
  - **Process manager: PID**
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ is configured with process managent as PID, therefore enable a bot onboot is not supported. Please use systemd process management instead."
  - **Process manager: systemd**
    - intelmqctl will change `onboot` configuration parameter to `true` value.
    - intelmqctl will not perform any other action because there is a `intelmq.scheduled_bots_on_boot.service` which is always enable and will automatically write on crontab accordingly to the all bots configured as `run_mode: scheduled` and `onboot: true`. The command that MUST be called in order to write the crontab lines MUST be `intelmqctl start <bot-id>` where <bot-id> is the bot(s) which are configured with `onboot: true` and `run_mode: scheduled` runtime configuration parameters.

perform only onboot and oneshoot, 

### intelmqctl disable `<bot_id>`

#### Command
```
intelctl disable `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.


#### Specific Procedure

* `intelmqctl` perform the usual checks and if no errors found, `intelmqctl` will configure the runtime configuration for the <bot_id> with `onboot: false`, independently of the `run_mode` and `process_manager` configuration parameter.

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ is configured with process managent as PID, therefore enable a bot onboot is not supported. Please use systemd process management instead."
  - **Process manager: systemd**
    - execute `systemctl enable <module@bot_id>`
    - intelmqctl will change `onboot` configuration parameter to `false` value.
* **Run mode: scheduled**
  - **Process manager: PID**
    - intelmqctl will not perform any action and will change `onboot` configuration parameter to `false` value.
    - In the end, write a log message "IntelMQ is configured with process managent as PID, therefore enable a bot onboot is not supported. Please use systemd process management instead."
  - **Process manager: systemd**
    - intelmqctl will change `onboot` configuration parameter to `true` value.
    - intelmqctl will not perform any other action because there is a `intelmq.scheduled_mode.on_boot.service` which is always enable and will automatically perform only onboot and oneshoot, the overwrite of crontab accordingly to the all bots configured as `run_mode: scheduled` and `onboot: true`. The command that MUST be called in order to write the crontab lines MUST be `intelmqctl start <bot-id>` where <bot-id> is the bot(s) which are configured with `onboot: true` and `run_mode: scheduled` runtime configuration parameters.





### intelmqctl disable `<bot_id>`

#### Command
```
intelctl disable `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.


#### Specific Procedure

* `intelmqctl` perform the usual checks and if no errors found, `intelmqctl` will configure the runtime configuration for the <bot_id> with `onboot: false`, independently of the `run_mode` and `process_manager` configuration parameter.

* **Run mode: stream**
  - **Process manager: PID**
    - intelmqctl will configure crontab to not start on boot this <bot_id> removing it from crontab system.
    - `FIXME`: is this really needed? Do we think that anyone will run the system in production without using a proper process manager?
  - **Process manager: systemd**
    - execute `systemctl disable <module@bot_id>`
* **Run mode: scheduled**
  - **Process manager: PID**
    - intelmqctl will configure crontab to not start on boot this <bot_id> removing it from crontab system.
    `FIXME`: as I mentioned in the FIXME tag before, this will mix a lot in crontab. Explain verbally to Sebastian!
  - **Process manager: systemd**
    - intelmqctl will not perform any action because there is a `intelmq.scheduled_mode.on_boot.service` which is always enable and will automatically perform only onboot and oneshoot, the overwrite of crontab accordingly to the all bots configured as `run_mode: scheduled` and `onboot: true`, therefore, any bots configured as `run_mode: scheduled` and `onboot: false` will take into account by the service `intelmq.scheduled_mode.on_boot.service`.



## Botnet related commands

#### intelmqctl add-to-botnet `<bot_id>`

#### Command
```
intelctl add-to-botnet `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.

#### Specific Procedure

* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: true`, independently of the `run_mode` and `process_manager` configuration parameter.

* `intelmqctl` will not perform any other actions because this `add-to-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.

* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to add the bot to the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"

#### intelmqctl remove-from-botnet `<bot_id>`

#### Command
```
intelctl remove-from-botnet `<bot_id>`
```

#### General procedure

* `intelmqctl` will perform the normal checks between internal runtime configuration and admin runtime configuration as mentioned on "Runtime configuration concepts" section.
* `intelmqctl` will always provide the best log message in order to give additional information to admin about the actions performed according to this general procedures described here, including "Runtime configuration concepts" section.

#### Specific Procedure

* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: false`, independently of the `run_mode` and `process_manager` configuration parameter.

* `intelmqctl` will not perform any other actions because this `remove-from-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.

* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to remove the bot from the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"

`FIXME`: there is a problem here when the user enable all botnet using the botnet command and then user adds a new bot which is stopped to the botnet. How we know that user execute enable botnet command?

```
    **IMPORTANT**: intelmqctl with `init_system: systemd` will always start all botnet on-boot, therefore, there is an issue related to bots configured as scheduled mode that needs to be solve. Read the following scenario/explanation:
        Let's assume that botnet is running but there is a bot which is not part of the botnet also running with run_mode configured as scheduled. In this case it means that there is a crontab entry for that bot. However, since crontab entries are permanent, even when system reboot, the all idea about only bots that belong to botnet with `init_system: systemd` will start on-boot is broken with this scenario. So, to prevent this I propose:

        Assumptions:
            on-boot only applies, as mentioned on this documentation, to bots that belong to botnet where the botnet is configured as `init_system: systemd`. Therefore, we can use systemd to manage this issue without any problem.
        Technical details:
             In order to do this we can create a specific service named `intelmq.crontab_check.service` which will be configured to only run on-boot BEFORE crontab service starts. This service will be responsible to when the operating-system starts, to check if the current runtime configuration regarding scheduled bots matches with the current configuration on crontab. With this, bots that were running as scheduled mode before operating system restarts will be automatically removed from crontab before crontab have a chance to run them.


    NOTE: removing a bot from botnet means two important things:
        1. you will continue to be able to execute start/stop/restart/reload/status botnet commands but these commands will NOT be applied to this bot that you removing from the botnet.
        2. if your IntelMQ is not configured with `init_system: intelmq`, instead is configured with `init_system: systemd`, this bot which you are removing from botnet will NOT start automatically on operating system boot (on-boot) in case operating system restarts for some reason.
```



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






# Issues

## Issue 1 - Where to store `init_system` configuration parameter

**Issue:** where and how we will store the configuration parameter `init_system`? on runtime.conf? per each bot? 

**Proposal:** TBD




# TODO

1. internal runtime configuration MUST be stored in /var/run/ location
2. internal runtime configuration cannot be called as configuration, should be called like 'current effective state of configuration' or other best name in order to not create confusion and be clear to the person who will read this documentation.
3. pipeline.conf MUST also follow the same procedure of backingup because its another point of failure due admin mistakes.
4. Create a diagram of the architecture of all process management systemd e

## Issues related to TODO that need to be discussed

* re 2. calling the current state is a problem because when admin perform add-to-botnet the botnet parameter will change in admin runtime configuration but the internal runtime configuration still have the old value. So, I think WE MUST add to that commands `add-to-botnet` and `remove-from-botnet` the internal action of update the internal runtime configuration.


