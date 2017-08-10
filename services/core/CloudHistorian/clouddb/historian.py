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

# }}}

from __future__ import absolute_import, print_function

import logging
import sys

import pymongo
from bson.objectid import ObjectId
from examples.ExampleSubscriber.subscriber import subscriber_agent
from pymongo import InsertOne, ReplaceOne
from pymongo.errors import BulkWriteError
import gevent



from datetime import datetime
import logging
import random
import sys
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
from volttron.platform.messaging import topics, headers as headers_mod
from volttron.platform.messaging.health import (STATUS_BAD,
                                                STATUS_GOOD, Status)
#IOT libraries----------------
import time
import sys
import  volttron.utils.iothub_client
from volttron.utils.iothub_client import *
from volttron.utils.iothub_client_args import *


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
Data_List = list() #empty list
# message = list()
#--------------------------------

from volttron.platform.agent import utils
from volttron.platform.agent.base_historian import BaseHistorian

# We choose HTTP as our protocol for our purpose to send messages to the IOT hub----------
protocol = IoTHubTransportProvider.HTTP

# The connection string for the device to communicate with the IOT hub
connection_string = "HostName=volttron-iot-demo.azure-devices.net;DeviceId=Myvm;SharedAccessKey=qO81QDqFzy6UeEFCd1/H01ie2PsL6Dkxgfz+2p+3h3w="

#the message we want to send to the cloud
#to do: get messages from VC and send it to the cloud
msg_txt = "{\"deviceId\": \"myRaspberryPieDevice\",\"DATA\": \"Data from the building\""

#-----------------------------------------------------

FORWARD_TIMEOUT_KEY = 'FORWARD_TIMEOUT_KEY'
utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.5'

'''
Structuring the agent this way allows us to grab config file settings
for use in subscriptions instead of hardcoding them.
'''
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
    print("insde the confirmation message")
    print("    message Id: %s" % message.message_id)
    print("    correlation Id: %s" % message.correlation_id)
    print("message sent :%s " , msg_txt)
    send_callbacks += 1
    print("    Total calls confirmed: %d" % send_callbacks)

def iothub_client_init():
    # prepare iothub client
    iotHubClient = IoTHubClient(connection_string, protocol)
    if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
        iotHubClient.set_option("timeout", timeout)
        iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)
    #iotHubClient.set_option("messageTimeout", message_timeout)
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

def iothub_client_volttron_run():
    i=0
    b=bytearray()
    try:
        #initializing the iotHubClient
        iotHubClient = iothub_client_init()

        while True:
            # send a few messages every minute
            if (i & 1) == 1:
                message = IoTHubMessage(bytearray(msg_txt, 'utf8'))
                print (message)
            else:
                message = IoTHubMessage(msg_txt)
            # message.message_id = "message_%d" % i
            # message.correlation_id = "correlation_%d" % i
            iotHubClient.send_event_async(message, send_confirmation_callback, i)
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


# if __name__ == '__main__':
#     print("\nPython Version : %s" % sys.version)
#     print("IoT Hub for Python SDK Version: %s" % iothub_client.__version__)
#
# #establish the connection using the connection string and the protocol
#     try:
#         (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
#     except OptionError as o:
#         print(o)
#         sys.exit(1)
#
#     print("Starting the IoT Hub for Volttron")
#     print("    Protocol : %s" % protocol)
#     print("    Connection string :%s" % connection_string)
#
#     iothub_client_volttron_run()

#end of the IOT code ----------------------------------------------------------------------------------

    def subscriber_agent(config_path, **kwargs):
        config = utils.load_config(config_path)
        destination_vip = config.get('destination-vip')
        subscriber_identity = config.get('subscriber_identity', None)

        class ExampleSubscriber(Agent):
            '''
            This agent demonstrates usage of the 3.0 pubsub service as well as
            interfacting with the historian. This agent is mostly self-contained,
            but requires the histoiran be running to demonstrate the query feature.
            '''

            def __init__(self, **kwargs):
                super(ExampleSubscriber, self).__init__(**kwargs)

            @Core.receiver('onstart')
            def setup(self, sender, **kwargs):
                # Demonstrate accessing a value from the config file
                iothub_client_volttron_run()
                self._agent_id = config['agentid']
                try:
                    # _log.debug("Setting up to forward to {}".format(destination_vip))
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
                agent.vip.pubsub.subscribe(peer='pubsub', prefix='devices/PNNL/', callback=self.on_match)

            def on_match(self, peer, sender, bus, topic, headers, message):
                '''
                Subscribes to the platform message bus on the actuator, record,
                datalogger, and device topics to capture data.
                '''

                _log.debug('GOT DATA FOR: {}'.format(topic))
                iothub_client_volttron_run()

        return ExampleSubscriber(**kwargs)

    def main(argv=sys.argv):
        '''Main method called by the eggsecutable.'''
        try:
            utils.vip_main(subscriber_agent)
        except Exception as e:
            _log.exception('unhandled exception')




def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(historian)
    except Exception as e:
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


