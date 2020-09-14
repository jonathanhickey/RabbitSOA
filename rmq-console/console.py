import protobuf_utils
from mqservice import initializeMQService
from cmd import Cmd
from multiprocessing import Process, Pipe
import os
from os.path import isfile, join
import ast
import copy
import pickle
import argparse
import importlib

class MyPrompt(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        # msgContents dict contains a mapping of msg_name to msg contents_dict
        # each msg contents_dict has a mapping of PB fields to PB field values
        # plus the key 'Action' whose value determines the PB message
        self.msgContents = {}

        self.our_conn, their_conn = Pipe()
        self.proc = Process(target=initializeMQService, args=(their_conn, exch_conf_filename))
        self.proc.start()
        self.msg_dir = '/msgs'
        self.load_msgs()

    def load_msgs(self):
        pickle_files = [f for f in os.listdir(self.msg_dir) if not f.startswith('.') and isfile(join(self.msg_dir, f))]
        print('loading msgs: {0}'.format(pickle_files))
        for msg_name in pickle_files:
            with open(join(self.msg_dir, msg_name), 'rb') as handle:
                contents_dict = pickle.load(handle)
                self.msgContents[msg_name] = contents_dict

    def parse1(self, rest):
        try:
            arg = ast.literal_eval(rest)
        except ValueError as ve:
            print('ast.literal_eval() failed with ValueError {0}'.format(ve))
            return None
        except SyntaxError as se:
            print('ast.literal_eval() failed with SyntaxError {0}'.format(se))
            return None
        return arg

    def do_store(self, rest):
        '''stores a whole msg, overwriting what was there. e.g. store msg1 {'mqexchange': 'amq.topic', 'protoimport': 'rsoa_example_pb2', 'protobuf': 'ValueReq', 'id': 1 }'''
        # some examples:
        # store n4 {'mqexchange': 'amq.topic', 'clOrdID': 'aaa', 'sessionID': '1234', 'protobuf': 'Action', 'oneof': 'newOrder', 'price': 850, 'quantity': 100, 'orderType': 0, 'symbol': 'TEST1|TEST2', 'side': 1}
        [msg_name, rest] = rest.split(maxsplit=1)
        content_dict = self.parse1(rest)
        self.store(msg_name, content_dict)

    def store(self, msg_name, content_dict):
        if 'protoimport' in content_dict:
            protoimport = content_dict['protoimport']
        else:
            print('content dictionary must have a protoimport')
            return
        if 'protobuf' in content_dict:
            protobuf = content_dict['protobuf']
        else:
            print('content dictionary must have a protobuf')
            return

        pb = protobuf_utils.find_protobuf(protoimport, protobuf)
        if not pb:
            print('protobuf {0} does not exist'.format(protobuf))
            return
        oneof = None
        if 'oneof' in content_dict:
            oneof = content_dict['oneof']
            oo = protobuf_utils.find_oneof(pb, oneof)
            if not oo:
                print('protbuf {0} does not have oneof field {1}'.format(protobuf, oneof))
            else:
                if (not protobuf_utils.validate_content_dict_with_field_descriptor2(
                        content_dict, oo, ['mqexchange', 'protoimport', 'protobuf', 'oneof', 'routing_key'])):
                    return
        else:
            if (not protobuf_utils.validate_content_dict_with_pb2(
                    content_dict, pb, ['mqexchange', 'protoimport', 'protobuf', 'routing_key'])):
                return

        self.msgContents[msg_name] = content_dict
        with open(join(self.msg_dir, msg_name), 'wb') as f:
            pickle.dump(content_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    def do_update(self, rest):
        '''updates fields of a msg. e.g. update n1 {'field1': 'newValue'}'''
        '''TODO: needs to validate by calling self.store()'''
        [msg_name, rest] = rest.split(maxsplit=1)
        update_to_content_dict = self.parse1(rest)
        if not update_to_content_dict:
            return
        if msg_name in self.msgContents:
            self.msgContents[msg_name].update(update_to_content_dict)
        else:
            self.msgContents[msg_name] = update_to_content_dict
        with open(join(self.msg_dir, msg_name), 'wb') as f:
            pickle.dump(self.msgContents[msg_name], f, protocol=pickle.HIGHEST_PROTOCOL)

    def do_show(self, rest):
        '''shows a msg. e.g. show msg1'''
        tokens = rest.split()
        if len(tokens) != 1:
            print('show expects 1 argument, {0} given'.format(len(rest)-1))
            return
        msg_name = rest
        if msg_name in self.msgContents:
            content_dict = self.msgContents[msg_name]
            print('{0}={1}'.format(msg_name, content_dict))
        else:
            print('{0} does not exist'.format(msg_name))

    def do_remove(self, rest):
        '''removes field from a msg. e.g. remove field1'''
        '''TODO: needs to validate by calling self.store()'''
        tokens = rest.split()
        if len(tokens) != 2:
            print('remove expects 2 arguments, {0} given'.format(len(tokens)))
            return
        [msg_name, field] = tokens
        if msg_name in self.msgContents:
            del self.msgContents[msg_name][field]
        else:
            print('{0} does not exist'.format(msg_name))
            return
        with open(join(self.msg_dir, msg_name), 'wb') as f:
            pickle.dump(self.msgContents[msg_name], f, protocol=pickle.HIGHEST_PROTOCOL)

    def do_delete(self, rest):
        '''deletes a msg. e.g. delete msg1'''
        tokens = rest.split()
        if len(tokens) != 1:
            print('delete expects 1 argument, {0} given'.format(len(rest)-1))
            return
        msg_name = rest
        if msg_name in self.msgContents:
            del self.msgContents[msg_name]
            os.remove(join(self.msg_dir, msg_name))
        else:
            print('{0} does not exist'.format(msg_name))

    def do_copy(self, rest):
        '''copies a msg. copy msg1 msg1_copy'''
        tokens = rest.split()
        if len(tokens) != 2:
            print('copy expects 2 arguments, {0} given'.format(len(tokens)))
            return
        [src, dest] = tokens
        if src in self.msgContents:
            content_dict = self.msgContents[src]
        else:
            print('{0} does not exist'.format(src))
        self.store(dest, copy.deepcopy(content_dict))

    def do_rename(self, rest):
        '''renames a msg'''
        # rename oldname newname
        pass

    def do_msgs(self, rest):
        '''shows all msgs. e.g. msgs'''
        for msg_name, content_dict in self.msgContents.items():
            print('{0} {1}'.format(msg_name, content_dict))

    def do_send(self, rest):
        '''sends a msg. e.g. send msg1'''
        s = rest.split(maxsplit=1)
        if len(s) != 1:
            print('send expects exactly 1 argument')
            return
        msg_name = s[0]
        if msg_name in self.msgContents:
            content_dict = self.msgContents[msg_name]
            dest_exchange = None
            if 'mqexchange' in content_dict:
                mqexchange = content_dict['mqexchange']
            else:
                print('content dictionary must have a mqexchange')
                return
            if 'protoimport' in content_dict:
                protoimport = content_dict['protoimport']
            else:
                print('content dictionary must have a protoimport')
                return
            if 'protobuf' in content_dict:
                protobuf = content_dict['protobuf']
            else:
                print('content dictionary must have a protobuf')
                return
            for ce in exchange_config.exchanges:
                if (ce['name'] == mqexchange):
                    dest_exchange = ce
            if not dest_exchange:
                print('unknown mqexchange {0}'.format(mqexchange))
                return
            if not (protoimport, protobuf) in dest_exchange['sendable_protobufs']:
                print('protoimport {0}, protobuf {1} not allowed on mqexchange {2}'.format(protoimport, protobuf, mqexchange))
                return
            print('sending {0}'.format(content_dict))
            b = pickle.dumps([mqexchange, content_dict])
            b = pickle.dumps(content_dict)
            self.our_conn.send(b)
        else:
            print('msg name {0} does not exist'.format(msg_name))

    def do_quit(self, rest):
        '''quits the program'''
        print("quitting")
        b = pickle.dumps(None)
        self.our_conn.send(b)
        raise SystemExit

    def emptyline(self):
        if self.our_conn.poll():
            b = self.our_conn.recv()
            s = pickle.loads(b)
            print('{0}'.format(s))


parser = argparse.ArgumentParser(description='Console for interacting with RabbitMQ using protobufs.')
parser.add_argument('exch_conf', help='the config file for the exchange(s)')
args = parser.parse_args()
exch_conf_filename = args.exch_conf
exchange_config = importlib.import_module(exch_conf_filename)

prompt = MyPrompt()
prompt.prompt = '> '
prompt.cmdloop()
