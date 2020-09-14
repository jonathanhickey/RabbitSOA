from protobufs import cpp_service_pb2


async def default_handler(self, channel, body, envelope, properties):
    data_a = cpp_service_pb2.DataA()
    data_a.ParseFromString(body)
    for da in data_a.ListFields():
        self.log.info('field name: {0}, type: {1}, value: {2}'.format(da[0].name, da[0].type, da[1]))

async def handle_DataA(self, channel, body, envelope, properties):
    data_a = cpp_service_pb2.DataA()
    data_a.ParseFromString(body)
    # for da in data_a.ListFields():
    #     self.log.info('field name: {0}, type: {1}, value: {2}'.format(da[0].name, da[0].type, da[1]))
    self.log.info('{0}>: DataA routing key: {1}, id:{2}, value: {3}'.format(
        envelope.exchange_name, envelope.routing_key,
        data_a.id, data_a.value))

async def handle_DataB(self, channel, body, envelope, properties):
    data_b = cpp_service_pb2.DataB()
    data_b.ParseFromString(body)
    self.log.info('{0}>: DataB routing key: {1}, id:{2}, ivalue: {3}, svalue: {4}'.format(
        envelope.exchange_name, envelope.routing_key,
        data_b.id, data_b.ivalue, data_b.svalue))
