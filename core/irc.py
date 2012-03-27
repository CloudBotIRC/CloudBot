import re
import socket
import time
import thread
import Queue

from ssl import wrap_socket, CERT_NONE, CERT_REQUIRED, SSLError


def decode(txt):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return txt.decode(codec)
        except UnicodeDecodeError:
            continue
    return txt.decode('utf-8', 'ignore')


def censor(text):
    replacement = '[censored]'
    if 'censored_strings' in bot.config:
        words = map(re.escape, bot.config['censored_strings'])
        regex = re.compile('(%s)' % "|".join(words))
        text = regex.sub(replacement, text)
    return text


class crlf_tcp(object):
    "Handles tcp connections that consist of utf-8 lines ending with crlf"

    def __init__(self, host, port, timeout=300):
        self.ibuffer = ""
        self.obuffer = ""
        self.oqueue = Queue.Queue()  # lines to be sent out
        self.iqueue = Queue.Queue()  # lines that were received
        self.socket = self.create_socket()
        self.host = host
        self.port = port
        self.timeout = timeout

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.TCP_NODELAY)

    def run(self):
        self.socket.connect((self.host, self.port))
        thread.start_new_thread(self.recv_loop, ())
        thread.start_new_thread(self.send_loop, ())

    def recv_from_socket(self, nbytes):
        return self.socket.recv(nbytes)

    def get_timeout_exception_type(self):
        return socket.timeout

    def handle_receive_exception(self, error, last_timestamp):
        if time.time() - last_timestamp > self.timeout:
            self.iqueue.put(StopIteration)
            self.socket.close()
            return True
        return False

    def recv_loop(self):
        last_timestamp = time.time()
        while True:
            try:
                data = self.recv_from_socket(4096)
                self.ibuffer += data
                if data:
                    last_timestamp = time.time()
                else:
                    if time.time() - last_timestamp > self.timeout:
                        self.iqueue.put(StopIteration)
                        self.socket.close()
                        return
                    time.sleep(1)
            except (self.get_timeout_exception_type(), socket.error) as e:
                if self.handle_receive_exception(e, last_timestamp):
                    return
                continue

            while '\r\n' in self.ibuffer:
                line, self.ibuffer = self.ibuffer.split('\r\n', 1)
                self.iqueue.put(decode(line))

    def send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            print ">>> %r" % line
            self.obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self.obuffer:
                sent = self.socket.send(self.obuffer)
                self.obuffer = self.obuffer[sent:]


class crlf_ssl_tcp(crlf_tcp):
    "Handles ssl tcp connetions that consist of utf-8 lines ending with crlf"
    def __init__(self, host, port, ignore_cert_errors, timeout=300):
        self.ignore_cert_errors = ignore_cert_errors
        crlf_tcp.__init__(self, host, port, timeout)

    def create_socket(self):
        return wrap_socket(crlf_tcp.create_socket(self), server_side=False,
                cert_reqs=CERT_NONE if self.ignore_cert_errors else
                CERT_REQUIRED)

    def recv_from_socket(self, nbytes):
        return self.socket.read(nbytes)

    def get_timeout_exception_type(self):
        return SSLError

    def handle_receive_exception(self, error, last_timestamp):
        # this is terrible
        if not "timed out" in error.args[0]:
            raise
        return crlf_tcp.handle_receive_exception(self, error, last_timestamp)

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


class IRC(object):
    "handles the IRC protocol"
    #see the docs/ folder for more information on the protocol
    def __init__(self, server, nick, port=6667, channels=[], conf={}):
        self.channels = channels
        self.conf = conf
        self.server = server
        self.port = port
        self.nick = nick

        self.out = Queue.Queue()  # responses from the server are placed here
        # format: [rawline, prefix, command, params,
        # nick, user, host, paramlist, msg]
        self.connect()

        thread.start_new_thread(self.parse_loop, ())

    def create_connection(self):
        return crlf_tcp(self.server, self.port)

    def connect(self):
        self.conn = self.create_connection()
        thread.start_new_thread(self.conn.run, ())
        self.set_pass(self.conf.get('server_password'))
        self.set_nick(self.nick)
        self.cmd("USER",
            [conf.get('user', 'cloudbot'), "3", "*", conf.get('realname',
                'CloudBot - http://git.io/cloudbot')])

    def parse_loop(self):
        while True:
            msg = self.conn.iqueue.get()

            if msg == StopIteration:
                self.connect()
                continue

            if msg.startswith(":"):  # has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            mask = user + "@" + host
            paramlist = irc_param_ref(params)
            lastparam = ""
            if paramlist:
                if paramlist[-1].startswith(':'):
                    paramlist[-1] = paramlist[-1][1:]
                lastparam = paramlist[-1]
            self.out.put([msg, prefix, command, params, nick, user, host,
                    mask, paramlist, lastparam])
            if command == "PING":
                self.cmd("PONG", paramlist)

    def set_pass(self, password):
        if password:
            self.cmd("PASS", [password])

    def set_nick(self, nick):
        self.cmd("NICK", [nick])

    def join(self, channel):
        self.cmd("JOIN", [channel])
        
    def part(self, channel):
        self.cmd("PART", [channel])

    def msg(self, target, text):
        self.cmd("PRIVMSG", [target, text])

    def cmd(self, command, params=None):
        if params:
            params[-1] = ':' + params[-1]
            self.send(command + ' ' + ' '.join(map(censor, params)))
        else:
            self.send(command)

    def send(self, str):
        self.conn.oqueue.put(str)


class FakeIRC(IRC):
    def __init__(self, server, nick, port=6667, channels=[], conf={}, fn=""):
        self.channels = channels
        self.conf = conf
        self.server = server
        self.port = port
        self.nick = nick

        self.out = Queue.Queue()  # responses from the server are placed here

        self.f = open(fn, 'rb')

        thread.start_new_thread(self.parse_loop, ())

    def parse_loop(self):
        while True:
            msg = decode(self.f.readline()[9:])

            if msg == '':
                print "!!!!DONE READING FILE!!!!"
                return

            if msg.startswith(":"):  # has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            mask = user + "@" + host
            paramlist = irc_param_ref(params)
            lastparam = ""
            if paramlist:
                if paramlist[-1].startswith(':'):
                    paramlist[-1] = paramlist[-1][1:]
                lastparam = paramlist[-1]
            self.out.put([msg, prefix, command, params, nick, user, host,
                    mask, paramlist, lastparam])
            if command == "PING":
                self.cmd("PONG", [params])

    def cmd(self, command, params=None):
        pass


class SSLIRC(IRC):
    def __init__(self, server, nick, port=6667, channels=[], conf={},
                 ignore_certificate_errors=True):
        self.ignore_cert_errors = ignore_certificate_errors
        IRC.__init__(self, server, nick, port, channels, conf)

    def create_connection(self):
        return crlf_ssl_tcp(self.server, self.port, self.ignore_cert_errors)
