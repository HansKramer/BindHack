#! /usr/bin/python
#
#  Author : Hans Kramer
#
#    Date : Jan 2015
#
#  Working but plenty of bugs and half ass implementation
#  However, this is the first working version
#

import SocketServer
import socket
import struct
import sys

class DNSMessage:

    A   = 1
    NS  = 2
    PTR = 12
    MX  = 15

    IN = 1
    CS = 2
    CH = 3
    HS = 4

    def init(self, request):
        request, self._header     = request[12:], list(struct.unpack("!HHHHHH", request[0:12]))
        request, self._question   = self.unpack_question(request)
        request, self._answer     = self.unpack_answer(request)
        request, self._authority  = self.unpack_authority(request)
        request, self._additional = self.unpack_additional(request)

    def unpack_question(self, request):
        if self.get_header('QDCOUNT') == 0:
            return (request, None)
        # fix me when QDCOUNT != 1
        # and fix index checking
        qname = []
        index = 0
        while True:
            oct_len = struct.unpack('!B', request[index])[0]
            if oct_len == 0:
                qtype  = struct.unpack("!H", request[index+1:index+3])[0]
                qclass = struct.unpack("!H", request[index+3:index+5])[0]
                return (request[index+5:], [qname, qtype, qclass])
            qname.append(request[index+1:index+oct_len+1])
            index += oct_len + 1

    def unpack_resource_section(self, request):
        resource = []
        oct_len = struct.unpack("!B", request[0])[0]
        if oct_len & 0xc0 == 0xc0: # it's a pointer!
            resource += [struct.unpack("!H", request[0:2])[0] & 0x3f]
            index = 4
        else:
            print "implement me"
        resource += struct.unpack("!HHHH", request[index:index+8])
        # fix me: assume A IN
        resource += struct.unpack("!L", request[index+8:index+12])
        return resource

        
    def unpack_answer(self, request):
        if self.get_header('ANCOUNT') == 0:
            return (request, [])
        answer = self.unpack_resource_section(request)
        return (request[1:], answer)

    def get_data(self):
        request  = self.pack_header()
        request += self.pack_question()
        request += self.pack_answer()
        return request

    def get_question(self):
        return self._question

    def pack_header(self):
        return struct.pack("!HHHHHH", *self._header)

    def pack_question(self):
        # fix if question != 1
        request = ""
        for x in self._question[0]:
            request += struct.pack("!B", len(x))
            request += x
        return request + struct.pack("!BHH", 0, self._question[1], self._question[2])
       
    def pack_answer(self):
        request = ""
        if self.get_header('ANCOUNT') == 0:
            return ""    
        # need to handle multiple answers!
        #for x in self._answer[0]:
        #    request += struct.pack("!B", len(x))
        #    request += x
        #request += struct.pack("!B", 0)
        
        request += struct.pack("!H", self._answer[0])
        request += struct.pack("!H", self._answer[1])
        request += struct.pack("!H", self._answer[2])
        request += struct.pack("!L", self._answer[3])
        request += struct.pack("!H", self._answer[4])
        request += struct.pack("!L", self._answer[5])
        return request

    def unpack_authority(self, request):
        if self.get_header('NSCOUNT') == 0:
            return (request, None)
        # fix me
        return (request[1:], request[0])

    def unpack_additional(self, request):
        if self.get_header('ARCOUNT') == 0:
            return (request, None)
        # fix me
        return (request[1:], request[0])

#        qr     = (header[1] & 0x8000) >> 15
#        opcode = (header[1] & 0x7800) >> 11
#        aa     = (header[1] & 0x0400) >> 10
#        tc     = (header[1] & 0x0200) >> 9
#        rd     = (header[1] & 0x0100) >> 8
#        ra     = (header[1] & 0x0080) >> 7
#        z      = (header[1] & 0x0070) >> 4
#        rcode  = (header[1] & 0x000f)

    def set_answer(self, answer):
        self._answer = answer

    def set_header(self, field, value): 
        if field == 'QR':
            self._header[1] |= value << 15 
        if field == 'AA':
            self._header[1] |= value << 10 
        if field == 'RD':
            self._header[1] |= value << 8 
        if field == 'RA':
            self._header[1] |= value << 7
        if field == 'RCODE':
            self._header[1] |= (value & 0x0f)
        if field == 'QDCOUNT':
            self._header[2] = value
        if field == 'ANCOUNT':
            self._header[3] = value
        if field == 'NSCOUNT':
            self._header[4] = value
        if field == 'ARCOUNT':
            self._header[5] = value

    def get_header(self, field):
        if field == 'ID':
            return self._header[0]
        if field == 'QR':
            return (self._header[1] & 0x8000) >> 15
        if field == 'AA':
            return (self._header[1] & 0x0400) >> 10
        if field == 'RD':
            return (self._header[1] & 0x0100) >> 8
        if field == 'RCODE':
            return self._header[1] & 0x0f
        if field == 'QDCOUNT':
            return self._header[2]
        if field == 'ANCOUNT':
            return self._header[3]
        if field == 'NSCOUNT':
            return self._header[4]
        if field == 'ARCOUNT':
            return self._header[5]
        return None

    def __repr__(self):
        return "header:   " + str(self._header)   + "\n" +  \
               "question: " + str(self._question) + "\n" +  \
               "answer:   " + str(self._answer)   + "\n" + str(self._authority) + str(self._additional)
      

class DNSServer(SocketServer.BaseRequestHandler):

    def print_hex(self, text):
        i = 0
        for x in text:
            i += 1
            print "%02x" % ord(x),
            if i % 16 == 0:
                print
        print


    def send(self, data):
        self.request[1].sendto(data, self.client_address) 


    def not_found(self):
        dns_msg = DNSMessage() 
        dns_msg.init(self.request[0])
        dns_msg._header[1] = 0
        dns_msg.set_header("RCODE", 3)
        dns_msg.set_header("QR", 1)
        dns_msg.set_header("ANCOUNT", 0)
        dns_msg.set_header("QDCOUNT", 1)
        dns_msg.set_header("ARCOUNT", 0)
        self.send(dns_msg.get_data()) 


    def answer(self, ip, auth):
        dns_msg = DNSMessage() 
        dns_msg.init(self.request[0])
        dns_msg.set_answer([0xc00c, DNSMessage.A, DNSMessage.IN, 0xffff, 4, ip])
        dns_msg.set_header("QR", 1)
        dns_msg.set_header("AA", auth)
        dns_msg.set_header("RD", 0)
        dns_msg.set_header("RA", 1)
        dns_msg.set_header("ANCOUNT", 1)
        dns_msg.set_header("QDCOUNT", 1)
        dns_msg.set_header("ARCOUNT", 0)
        self.send(dns_msg.get_data()) 


    def recursion(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(self.request[0], ("192.168.1.3", 53))
        received = sock.recv(4096)
        dns_msg = DNSMessage() 
        dns_msg.init(received)
        if dns_msg.get_header("RCODE") != 0:
            return None, True
        else:
            return dns_msg._answer[5], dns_msg.get_header("AA")


    def get_request(self):
        dns_msg = DNSMessage() 
        dns_msg.init(self.request[0])
        request = dns_msg.get_question()
        if request[1] == DNSMessage.A and request[2] == DNSMessage.IN:
            try:
                octets = map(int, request[0][0].split('-'))
                for octet in octets:
                    if octet > 255:
                        raise Exception
                if len(octets) == 4:
                    return (((((octets[0]<<8) + octets[1])<<8) + octets[2])<<8) + octets[3], True
            except:
                pass
            return self.recursion()
        else:
            print "We don't handle:", request[1], request[2]
        return None


    def handle(self):
        ip, auth = self.get_request()
        if ip == None:
            self.not_found()
        else:
            self.answer(ip, auth)


if __name__ == "__main__":
    host = "localhost"
    port = 53
    server = SocketServer.UDPServer((host, port), DNSServer)
    server.serve_forever()
