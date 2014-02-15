import re
import socket
import time
import threading
import Queue

from core import permissions

from ssl import wrap_socket, CERT_NONE, CERT_REQUIRED, SSLError

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


def decode(txt):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return txt.decode(codec)
        except UnicodeDecodeError:
            continue
    return txt.decode('utf-8', 'ignore')


def censor(text):
    return text


class ReceiveThread(threading.Thread):
    """receives messages from IRC and puts them in the input_queue"""
    def __init__(self, sock, input_queue, timeout):
        self.input_buffer = ""
        self.input_queue = input_queue
        self.socket = sock
        self.timeout = timeout

        self.shutdown = False
        threading.Thread.__init__(self)

    def recv_from_socket(self, nbytes):
        return self.socket.recv(nbytes)

    def handle_receive_exception(self, error, last_timestamp):
        if time.time() - last_timestamp > self.timeout:
            self.input_queue.put(StopIteration)
            self.socket.close()
            return True
        return False

    def get_timeout_exception_type(self):
        return socket.timeout

    def run(self):
        last_timestamp = time.time()
        while not self.shutdown:
            try:
                data = self.recv_from_socket(4096)
                self.input_buffer += data
                if data:
                    last_timestamp = time.time()
                else:
                    if time.time() - last_timestamp > self.timeout:
                        self.input_queue.put(StopIteration)
                        self.socket.close()
                        return
                    time.sleep(1)
            except (self.get_timeout_exception_type(), socket.error) as e:
                if self.handle_receive_exception(e, last_timestamp):
                    return
                continue

            while '\r\n' in self.input_buffer:
                line, self.input_buffer = self.input_buffer.split('\r\n', 1)
                self.input_queue.put(decode(line))


class SSLReceiveThread(ReceiveThread):
    def __init__(self, sock, input_queue, timeout):
        ReceiveThread.__init__(self, sock, input_queue, timeout)

    def recv_from_socket(self, nbytes):
        return self.socket.read(nbytes)

    def get_timeout_exception_type(self):
        return SSLError

    def handle_receive_exception(self, error, last_timestamp):
       # this is terrible
        if not "timed out" in error.args[0]:
            raise
        return ReceiveThread.handle_receive_exception(self, error, last_timestamp)


class SendThread(threading.Thread):
    """sends messages from output_queue to IRC"""
    def __init__(self, sock, conn_name, output_queue):
        self.output_buffer = ""
        self.output_queue = output_queue
        self.conn_name = conn_name
        self.socket = sock

        self.shutdown = False
        threading.Thread.__init__(self)

    def run(self):
        while not self.shutdown:
            line = self.output_queue.get().splitlines()[0][:500]
            self.output_buffer += line.encode('utf-8', 'replace') + '\r\n'
            while self.output_buffer:
                sent = self.socket.send(self.output_buffer)
                self.output_buffer = self.output_buffer[sent:]


class ParseThread(threading.Thread):
    """parses messages from input_queue and puts them in parsed_queue"""
    def __init__(self, input_queue, output_queue, parsed_queue):
        self.input_queue = input_queue  # lines that were received
        self.output_queue = output_queue  # lines to be sent out
        self.parsed_queue = parsed_queue  # lines that have been parsed

        threading.Thread.__init__(self)

    def run(self):
        while True:
            # get a message from the input queue
            msg = self.input_queue.get()

            if msg == StopIteration:
                # got a StopIteration from the receive thread, pass it on
                # so the main thread can restart the connection
                self.parsed_queue.put(StopIteration)
                continue

            # parse the message
            if msg.startswith(":"):  # has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            mask = nick + "!" + user + "@" + host
            paramlist = irc_param_ref(params)
            lastparam = "" 
            if paramlist:
                if paramlist[-1].startswith(':'):
                    paramlist[-1] = paramlist[-1][1:]
                lastparam = paramlist[-1]
            # put the parsed message in the response queue
            self.parsed_queue.put([msg, prefix, command, params, nick, user, host,
                                   mask, paramlist, lastparam])
            # if the server pings us, pong them back
            if command == "PING":
                string = "PONG :" + paramlist[0]
                self.output_queue.put(string)


class IRCConnection(object):
    """handles an IRC connection"""
    def __init__(self, name, host, port, input_queue, output_queue):
        self.output_queue = output_queue  # lines to be sent out
        self.input_queue = input_queue  # lines that were received
        self.socket = self.create_socket()
        self.conn_name = name
        self.host = host
        self.port = port
        self.timeout = 300

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.TCP_NODELAY)

    def connect(self):
        self.socket.connect((self.host, self.port))

        self.receive_thread = ReceiveThread(self.socket, self.input_queue, self.timeout)
        self.receive_thread.start()

        self.send_thread = SendThread(self.socket, self.conn_name, self.output_queue)
        self.send_thread.start()

    def stop(self):
        self.send_thread.shutdown = True
        self.receive_thread.shutdown = True
        time.sleep(0.1)
        self.socket.close()

    def reconnect(self):
        self.stop()
        self.connect()


class SSLIRCConnection(IRCConnection):
    """handles a SSL IRC connection"""

    def __init__(self, name, host, port, input_queue, output_queue, ignore_cert_errors):
        self.ignore_cert_errors = ignore_cert_errors
        IRCConnection.__init__(self, name, host, port, input_queue, output_queue)

    def create_socket(self):
        return wrap_socket(IRCConnection.create_socket(self), server_side=False,
                           cert_reqs=CERT_NONE if self.ignore_cert_errors else
                           CERT_REQUIRED)


class IRC(object):
    """handles the IRC protocol"""

    def __init__(self, name, server, nick, port=6667, logger=None, channels=[], config={}):
        self.name = name
        self.channels = channels
        self.config = config
        self.server = server
        self.port = port
        self.logger = logger
        self.nick = nick
        self.vars = {}

        self.parsed_queue = Queue.Queue()  # responses from the server are placed here
        # format: [rawline, prefix, command, params,
        # nick, user, host, paramlist, msg]

        self.parsed_queue = Queue.Queue()
        self.input_queue = Queue.Queue()
        self.output_queue = Queue.Queue()

        # create the IRC connection and connect
        self.connection = self.create_connection()
        self.connection.connect()

        self.set_pass(self.config.get('server_password'))
        self.set_nick(self.nick)
        self.cmd("USER",
                 [self.config.get('user', 'cloudbot'), "3", "*",
                  self.config.get('realname', 'CloudBot - http://git.io/cloudbot')])

        self.parse_thread = ParseThread(self.input_queue, self.output_queue,
                                        self.parsed_queue)
        self.parse_thread.daemon = True
        self.parse_thread.start()

    def create_connection(self):
        return IRCConnection(self.name, self.server, self.port,
                             self.input_queue, self.output_queue)

    def stop(self):
        self.connection.stop()

    def set_pass(self, password):
        if password:
            self.cmd("PASS", [password])

    def set_nick(self, nick):
        self.cmd("NICK", [nick])

    def join(self, channel):
        """ makes the bot join a channel """
        self.send("JOIN {}".format(channel))
        if channel not in self.channels:
            self.channels.append(channel)

    def part(self, channel):
        """ makes the bot leave a channel """
        self.cmd("PART", [channel])
        if channel in self.channels:
            self.channels.remove(channel)

    def msg(self, target, text):
        """ makes the bot send a PRIVMSG to a target  """
        self.cmd("PRIVMSG", [target, text])

    def ctcp(self, target, ctcp_type, text):
        """ makes the bot send a PRIVMSG CTCP to a target """
        out = u"\x01{} {}\x01".format(ctcp_type, text)
        self.cmd("PRIVMSG", [target, out])

    def cmd(self, command, params=None):
        if params:
            params[-1] = u':' + params[-1]
            self.send(u"{} {}".format(command, ' '.join(params)))
        else:
            self.send(command)

    def send(self, string):
        try:
            self.logger.info(u"{} >> {}".format(self.name.upper(), string))
        except:
            # if this doesn't work, no big deal
            pass
        self.output_queue.put(string)


class SSLIRC(IRC):
    def __init__(self, name, server, nick, port=6667, logger=None, channels=[], config={},
                 ignore_certificate_errors=True):
        self.ignore_cert_errors = ignore_certificate_errors
        IRC.__init__(self, name, server, nick, port, logger, channels, config)

    def create_connection(self):
        return SSLIRCConnection(self.name, self.server, self.port, self.input_queue,
                                self.output_queue, self.ignore_cert_errors)
