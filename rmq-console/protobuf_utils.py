import importlib
import glob

compiled_pb2_list=glob.glob('protobufs/*_pb2.py')

def filename_to_importname(fn):
    return fn[:-3].replace('/','.')

def filename_to_fieldvalue(fn):
    return fn[10:-7]

protobuf_modules = {}
for compiled_pb2 in compiled_pb2_list:
    m = importlib.import_module(filename_to_importname(compiled_pb2))
    protobuf_modules[filename_to_fieldvalue(compiled_pb2)] = m


def find_protobuf(proto_file, name):
    m = protobuf_modules.get(proto_file)
    if not m:
        return None
    c = m.__dict__.get(name)
    return c

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
