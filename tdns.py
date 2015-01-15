#! /usr/bin/python
#
#  Author : Hans Kramer
#
#    Date : Jan 2015
#
#  This code is so not working yet, it ain't funny
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
        request, self._header   = request[12:], struct.unpack("!HHHHHH", request[0:12])
        request, self._question   = self.unpack_question(request)
        request, self._answer     = self.unpack_answer(request)
        request, self._authority  = self.unpack_authority(request)
        request, self._additional = self.unpack_additional(request)

    def get_data(self):
        request = struct.pack("!HHHHHH", *self._header)
        for x in self._question[:-2]:
            print x
            request += struct.pack("!B", len(x))
            request += x
        request += struct.pack("!BHH", 0, self._question[-2], self._question[-1])
        return request

    def unpack_question(self, request):
        # fix me when QDCOUNT != 1
        question = []
        index    = 0
        while True:
            oct_len = struct.unpack('!B', request[index])[0]
            if oct_len == 0:
                question.append(struct.unpack("!H", request[index+1:index+3])[0])
                question.append(struct.unpack("!H", request[index+3:index+5])[0])
                return (request[index+5:], question)
            question.append(request[index+1:index+oct_len+1])
            index += oct_len + 1

    def unpack_answer(self, request):
        if self.get_header('ANCOUNT') == 0:
            return (request, [])
        # fix me
        return (request[1:], request[0])

    def pack_answer(self):
        for answer in self._answer:
            print answer 
        return None

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

    def get_header(self, field):
        if field == 'ID':
            return self._header[0]
        if field == 'QR':
            return (self._header[1] & 0x8000) >> 15
        if field == 'RD':
            return (self._header[1] & 0x0100) >> 8
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
        return str(self._header) + str(self._question) + str(self._answer) + str(self._authority) + str(self._additional)
      

class DNSServer(SocketServer.BaseRequestHandler):

    def handle(self):
        data   = self.request[0]
        print len(data)
        dns_msg = DNSMessage() 
        dns_msg.init(data)
        print dns_msg.get_header('RD')
        print dns_msg
        x2 = dns_msg.get_data()
        x1 = data
        print len(x1), len(x2)
        if x1 == x2:
            print "equal"
        dns_msg._answer = [("fuck2", "hanskramer", "com"), DNSMessage.A, DNSMessage.IN, 0xffff, 4, 0]
         
#        host = "hanskramer.com"
#        port = 53
#        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        sock.sendto(data, (host, port)) 
#        recv = sock.recv(1024)
#        dns_msg = DNSMessage() 
#        dns_msg.init(data)
#        print "received", dns_msg
        
        
        #socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    host = "localhost"
    port = 53
    server = SocketServer.UDPServer((host, port), DNSServer)
    server.serve_forever()
    print "bye!"
