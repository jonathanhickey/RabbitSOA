import handlers


exchanges = [
    {
        'name': 'rsoa_exch',
        'type': 'direct',
        'durable': False,
        'sendable_protobufs': frozenset([('rsoa_example', 'ValueReq'), ('cpp_service', 'Request')]),
        'queues': [
            {
                'name': 'response',
                'durable': False,
                'routing_key': 'DataA',
                'handler': handlers.handle_DataA
            },
            {
                'name': 'dataB',
                'durable': False,
                'routing_key': 'DataB',
                'handler': handlers.handle_DataB
            }
        ]
    }
]
