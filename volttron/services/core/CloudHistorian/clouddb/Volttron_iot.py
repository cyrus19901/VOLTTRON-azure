

import time
import sys
import iothub_client
from iothub_client import *
from iothub_client_args import *


#global variables
timeout = 241000
minimum_polling_time = 1
receive_context = 0
received_count = 0
i=0
# global counters
receive_callbacks = 0
send_callbacks = 0

# We choose HTTP as our protocol for our purpose
protocol = IoTHubTransportProvider.HTTP

# The connection string for the device
connection_string = "HostName=volttron-iot-demo.azure-devices.net;DeviceId=Myvm;SharedAccessKey=qO81QDqFzy6UeEFCd1/H01ie2PsL6Dkxgfz+2p+3h3w="


#the message we want to send to the cloud

#to do: get messages from VC and send it to the cloud

msg_txt = "{\"deviceId\": \"myRaspberryPieDevice\",\"DATA\": \"Data from the building\""

# define the certificated here which need to be defined to establish the communication
def set_certificates(iotHubClient):
    from iothub_client_cert import certificates
    try:
        iotHubClient.set_option("TrustedCerts", certificates)
        print("set_option TrustedCerts successful")
    except IoTHubClientError as e:
        print("set_option TrustedCerts failed (%s)" % e)

# we receive messages here from the cloud

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

# send confirmation message that the data has been pushed to the cloud

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
    try:
#initializing the iotHubClient
        iotHubClient = iothub_client_init()

        while True:
            # send a few messages every minute
            if (i & 1) == 1:
                message = IoTHubMessage(bytearray(msg_txt, 'utf8'))
            else:
                message = IoTHubMessage(msg_txt)
            message.message_id = "message_%d" % i
            message.correlation_id = "correlation_%d" % i
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



if __name__ == '__main__':
    print("\nPython Version : %s" % sys.version)
    print("IoT Hub for Python SDK Version: %s" % iothub_client.__version__)

#establish the connection using the connection string and the protocol
    try:
        (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
    except OptionError as o:
        print(o)
        sys.exit(1)

    print("Starting the IoT Hub for Volttron")
    print("    Protocol : %s" % protocol)
    print("    Connection string :%s" % connection_string)

    iothub_client_volttron_run()
