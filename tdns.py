#! /usr/bin/python
#
#  Author : Hans Kramer
#
#    Date : Jan 2015
#
#  Working but plenty of bugs and half ass implementation
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
        request = ""
        for x in self._question[:-2]:
            request += struct.pack("!B", len(x))
            request += x
        return request + struct.pack("!BHH", 0, self._question[-2], self._question[-1])
       
    def pack_answer(self):
        # need to handle multiple answers!
        request = ""
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
        return "header:   " + str(self._header)   + "\n" +  \
               "question: " + str(self._question) + "\n" +  \
               "answer:   " + str(self._answer)   + "\n" + str(self._authority) + str(self._additional)
      

class DNSServer(SocketServer.BaseRequestHandler):

    def handle(self):
        data   = self.request[0]

        dns_msg = DNSMessage() 
        dns_msg.init(data)

        print dns_msg.get_question()
        try:
            octets = map(int, dns_msg.get_question()[0].split('-'))
            ip = (((((octets[0]<<8) + octets[1])<<8) + octets[2])<<8) + octets[3]
        except:
            ip = 0
 
        answer = [0xc00c, DNSMessage.A, DNSMessage.IN, 0xffff, 4, ip]

        dns_msg.set_answer(answer)
        dns_msg.set_header("QR", 1)
        dns_msg.set_header("AA", 1)
        dns_msg.set_header("RD", 0)
        dns_msg.set_header("RA", 1)
        dns_msg.set_header("ANCOUNT", 1)
        dns_msg.set_header("QDCOUNT", 1)
        dns_msg.set_header("ARCOUNT", 0)

        x2 = dns_msg.get_data()
        self.request[1].sendto(x2, self.client_address) 


if __name__ == "__main__":
    host = "localhost"
    port = 53
    server = SocketServer.UDPServer((host, port), DNSServer)
    server.serve_forever()
