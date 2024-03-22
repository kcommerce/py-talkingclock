
import sys,os
from datetime import datetime
from playsound import playsound

PATH="~/mp3/time/"
d = datetime.now()
begin="begintime.mp3"
narika="narika.mp3"
natee="natee.mp3"
vinatee="vinatee.mp3"
end="endtime.mp3"
print(d)

playsound(PATH+begin)
playsound(PATH+str(d.hour)+".mp3")
playsound(PATH+narika)
playsound(PATH+str(d.minute)+".mp3")
playsound(PATH+natee)
playsound(PATH+str(d.second)+".mp3")
playsound(PATH+vinatee)
playsound(PATH+end)

