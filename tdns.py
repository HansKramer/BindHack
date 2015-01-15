#! /usr/bin/python
#
#

import SocketServer
import socket
import struct
import sys

class DNSMessage:

    def init(self, request):
        request, self._header   = request[12:], struct.unpack("!HHHHHH", request[0:12])
        # fix me when QDCOUNT != 1
        request, self._question   = self.unpack_question(request)
        request, self._answer     = self.unpack_answer(request)
        request, self._authority  = self.unpack_authority(request)
        request, self._additional = self.unpack_additional(request)

    def unpack_question(self, request):
        question = []
        index    = 0
        while True:
            oct_len = struct.unpack('!B', request[index])[0]
            if oct_len == 0:
                question.append(struct.unpack("!H", request[index+1:index+3])[0])
                question.append(struct.unpack("!H", request[index+3:index+5])[0])
                return (request[index+6:], question)
            question.append(request[index+1:index+oct_len+1])
            index += oct_len + 1

    def unpack_answer(self, request):
        if self.get_header('ANCOUNT') == 0:
            return (request, None)
        # fix me
        return (request[1:], request[0])

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

    def get_header(self, record):
        header = struct.unpack("!HHHHHH", record[0:12])
        qr     = (header[1] & 0x8000) >> 15
        opcode = (header[1] & 0x7800) >> 11
        aa     = (header[1] & 0x0400) >> 10
        tc     = (header[1] & 0x0200) >> 9
        rd     = (header[1] & 0x0100) >> 8
        ra     = (header[1] & 0x0080) >> 7
        z      = (header[1] & 0x0070) >> 4
        rcode  = (header[1] & 0x000f)
        print header, qr, opcode, tc, rd, ra, z, rcode, header[2]
        return record[12:]

    def get_question(self, record): 
        index = 0
        while True:
            oct_len = struct.unpack('!B', record[index])[0]
            if oct_len == 0:
                print struct.unpack('!HH', record[index+1:index+5])
                print record[index+1:index+3]
                print record[index+3:index+5]
                return
            print record[index+1:index+oct_len+1]
            index += oct_len + 1
     

    def handle(self):
        data   = self.request[0]
        dns_msg = DNSMessage() 
        dns_msg.init(data)
        print dns_msg.get_header('RD')
        print dns_msg

        host = "hanskramer.com"
        port = 53
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (host, port)) 
        recv = sock.recv(1024)
        dns_msg = DNSMessage() 
        dns_msg.init(data)
        print "received", dns_msg
        
        
        #socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    host = "localhost"
    port = 53
    server = SocketServer.UDPServer((host, port), DNSServer)
    server.serve_forever()
    print "bye!"
