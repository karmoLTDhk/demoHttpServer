# Http Server

## Python Server

```bash
$ python3 httpDataServer.py -p 51830
```

Execue the python for the server

---

## Network Interface:
|Device         |IP         |Port   |URL            |Function       |
|---            |--         |--     |--             |--             |
|Server         |192.168.5.1|51830  |/chassisData   |HTTP Telemetry |
|Server         |192.168.5.1|51830  |/cmd/..        |HTTP CMD       |
|Server         |192.168.5.1|51831  |/camera        |Video Port     |
|Server         |192.168.5.1|51832  |/camera        |Video Port     |
|Server         |192.168.5.1|51833  |/camera        |Video Port     |
|--             |--         |--     |--             |--             |
|Tablet         |192.168.5.2|/      |/              |Local IP       |
|--             |--         |--     |--             |--             |
|*GATEWAY*      |192.168.5.3|/      |/              |Local IP       |
|--             |--         |--     |--             |--             |


---

## HTTP GET CMD
All in small-caps
```
url/chassisData
```
*Return 200* for Sucess executed command\

```JSON
{
    'radar':    [0, 0, 0, 0],

    'gps':      {
                    'year':     0,
                    'month':    0,
                    'day':      0,
                    'hour':     0,
                    'mins':     0,
                    'sec':      0,
                    'lat':      0,
                    'lon':      0,
                    'nSate':    0,
                    'PDOP':     0,
                    'HDOP':     0,
                    'VDOP':     0,
                },

    'stepper':  {
                    'mode':     0,
                    'xPos':     0,
                    'yPos':     0,
                },

    'chassis':  {
                    'voltage':  0,
                    'temp':     0,
                    'rpmL':     0,
                    'rpmR':     0,
                },

    'system':   {
                    'warningLight':     0,
                    'headlight':        0,
                    'bumper':           0,
                    'emergencyBtn':     0,
                },

    'fogger':   {
                    'id':       0,
                    'flowRate': 0,
                    'flowSpeed':0,
                    'warning':  0,
                },

    'imu':    [0, 0, 0]
}
```

---

## HTTP POST CMD
All in small-caps
```
url/cmd/<ID>/<ACTION>/<VALUE>/<arguments>
```
*Return 200* for Sucess executed command\
*Return 501* for Correct but not-executed command\
*Return 403* for imcompleted command\
*Return 404* for error command\
### Chassis
>Change the chassis mode\
>->Auto\
>->Manual\
>**for AUTO mode, both 2 arguments must be given.**
<dl>
    <dt>Value</dt>
    <dd><em>Maunal</em> mode or <em>Auto</em> Mode</dd>
    <dd>
        <dt>Args</dt>
            <dd>surge >> <em>range within -200 to 200</em></dd>
            <dd>yaw   >> <em>range within -200 to 200</em></dd>
</dl>

```
/cmd/CHASSIS/>>/..
>> 'M'
>> 'A'
..>> +-200 
..>> +-200
```

### Stepper
>Change the Stepper mode\
>->Manual\
>->Auto\
>->Reset\
>->System\
>**In AUTO mode, all arguments are required.**\
>**In SYSTEM mode, arguments are different.**
<dl>
    <dt>Value</dt>
    <dd><em>Auto</em> Mode</dd>
    <dd>
        <dt>Args</dt>
            <dd>Minimum X >> <em>range within -90 to 90</em>, smaller than Maximum X</dd>
            <dd>Maximum X >> <em>range within -90 to 90</em>, larger than Minimum X</dd>
            <dd>Minimum Y >> <em>range within -45 to 45</em>, smaller than Maximum Y</dd>
            <dd>Maximum Y >> <em>range within -45 to 45</em>, larger than Minimum Y</dd>
            <dd>Speed     >> <em>range within 0 to 15</em></dd>
</dl>

<dl>
    <dt>Value</dt>
    <dd><em>System</em> Mode</dd>
    <dd>
        <dt>Args</dt>
            <dd>x PWM   >> <em>range within 10 to 20</em></dd>
            <dd>y PWM   >> <em>range within -10 to 20</em></dd>
            <dd>Speed   >> <em>range within 0 to 15</em></dd>
</dl>

<dl>
    <dt>Value</dt>
    <dd><em>Manual</em> Mode or <em>Reset</em> Mode</dd>
    <dd>
        <dt>Args</dt>
            <dd>Speed   >> <em>range within 0 to 15</em></dd>
</dl>

```
/cmd/STEPPER/>>/..

>> 'M' or 'R'
..>> 0-15

>> 'A'
..>> +-90
..>> +-90
..>> +-45
..>> +-45
..>> 0-15

>> 'S'
..>> 10-20
..>> 10-20
..>> 0-15
```

### System
>Change the light system or horn\
>->WarningLight\
>->HeadLight\
>->Horn

<dl>
    <dt>Value</dt>
    <dd><em>Headlight</em> or <em>Horn</em></dd>
    <dd>
        <dt>Args</dt>
            <dd>on</dd>
            <dd>off</dd>
</dl>

<dl>
    <dt>Value</dt>
    <dd><em>WarningLight</em></dd>
    <dd>
        <dt>Args</dt>
            <dd>Colour >> </dd>
            <dd><em>Red (1)</em></dd>
            <dd><em>Green (2)</em></dd>
            <dd><em>Yellow (3)</em></dd>
            <dd><em>Blue (4)</em></dd>
            <dd><em>purple (5)</em></dd>
            <dd><em>white (6)</em></dd>
            <dd><em>off (0))</em></dd>
</dl>

```
/cmd/SYSTEM/>>/..

>> 'HEADLIGHT' or 'HORN'
..>> ON
..>> OFF

>> 'WARNINGLIGHT'
..>> 0-6
```

### Fogger System
>Change the fogger system parameters\
>->flowRate\
>->flowSpeed

<dl>
    <dt>Value</dt>
    <dd><em>flowRate</em> or <em>flowSpeed</em></dd>
    <dd>
        <dt>Args</dt>
            <dd>0-9</dd>
</dl>

```
/cmd/FOGGER/>>/..

>> 'FLOWRATE' or 'FLOWSPEED'
..>> 0-9
```