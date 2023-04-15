"""
Optolink_mac package
Author: vich-667
"""
import platform

from vito_monitor_ctrl.optolink_mac.optolink_mac_interface import OptolinkMode, OptolinkInvalidMode, OptolinkCommError

if platform.system() == 'Linux':
    from vito_monitor_ctrl.optolink_mac.optolink_mac_serial import OptolinkMacSerial as OptolinkMac
else:
    from vito_monitor_ctrl.optolink_mac.optolink_dummy import OptolinkMacDummy as OptolinkMac
