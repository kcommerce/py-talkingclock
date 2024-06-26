# Prerequisites
- Python 3.5+
- lib playsound
- lib icalendar
# Build Pypi and upload
### 1. Project structure
```
py-talkingclock:
   src:
     talkingclock:
         talkingclock.py
         __init__.py
         buddha.ics
         mp3:
             1.mp3
             2.mp3
             ...
   setup.py
```

### 2. Build the package
```bash
python3 setup.py sdist bdist_wheel
```
### 3. Upload the package
```bash
twine upload dist/*
```
# Binary Download
- Download the binary: [download link](https://github.com/kcommerce/py-talkingclock/)

## TalkingClock
### 1. Install TalkingClock

  - Run the following command to install talkingclock
    ```bash
    pip3 install talkingclock
    ```
  - Note: If there's error about "OSError: could not get source code" try the following commands:
    ```bash
    pip3 install --upgrade wheel
    pip3 install --upgrade setuptools
    pip3 install PyObjC
    pip3 install playsound
    pip3 install talkingclock
    ```

### 2. Use : play current sound time

- Import and use talkingclock
    ```bash
    Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from talkingclock import talkingclock
    >>> talkingclock.play_soundtime()   
    ```
- Use in cronjob:
    ```bash
    0 8-23 * * * python3 -c "from talkingclock import talkingclock; talkingclock.play_soundtime()" >> ~/logs/time.log 1>&2

    ```
### 3. Use : play buddhist holy day sound

- Import and use talkingclock
    ```bash
    Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from talkingclock import buddhist_holyday
    >>> buddhist_holyday.play_holysound()
    ```
- Use in cronjob:
    ```bash
    0 8,12,17 * * * python3 -c "from talkingclock import buddhist_holyday; buddhist_holyday.play_holysound()" >> ~/logs/holyday.log  1>&2
    ```
