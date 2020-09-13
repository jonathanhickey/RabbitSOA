from protobufs import cpp_service_pb2
# import pickle


async def handle_DataA(self, channel, body, envelope, properties):
    data_a = cpp_service_pb2.DataA()
    data_a.ParseFromString(body)
    self.log.info('{0}>: DataA routing key: {1}, id:{2}, value: {3}'.format(
        envelope.exchange_name, envelope.routing_key,
        data_a.id, data_a.value))
    # data_a_dict = {
    #     'msgType': 'DataA',
    #     'id': dataA.id,
    #     'value': dataA.value
    # }
    # self.console_conn.send(pickle.dumps(data_a_dict))

async def handle_DataB(self, channel, body, envelope, properties):
    data_b = cpp_service_pb2.DataB()
    data_b.ParseFromString(body)
    self.log.info('{0}>: DataB routing key: {1}, id:{2}, ivalue: {3}, svalue: {4}'.format(
        envelope.exchange_name, envelope.routing_key,
        data_b.id, data_b.ivalue, data_b.svalue))
