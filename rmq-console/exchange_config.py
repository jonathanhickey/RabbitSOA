
exchanges = [
    {
        'name': 'msgs',
        'type': 'direct',
        'durable': False,
        'sendable_protobufs': frozenset([('rsoa_example_pb2', 'ValueReq')])
    }
]
