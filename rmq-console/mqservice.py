import asyncio
import aioamqp
import exchange_config
import pickle
import types
from os.path import join
import protobuf_utils
import logging


class MQService():
    def __init__(self, conn):
        self.console_conn = conn
        self.loop = asyncio.get_event_loop()
        self.log_dir = '/log'
        self.rootlog = logging.getLogger()
        # self.log = logging.getLogger('console.mq_activity')
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='%(asctime)s %(name)-16s %(levelname)-8s %(message)s', datefmt='%Y%m%d %H:%M:%S')
        fh = logging.FileHandler(join(self.log_dir, 'mq_activity.log'))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.rootlog.addHandler(fh)

    async def init(self):
        await self.init_mq()

    async def init_mq(self):
        self.log.info('initiating MQ connection')
        while True:
            host='mq'
            port=5672
            login='system'
            password='system'
            try:
                self.transport, self.protocol = await aioamqp.connect(host=host,
                                                                      port=port,
                                                                      login=login,
                                                                      password=password)
                break
            except OSError:
                self.log.warning('cannot connect to {0}:{1}, will retry in 2 seconds'.format(host, port))
                await asyncio.sleep(2)
        self.log.info('connected to {0}:{1}'.format(host, port))

        self.channel = await self.protocol.channel()

        for exchange in exchange_config.exchanges:
            await self.setup_exchange(exchange)

        self.log.info('finished connecting to MQ')

    async def setup_exchange(self, exchange):
        exchange_name = exchange['name']
        self.log.info('declaring {0} exchange "{1}"'.format(exchange['type'], exchange_name))
        await self.channel.exchange_declare(exchange_name=exchange_name, type_name=exchange['type'], durable=exchange['durable'])
        if 'queues' in exchange:
            for queue in exchange['queues']:
                queue_name = queue['name']
                routing_key = queue['routing_key']
                handler = queue['handler']
                setattr(self, handler.__name__, types.MethodType(handler, self)) # add the handler to our instance
                self.log.info('declaring queue {0}'.format(queue_name))
                await self.channel.queue_declare(queue_name=queue_name, durable=queue['durable'])
                self.log.info('binding queue {0} to exchange {1} with routing key {2}, handler {3}'.format(
                    queue_name, exchange_name, routing_key, handler.__name__))
                await self.channel.queue_bind(queue_name=queue_name, exchange_name=exchange_name, routing_key=routing_key)
                await self.channel.basic_consume(getattr(self, handler.__name__), queue_name=queue_name, no_ack=True)

    async def check_for_pickles_from_pipe(self):
        while True:
            if self.console_conn.poll():
                b = self.console_conn.recv()
                s = pickle.loads(b)
                if not s:
                    self.log.info('exiting MQService')
                    break

                content_dict = s
                if content_dict == None:
                    self.log.info('content_dict == None')
                    break
                exchange = content_dict.pop('mqexchange')
                routing_key = content_dict.pop('routing_key')
                protoimport = content_dict.pop('protoimport')
                protobuf = content_dict.pop('protobuf')
                pb_type = protobuf_utils.find_protobuf(protoimport, protobuf)
                pb_inst = pb_type()
                oneof = content_dict.pop('oneof', None)
                if oneof: # use fd to get field list
                    self.log.info('{0}<{1}: {2}.{3}.{4} {5}'.format(exchange, routing_key, protoimport, protobuf, oneof, content_dict))
                    oneof_type = getattr(pb_inst, oneof)
                    fd_type = protobuf_utils.find_oneof(pb_type, oneof)
                    for field_name in fd_type.message_type.fields_by_name.keys():
                        if field_name in content_dict: setattr(oneof_type, field_name, content_dict.pop(field_name))
                    if len(content_dict) > 0:
                        self.log.info('there are unused items in the content_dict {0}'.format(str(content_dict.items())))
                    await self.channel.basic_publish(pb_inst.SerializeToString(),
                            exchange_name=exchange,
                            routing_key=routing_key)
                else:
                    self.log.info('{0}<{1}: {2}.{3} {4}'.format(exchange, routing_key, protoimport, protobuf, content_dict))
                    for field_name in pb_type.DESCRIPTOR.fields_by_camelcase_name.keys():
                        self.log.info('field_name: {0}'.format(field_name))
                        self.log.info(content_dict)
                        if field_name in content_dict: setattr(pb_inst, field_name, content_dict.pop(field_name))
                    if len(content_dict) > 0:
                        self.log.info('there are unused items in the content_dict {0}'.format(str(content_dict.items())))
                    await self.channel.basic_publish(pb_inst.SerializeToString(),
                            exchange_name=exchange,
                            routing_key=routing_key)

            await asyncio.sleep(1)

    def run(self):
        self.loop.run_until_complete(asyncio.ensure_future(self.init()))
        self.loop.run_until_complete(asyncio.ensure_future(self.check_for_pickles_from_pipe()))

def initializeMQService(conn):
    svc = MQService(conn)
    svc.run()
