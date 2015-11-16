# -*- coding: utf-8 -*-

from __future__ import unicode_literals
<<<<<<< HEAD

import os.path
import sys
=======
import sys
import os.path
import stomp
>>>>>>> fd510b5... initial n6stomp commit. PEP8 ready!

from intelmq.lib.bot import Bot
from intelmq.lib.harmonization import DateTime
from intelmq.lib.message import Report

<<<<<<< HEAD
import stomp

=======
>>>>>>> fd510b5... initial n6stomp commit. PEP8 ready!

class StompListener(stomp.listener.PrintingListener):
    """ the stomp listener gets called asynchronously for
        every STOMP message
    """
    def __init__(self, n6stompcollector):
        self.n6stomper = n6stompcollector

    def on_heartbeat_timeout(self):
<<<<<<< HEAD
        self.n6stomper.logger.warn("Lost connection! Re-establishing.")
        self.n6stomper.conn.disconnect()
        self.n6stomper.conn.connect(wait=False)

    def on_error(self, headers, message):
        self.n6stomper.logger.warn('Received an error "%s".' % repr(message))

    def on_message(self, headers, message):
        self.n6stomper.logger.info("Got message %s." % repr(message))
=======
        # XXX FIXME: use logger instead of print
        # XXX FIXME: need to reconnect after timeout
        print "lost connection!"

    def on_error(self, headers, message):
        # XXX FIXME: use logger instead of print
        self.n6stomper.logger.warn('received an error "%s"' % repr(message))

    def on_message(self, headers, message):
        self.n6stomper.logger.info("got message %s" % repr(message))
>>>>>>> fd510b5... initial n6stomp commit. PEP8 ready!
        report = Report()
        report.add("raw", message.rstrip(), sanitize=True)
        report.add("feed.name", self.n6stomper.parameters.feed,
                   sanitize=True)
        report.add("feed.url", "stomp://" + self.n6stomper.parameters.server +
                   ":" + self.n6stomper.parameters.port +
                   "/" + self.n6stomper.parameters.exchange, sanitize=True)
        time_observation = DateTime().generate_datetime_now()
        report.add('time.observation', time_observation, sanitize=True)
        self.n6stomper.send_message(report)


class n6stompCollectorBot(Bot):
    """ main class for the n6 STOMP protocol collector """

    def init(self):
        self.server = getattr(self.parameters, 'server', 'n6stream.cert.pl')
        self.port = getattr(self.parameters, 'port', 61614)
        self.exchange = getattr(self.parameters, 'exchange', '')
        self.heartbeat = getattr(self.parameters, 'heartbeat', 60000)
        self.ssl_ca_cert = getattr(self.parameters, 'ssl_ca_certificate',
                                   'ca.pem')
        self.ssl_cl_cert = getattr(self.parameters, 'ssl_client_certificate',
                                   'client.pem')
        self.ssl_cl_cert_key = getattr(self.parameters,
                                       'ssl_client_certificate_key',
                                       'client.key')
        self.http_verify_cert = getattr(self.parameters,
                                        'http_verify_cert', True)

        # check if certificates exist
        for f in [self.ssl_ca_cert, self.ssl_cl_cert, self.ssl_cl_cert_key]:
            if (not os.path.isfile(f)):
<<<<<<< HEAD
                raise ValueError('Could not open file %s.' % f)
=======
                self.logger.exception('could not open file %s' % f)
                raise Exception('could not open file %s' % f)
>>>>>>> fd510b5... initial n6stomp commit. PEP8 ready!

        _host = [(self.server, self.port)]
        self.conn = stomp.Connection(host_and_ports=_host, use_ssl=True,
                                     ssl_key_file=self.ssl_cl_cert_key,
                                     ssl_cert_file=self.ssl_cl_cert,
                                     ssl_ca_certs=self.ssl_ca_cert,
                                     wait_on_receipt=True,
                                     heartbeats=(self.heartbeat,
                                                 self.heartbeat))

        self.conn.set_listener('', StompListener(self))
        self.conn.start()
        self.conn.connect(wait=False)
        self.conn.subscribe(destination=self.exchange, id=1, ack='auto')

    def disconnect(self):
        self.conn.disconnect()

    def process(self):
        pass

if __name__ == "__main__":
    bot = n6stompCollectorBot(sys.argv[1])
    bot.start()
