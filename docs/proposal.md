Overall feedback
=================
  * too complicated. It tries to solve independent things at once in one document --> split it!
  * look and read job scheduluer systems (luigi, etc). There are plenty of them. We can re-use stuff!
  * missing concept: every bot MUST have a self-test and stats-component. This can be used for the ctl tool to check if the internal state of a bot is OK.
  * define test cases upfront for the new behaviour!
  * use RFC-ish MUST, MAY, SHALL
  
More comments inline marked as "XXX comment"

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
      * [intelmqctl start action](#intelmqctl-start-action)
      * [intelmqctl stop action](#intelmqctl-stop-action)
      * [intelmqctl restart action](#intelmqctl-restart-action)
      * [intelmqctl reload action](#intelmqctl-reload-action)
      * [intelmqctl configtest action](#intelmqctl-configtest-action)
      * [intelmqctl status action](#intelmqctl-status-action)
      * [intelmqctl enable action](#intelmqctl-enable-action)
      * [intelmqctl disable action](#intelmqctl-disable-action)
      * [intelmqctl add-to-botnet action](#intelmqctl-add-to-botnet-action)
      * [intelmqctl remove-from-botnet action](#intelmqctl-remove-from-botnet-action)
   * [Scenarios](#scenarios)
      * [Scenario 1](#scenario-1)
      * [Scenario 2](#scenario-2)
      * [Scenario 3](#scenario-3)


# Definitions

* **system:** system on this proposal means IntelMQ system.
* **operating system:** operating system on this proposal means the operating systems currently supported by IntelMQ.
* **production environment:** system that belongs to production environment is considered a system that should never stop and should work properly all the time.
* **{runtime, defaults, pipeline} configuration:** term to mention the configuration without specifying if internal or admin configuration because is not required for the explanation since it's not revelevant.
* **admin {runtime, defaults, pipeline} configuration:** a configuration file used by IntelMQ sysadmin and also used by intelmqctl.
XXX comment: where is this admin config? Please clarify that this is the config files which an admin MAY edit (as opposed to internal config)
* **internal {runtime, defaults, pipeline} configuration:** a hidden configuration file only used by intelmqctl to track of the last successfully configuration used to perform some action through intelmqctl. This file is located in `/var/run/intelmq/` and should not be manually changed.
* **`process_manager: "pid/systemd"`**: is a parameter on defaults configuration which will define the process manager that IntelMQ will use to manage the bots.
* **`botnet: true/false`** is a parameter of runtime configuration per each bot to define if a bot is part of the botnet or not.
* **`onboot: true/false`** is a parameter of runtime configuration per each bot to define if a bot will start on boot.
* **`botnet_onboot: true/false`** is a parameter of defaults configuration which will define if the bots configured as part of the botnet will start onboot.
XXX comment: botnet_onboot is not necessary

* **`run_mode: <scheduled/stream>`** is a parameter of runtime configuration per each bot to define how bot should run.
XXX comment: I prefer the word "continuous" to stream. 
 - **`stream`:** this value will allow the bot to run and process messages indefinitely.
 - **`scheduled`:** this value will allow the bot to start at `schedule_time` (bot parameter), run one successfully time and then exit.
* **`schedule_time`:** is a parameter of runtime configuration per each bot to define in which specific scheduled time the bot should run  This parameter needs to be defined using crontab syntax. Please note that this parameter is only applicable to bots configured as `scheduled` run_mode.

# Concepts

## Process management

Process management on IntelMQ has two modes on this proposal: systemd and PID. Changing on IntelMQ configuration the process management to PID will work as always worked before. Using systemd to do process management will rely on systemd to manage the IntelMQ system.

XXX comment: process manager is independent of run mode (in an abstract sense). Let's keep this separated.

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

XXX comment: if y ou really want to explicitly say "botnet" . How about renaming this to "configuration" since it is a configuration setup (a complete configuration) which actually gets executed. Also... I prefer that we can give names to configurations/botnets.

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

XXX comment: this is not logical why it is in the parser runtime.conf. did you mean "is_in_botnet"? But if that's the intention, I would rather say ``"botnet": <name of botnet>``.



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

XXX : not intuitively clear

## Run mode

Each bot can be configured with a specific run mode such as:
* **Stream:** bot will run and process messages indefinitely.
* **Scheduled:** bot will start at the defined `schedule_time`, run one successfully time and then exit.

XXX: see comment abouve. "continous" vs. "scheduled. Makse more sense for my feeling of english language.

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

![architecture](https://s27.postimg.org/6snypqi9v/intelmqctl_2.jpg)


XXX comment: graphics is too hard to read.

## Configurations (admin vs internal)

The usual configurations files will now be copied every time `intelmqctl` successfully run to an hidden files located on `/var/run/intelmq`. The reason why `intelmqctl` will always keep a successfully running state version of admin configurations, as we call it, the internal configurations, is to prevent bad configurations changes on admin configuration files which can put the IntelMQ in a unstable mode.

XXX comment: what happens when the two configs get out of sync for some reason? Will this be checked every time? How?

**However**, from a usual admin perspective, there is no need to be aware of this because are just internal files and an internal procedure used by intelmqctl to manage the system. In situations where intelmqctl detects some insconsitence in the current running state and the admin configurations, intelmqctl will require action from admin if intelmqctl is being run in interactive mode or if not, will be available the possibility to specify flags to automatically perform the actions without need interaction.

XXX comment: see above. How?

In a nutshell, intelmqctl will always have a copy of the three main configuration files (runtime.conf, defaults.conf and pipeline.conf) and will use them to detect possible issues, such as, bots which are running but not being managed since they were removed manually from configuration files.


### Configurations Check Procedure
intelmqctl will always perform the normal checks between internal runtime configuration and admin runtime configuration for all bots even if the `intelmqctl` command was executed just to only one bot. 
XXX comment: specify how?

This checks will allow the sysadmin to be aware that something is wrong with the configuration even if sysadmin is executing other command with intelmqctl, therefore, a warning message will always show in the end of the command output.


# intelmqctl

**Rules & Checks:**
* the sysadmin in order to remove a bot from the configuration which is still running. MUST first to stop and then remove the configuration, not the opposite.
* will always execute the bot background, not in foreground.

XXX comment: how about test mode?

* will always provide the best log message in order to give additional information to sysadmin about the actions performed. 

XXX define log format in a separate document and link to it. Make this a HOWTO for new developers. What needs to be logged, when? Which log levels?

* will always check if there is any issue with configurations (runtime, defaults, pipeline) regarding all bots even if just one action to one bot has been executed.
 * in case a bot is running but some configuration for that bot is missing in one of the files, the action will not be performed and sysadmin will receive a warning message
 
 XXX where? on the logging system?
 
 * intelmqctl will automatically re-add the missing configuration and ask to syadmin to re-run the command again, now with the configurations cleaned.

XXX sounds like too much magic here. I prefer a **good** error message for the sysadmin, telling him what to do. And then the system should NOT try to be too smart.


**Syntax:**

XXX : note this section could benefit from the way man pages are written.

```
intelmqctl <action command> [<bot_id> | botnet ] <flags>
```

**Flags:**
XXX call it "generic Flags"


* `--now`: this parameter will execute the bot automatically without taking into account `run_mode`.
XXX comment: only once?

* `--debug`: this parameter will execute the bot in debug mode which automatically run it in foreground in order to easily see the log lines in the console and the log level will also automatically set up to `DEBUG`.

XXX : only once?

* `--filter`: this parameter will provide to sysadmin a quick way to apply a filter to which bots the action will take place. The filtering can be done using the configuration parameters as the following example:
```
intelmqctl start --filter "run_mode:scheduled, group:Collectors"
```

XXX define all filters



## intelmqctl start action

**Command:**

```
intelmqctl start [<bot_id> | botnet ] <flags>
```

**Procedure:**

* `intelmqctl` will not perform any action to a bot which is already running.
* if Run mode: stream
  - if Process manager: PID
    - intelmqctl will check if there is a PID file
    - if PID file exists, do nothing XXX : and print error message
    - if PID file does not exist, execute start action on bot and write PID file
  - if Process manager: systemd
    - execute `systemctl start <module@bot_id>`
* if Run mode: scheduled
  - if Process manager: PID or systemd
    - intelmqctl will check if crontab configuration line for the bot is already on crontab:
     - if crontab configuration line exists, do nothing. In the end, write a log message "bot is already running" XXX : is "scheduled" . Running is soemthing else!
     - if crontab configuration line does not exists, add configuration line on crontab such as `<schedule_time> <intelmq bot module> <bot_id> # <bot_id>`. In the end, write a log message "bot is schedule and will run at this time: `* * * * * `"
       XXX Aren't we trying to be too smart here? Lt's discuss...


## intelmqctl stop action

**Command:**

```
intelmqct stop [<bot_id> | botnet ] <flags>
```

**Procedure:**

* `intelmqctl` will not perform any action to a bot which is already stopped.
* if Run mode: stream
  - if Process manager: PID
    - intelmqctl will check if there is a PID file
    - if PID file exists, execute stop action on the bot and remove PID file. XXX print success of stopping the bot (yes, no). Print warning if it can not be stopped for some reason. XXX2: should we kill -9 ?
    - if PID file does not exist, do nothing
  - if Process manager: systemd
    - execute `systemctl stop <module@bot_id>`
* if Run mode: scheduled
  - if Process manager: PID or systemd
    - intelmqctl will check if crontab configuration line for the bot is still on crontab
    - if crontab configuration line exists, remove configuration line on crontab. In the end, write a log message "bot is unschedule."
    - if crontab configuration line does not exists, do nothing. In the end, write a log message "bot is already stopped"


## intelmqctl restart action

**Command:**

```
intelmqctl restart [<bot_id> | botnet ] <flags>
```

**Procedure:**

* `intelmqctl` will use the stop action command and start action command to perform the restart, therefore, there is no additional information required here, is only to actions commands being executed already explained.



## intelmqctl reload action

**Command:**

```
intelmqctl reload [<bot_id> | botnet ] <flags>
```

**Procedure:**

* `intelmqctl` will perform additional checks in order to handle some issues related to correct procedures which may not being followed by admin. The checks will be described in this section. 

* if `<bot_id>` has a new `run_mode` value AND `<bot_id>` is running:
  - raise message "`<bot_id>` is configured with a new `run_mode` therefore cannot be reload and it requires to be restarted in order to reload the new configuration. Do you want to restart the bot to apply the new `run_mode`? [Y/n]"
    - "[Y] `intelmqctl` will automatically execute restart action on the bot and the bot will start with the new configuration" \
    - "[N] `intelmqctl` will not perform any action, therefore bot will keep running in the current run state.
    XXX how aobut if this gets called from the manager? We can not enter keyboard strockes there!
    
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
        - if crontab configuration line exists, replace it and log a message explaining the update action. XXX: here some nice errors can happen.
        - if crontab configuration line does not exists, add it and log a message explaining the update action.
      **Note**: if a scheduled bot is running the reload action will be ignored until the next bot execution.

**Please note** the above explanation is exemplifying an interactive mode of intelmqctl, however, there will be available additional parameters to automatically answer the questions which will allow to execute this command by scripts or other tools.

XXX define them :)

## intelmqctl configtest action

**Command:**
```
intelmqctl configtest [<bot_id> | botnet ] <flags>
```

**Procedure:**

* there are 2 types of checks. check if json is ok and check if parameters of bots are ok.
 * for json check should give a generic message in case of something is failing saying "json is bad"
 * for bot check should give a generic message in case of something is failing saying "bot config is bad because ..."


## intelmqctl status action

**Command:**
```
intelctl status [<bot_id> | botnet ] <flags>
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
      - if configured on crontab, log message saying the current status is "running" XXX: call it "scheduled". Running is smthg else.
      - if not configured on crontab, log message saying the current status is "not running" XXX "not scheduled"

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


XXX think about an output format which is easy to parse for other systems.
Human readable tables are not.


## intelmqctl enable action

**Command:**
```
intelctl enable [<bot_id> | botnet ] <flags>
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


## intelmqctl disable action

**Command:**
```
intelctl disable [<bot_id> | botnet ] <flags>
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


## intelmqctl add-to-botnet action

**Command:**
```
intelctl add-to-botnet [<bot_id>] <flags>
```

**Procedure:**

* command only applies to bots, not to botnet
* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: true`, independently of the `run_mode` and `process_manager` configuration parameter.
* `intelmqctl` will not perform any other actions because this `add-to-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.
* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to add the bot to the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"


## intelmqctl remove-from-botnet action

**Command:**
```
intelctl remove-from-botnet [<bot_id> ] <flags>
```

**Procedure:**

* command only applies to bots, not to botnet
* `intelmqctl` will perform the usual checks and if no errors found, `intelmqctl` will configure the botnet configuration for the <bot_id> with `botnet: false`, independently of the `run_mode` and `process_manager` configuration parameter.
* `intelmqctl` will not perform any other actions because this `remove-from-botnet` action only change the runtime configuration parameter, without perform start/stop/restart/reload actions.
* `intelmqctl` will log a message "<bot_id> runtime configuration has been changed in order to remove the bot from the botnet but the bot will keep is current status (running or stopped). Please check bot current status and then perform, if needs, the action to start/stop/restart"





# Scenarios

## Scenario 1

**Scenario:** botnet start command after bot configuration was manually removed

Please note that this scenario is using botnet commands, therefore, it's crutial to have a good understand about botnet concept. Also, every single mentioned to "bots", except mentioned explicity, means bots which are part of the botnet.

1. In this case there are 10 bots configured as `botnet: true`. Admin execute the command to start the botnet.
2. Admin accidentally remove manually a bot with `bot_id: my-bot-1` from admin runtime configuration without stopping it previously.
3. Admin add manually a new bot with `bot_id: my-bot-2` to admin runtime configuration.
4. Admin execute the command to start the botnet which will do the following:
 1. do nothing to the bots which were already started in the first execution of the command to start the botnet
 2. execute start command following normal procedure to the `bot_id: my-bot-2` and intelmqctl will update the internal runtime configuration accordingly.
 3. keep the bot with `bot_id: my-bot-1` running but will also add the configuration stored in internal runtime configuration to the admin runtime configuration in order to prevent possible loss of bot configuration by this user mistake (not following the correct procedure).
 4. log a warning message providing information to the admin explaining the situation: "intelmqctl detected that bot my-bot-1 is still running but has been removed from user runtime configuration. intelmqctl added it to the user runtime configuration. Please first stop the bot, and remove it afterwards.".

The **correct procedure** is stop bot first and then remove bot configuration from admin runtime configuration.

## Scenario 2

**Scenario:** botnet stop command after bot configuration was manually removed

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


## Scenario 3

**Scenario:** botnet reload command after bot configuration was manually removed

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
