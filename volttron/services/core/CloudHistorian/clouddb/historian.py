# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing
# official policies, either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# Author :Rajveer Singh
# }}}
from __future__ import absolute_import, print_function

import pymssql
import gevent
import json
import logging
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.messaging.health import (STATUS_BAD,
                                                STATUS_GOOD, Status)
import datetime
import numpy as np
import pandas as pd
import sys
import string
import re
#IOT libraries----------------
import time
import sys
from volttron.utils.iothub_client import *
from volttron.utils.iothub_client_args import *
from volttron.platform.agent import utils
#-------------------------------

#global variable for iot hub---
timeout = 241000
minimum_polling_time = 1
receive_context = 0
received_count = 0
i=0
# global counters
receive_callbacks = 0
send_callbacks = 0
flag=0
#--------------------------------


from volttron.platform.agent.base_historian import BaseHistorian

# We choose HTTP as our protocol for our purpose to send messages to the IOT hub----------
protocol = IoTHubTransportProvider.HTTP

# The connection string for the device to communicate with the IOT hub
connection_string = "HostName=volttron-iot-demo.azure-devices.net;DeviceId=Myvm;SharedAccessKey=qO81QDqFzy6UeEFCd1/H01ie2PsL6Dkxgfz+2p+3h3w="
#-----------------------------------------------------

FORWARD_TIMEOUT_KEY = 'FORWARD_TIMEOUT_KEY'
utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.5'
conn = pymssql.connect(server='volttroniot.database.windows.net', user='volttron@volttroniot', password='vvvVVV123@@@',
                       database='database1')
cursor = conn.cursor()
conn.autocommit(True)

#IOT code------------------------------------------------------------------------------
# define the certificated here which need to be defined to establish the communication
def set_certificates(iotHubClient):
    from iothub_client_cert import certificates
    try:
        iotHubClient.set_option("TrustedCerts", certificates)
        print("set_option TrustedCerts successful")
    except IoTHubClientError as e:
        print("set_option TrustedCerts failed (%s)" % e)


def receive_message_callback(message, counter):
    global receive_callbacks
    volttron_data_buffer = message.get_bytearray()
    size_data = len(volttron_data_buffer)
    print("Received Data: --%s-- " % (volttron_data_buffer[:size_data].decode('utf-8')))
    map_properties = message.properties()
    print("Map Properties inside the receive function : %s " % (map_properties))
    key_value_pair = map_properties.get_internals()
    print("key value pair in the receive function : %s" %(key_value_pair))
    counter += 1
    receive_callbacks += 1
    print("    Total calls received: %d" % receive_callbacks)
    return IoTHubMessageDispositionResult.ACCEPTED
    n=0
    while n < 1:
        status = iotHubClient.get_send_status()
        print("Send status: %s" % status)
        time.sleep(1002)
        n += 1

def send_confirmation_callback(message, result, user_context):
    global send_callbacks
    print(
        "Confirmation[%d] received for message with result = %s" %
        (user_context, result))
    send_callbacks += 1
    print("Total calls confirmed: %d" % send_callbacks)

def iothub_client_init():
    # prepare iothub client
    iotHubClient = IoTHubClient(connection_string, protocol)
    if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
        iotHubClient.set_option("timeout", timeout)
        iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)
    if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
        iotHubClient.set_option("logtrace", 0)
    iotHubClient.set_message_callback(
        receive_message_callback, receive_context)
    return iotHubClient

def print_last_message_time(iotHubClient):
    try:
        last_message = iotHubClient.get_last_message_receive_time()
        print("Last Message: %s" % time.asctime(time.localtime(last_message)))
        print("Actual time : %s" % time.asctime())
    except IoTHubClientError as e:
        if (e.args[0].result == IoTHubClientResult.INDEFINITE_TIME):
            print("No message received")
        else:
            print(e)

def iothub_client_volttron_run(self, peer, sender, bus, topic, headers, message):

    results_parametername=list()
    results_parametervalue=[]
    topicNameList=[]

    try:
        i = 0
        timestamp=headers['TimeStamp']
        converted_timestamp=pd.Timestamp(np.datetime64(timestamp)).to_pydatetime()
        print(converted_timestamp)
        time_formatted= time.mktime(converted_timestamp.timetuple())
        print(time_formatted)
        #initializing the iotHubClient
        iotHubClient = iothub_client_init()
        print("the database connection is established")
        cursor = conn.cursor()
        for element in message[0]:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            topicname = topic
            print (topicname)
            setpoint = element
            setpoint_value = message[0][element]
            results_parametervalue.append(setpoint_value)
            print (setpoint)
            chars_to_remove = ['(',')','(','\n','!','?','/',' ','-']
            topicname_modified=topic.translate(None, ''.join(chars_to_remove))
            print(topicname_modified)
            setpoint_modified=setpoint.translate(None, ''.join(chars_to_remove))
            msg_txt = '%s' % setpoint_modified
            results_parametername.append(msg_txt)
            msg_json = "{\"TopicName\": \"%s\",\"SetPointName\": \"%s\",\"SetPointValue\": %r,\"Time\": %r}"
            msg_json_formatted = msg_json % (topicname,msg_txt,setpoint_value,time_formatted)
            print(msg_json_formatted)
            message_json=IoTHubMessage(bytearray(msg_json_formatted, 'utf8'))
            iotHubClient.send_event_async(message_json, send_confirmation_callback, i)
            i=i+1

        global flag
        tup = tuple(results_parametername)
        tup2 =(' FLOAT(10),'.join(ele for ele in tup))
        tup3 = (tup2+' FLOAT(10)')
        tup1 =(','.join(ele for ele in tup))
        topicNameList.append(topicname_modified)
        results_parametervalue.append(time_formatted)
        for iterate in topicNameList:
            if (topicname_modified!=iterate):
                query3 = "CREATE TABLE %s (%s,time_value FLOAT);" % (topicname_modified, tup3)
                cursor.execute(query3)
            else:
                query_string = 'INSERT INTO %s(%s,time_value) VALUES %r' % (
                topicname_modified, tup1, tuple(results_parametervalue))
                cursor.execute(query_string)
        flag = flag + 1

        print(
            "IoTHubClient.send_event_async accepted message [%d]"
            " for transmission to IoT Hub." %
            i)
        i=i+1
        # Wait for Commands or exit
        print("IoTHubClient waiting for commands, press Ctrl-C to exit")

        n = 0
        while n < 1:
            status = iotHubClient.get_send_status()
            print("Send status: %s" % status)
            time.sleep(2)
            n += 1

    except IoTHubError as e:
        print("Unexpected error %s from IoTHub" % e)
        return
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

    print_last_message_time(iotHubClient)
    # conn.close()


#end of the IOT code ----------------------------------------------------------------------------------


def historian(config_path, **kwargs):
    config = utils.load_config(config_path)
    destination_vip = config.get('destination-vip')
    # subscriber_identity = config.get('subscriber_identity', None)

    class CloudHistorian(Agent):

        def __init__(self, **kwargs):
            super(CloudHistorian, self).__init__(**kwargs)

        @Core.receiver('onstart')
        def setup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            self._agent_id = config['agentid']
            try:
                event = gevent.event.Event()
                agent = Agent(address=destination_vip)
                agent.core.onstart.connect(lambda *a, **kw: event.set(), event)
                gevent.spawn(agent.core.run)
                event.wait(timeout=10)
                self._target_platform = agent

            except gevent.Timeout:
                self.vip.health.set_status(
                    STATUS_BAD, "Timeout in setup of agent")
                status = Status.from_json(self.vip.health.get_status())
                self.vip.health.send_alert(FORWARD_TIMEOUT_KEY,
                                           status)
                event.wait(timeout=10)
            agent.vip.pubsub.subscribe(peer='pubsub', prefix='devices/PNNL/BUILDING1/', callback=self.on_match)

        def on_match(self, peer, sender, bus, topic, headers, message):
            '''
            Subscribes to the platform message bus on the actuator, record,
            datalogger, and device topics to capture data.
            '''

            _log.debug('GOT DATA FOR: {}'.format(topic))
            iothub_client_volttron_run(self, peer, sender, bus, topic, headers, message)

    return CloudHistorian(**kwargs)

def main(argv=sys.argv):
    """Main method called by the eggsecutable.
    @param argv:
    """
    try:
        utils.vip_main(historian)
    except Exception as e:
        print(e)
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass

    print("\n Python Version : %s" % sys.version)
    print("IoT Hub for Python SDK Version: %s" % iothub_client.__version__)

    # establish the connection using the connection string and the protocol
    try:
        (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
    except OptionError as o:
        print(o)
        sys.exit(1)

    print("Starting the IoT Hub for Volttron")
    print("    Protocol : %s" % protocol)
    print("    Connection string :%s" % connection_string)


