from google.protobuf.message import Message

protobufs = {}

import rsoa_example_pb2
protobufs['rsoa_example_pb2'] = [v for v in  vars(rsoa_example_pb2).values() if isinstance(v, type) and issubclass(v, Message)]


def find_protobuf(proto_file, name):
    for pb in protobufs[proto_file]:
        if pb.DESCRIPTOR.name == name:
            return pb
    return None

def find_oneof(pb, name):
    for f in pb.DESCRIPTOR.oneofs_by_name['msg'].fields:
        if f.name == name:
            return f
    return None

def validate_content_dict_with_pb(content_dict, pb):
    unexpected_keys = set(content_dict.keys()) - set(pb.DESCRIPTOR.fields_by_camelcase_name.keys())
    if len(unexpected_keys) > 0:
        print('unexpected keys in {0}: {1}'.format(pb.DESCRIPTOR.name, unexpected_keys))
        return False
    return True


def validate_content_dict_with_pb2(content_dict, pb, expected):
    unexpected_keys = set(content_dict.keys()) - set(pb.DESCRIPTOR.fields_by_camelcase_name.keys()) - set(expected)
    if len(unexpected_keys) > 0:
        print('unexpected keys in {0}: {1}'.format(pb.DESCRIPTOR.name, unexpected_keys))
        return False
    return True

def validate_content_dict_with_field_descriptor(content_dict, fd):
    unexpected_keys = set(content_dict.keys()) - set(fd.message_type.fields_by_name.keys())
    if len(unexpected_keys) > 0:
        print('unexpected keys in {0}: {1}'.format(fd.message_type.name, unexpected_keys))
        return False
    return True

def validate_content_dict_with_field_descriptor2(content_dict, fd, expected):
    print('{0} {1} {2}'.format(set(content_dict.keys()), set(fd.message_type.fields_by_name.keys()), set(expected)))
    unexpected_keys = set(content_dict.keys()) - set(fd.message_type.fields_by_name.keys()) - set(expected)
    if len(unexpected_keys) > 0:
        print('unexpected keys in {0}: {1}'.format(fd.message_type.name, unexpected_keys))
        return False
    return True
