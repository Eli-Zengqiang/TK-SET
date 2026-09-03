import io, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from xml.etree import ElementTree as ET

import uiautomator2 as u2
d = u2.connect()
print(d.app_current())
# dev=u2.connect()
# dev.app_start('com.tunnelkey.smarteye', '.refactor.core_app.main.MainActivity')
# time.sleep(3)


card = d(resourceId="com.tunnelkey.smarteye:id/connectWifiImg")
if card.exists:
    card.click()