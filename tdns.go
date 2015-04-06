/*

    Author : Hans Kramer

      Date : Jan 2015

      Code : Go implementation of (limited) DNS server
             Port from my Python Code

 */
package main

import "fmt"
import "net"
import "encoding/binary"
import "bytes"
import "io"


const max_message_length int = 512

const (
    A     = 1   // a host address
    NS    = 2   // an authoritative name server
    MD    = 3   // a mail destination (Obsolete - use MX)
    MF    = 4   // a mail forwarder (Obsolete - use MX)
    CNAME = 5   // the canonical name for an alias
    SOA   = 6   // marks the start of a zone of authority
    MB    = 7   // a mailbox domain name (EXPERIMENTAL)
    MG    = 8   // a mail group member (EXPERIMENTAL)
    MR    = 9   // a mail rename domain name (EXPERIMENTAL)
    NULL  = 10  // a null RR (EXPERIMENTAL)
    WKS   = 11  // a well known service description
    PTR   = 12  // a domain name pointer
    HINFO = 13  // host information
    MINFO = 14  // mailbox or mail list information
    MX    = 15  // mail exchange
    TXT   = 16  // text strings
    AXFR  = 252 // A request for a transfer of an entire zone
    MAILB = 253 // A request for mailbox-related records (MB, MG or MR)
    MAILA = 254 // A request for mail agent RRs (Obsolete - see MX)
    ALL   = 255 // A request for all records
)

const (
    IN = 1 // the Internet
    CS = 2 // the CSNET class (Obsolete - used only for examples in some obsolete RFCs)
    CH = 3 // the CHAOS class
    HS = 4 // Hesiod [Dyer 87]
)


type Header struct {
    id      uint16
    status  uint16
    qdcount uint16
    ancount uint16
    nscount uint16
    arcount uint16
}

type Question struct {
    qname  []string
    qtype  uint16
    qclass uint16 
}

type ResourceRecord struct {
    name     []string
    rr_type  uint16
    class    uint16 
    ttl      uint16
    rdlength uint16
    rdata    []byte
}

type Message struct {
    header   Header
    question []Question  // allow for multiple questions even though most DNS servers don't support this
}

func (header *Header) Unpack(r io.Reader) {
    binary.Read(r, binary.BigEndian, &header.id)
    binary.Read(r, binary.BigEndian, &header.status)
    binary.Read(r, binary.BigEndian, &header.qdcount)
    binary.Read(r, binary.BigEndian, &header.ancount)
    binary.Read(r, binary.BigEndian, &header.nscount)
    binary.Read(r, binary.BigEndian, &header.arcount)
}

func (header Header) Pack() []byte {
    buf := new(bytes.Buffer)

    binary.Write(buf, binary.BigEndian, header.id)
    binary.Write(buf, binary.BigEndian, header.status)
    binary.Write(buf, binary.BigEndian, header.qdcount)
    binary.Write(buf, binary.BigEndian, header.ancount)
    binary.Write(buf, binary.BigEndian, header.nscount)
    binary.Write(buf, binary.BigEndian, header.arcount)
 
    return buf.Bytes()
}

func ReadFQName(s *bytes.Buffer) []string {
    var oct_len uint8
    var data    []string
    for {
        binary.Read(io.Reader(s), binary.BigEndian, &oct_len)
        if oct_len == 0 {
            return data
        }
        data = append(data, string(s.Next(int(oct_len))))
    }
}

func WriteFQName(name []string) []byte {
    buf := new(bytes.Buffer)

    for _, label := range name {
        var length byte = byte(len(label))
        binary.Write(buf, binary.BigEndian, length)
        buf.WriteString(label)
    }

    return buf.Bytes()
}

func (question *Question) Unpack(s *bytes.Buffer) {
    question.qname = ReadFQName(s)
    binary.Read(io.Reader(s), binary.BigEndian, &question.qtype)
    binary.Read(io.Reader(s), binary.BigEndian, &question.qclass)
}

func (question Question) Pack() []byte {
    buf := new(bytes.Buffer)

    buf.Write(WriteFQName(question.qname))
    binary.Write(buf, binary.BigEndian, question.qtype)
    binary.Write(buf, binary.BigEndian, question.qclass)
  
    return buf.Bytes()
}

func (message *Message) Unpack(s *bytes.Buffer) {
    message.header.Unpack(s)

    message.question = make([]Question, message.header.qdcount)
    for i:=0; i<int(message.header.qdcount); i++ {
        message.question[i].Unpack(s)
    }

    fmt.Println(message)
}

func (message Message) Pack() []byte {
    var data = message.header.Pack()

    for i:=0; i<int(message.header.qdcount); i++ {
        data = append(data, message.question[i].Pack()...)
    }

    return data
}



type DNSHeader struct {
    id      uint16
    status  uint16
    qdcount uint16
    ancount uint16
    nscount uint16
    arcount uint16
}

type DNSQuestion struct {
    qname  []string
    qtype  uint16
    qclass uint16 
}

type DNSAnswer struct {
    name     []string
    atype    uint16
    class    uint16 
    ttl      uint16
    rdlength uint16
    rdata    []byte
}

type DNSAuthority struct {
    name     []string
    atype    uint16
    class    uint16 
    ttl      uint16
    rdlength uint16
    rdata    []byte
}

type DNSServer struct {
    addr      *net.UDPAddr
    header    DNSHeader
    question  DNSQuestion 
    answer    DNSAnswer
    authority DNSAuthority
}


func (header *DNSHeader) Init(r io.Reader) {
    binary.Read(r, binary.BigEndian, &header.id)
    binary.Read(r, binary.BigEndian, &header.status)
    binary.Read(r, binary.BigEndian, &header.qdcount)
    binary.Read(r, binary.BigEndian, &header.ancount)
    binary.Read(r, binary.BigEndian, &header.nscount)
    binary.Read(r, binary.BigEndian, &header.arcount)
}

func (question *DNSQuestion) Init(s *bytes.Buffer) {
    question.qname = ReadFQName(s)
    binary.Read(io.Reader(s), binary.BigEndian, &question.qtype)
    binary.Read(io.Reader(s), binary.BigEndian, &question.qclass)
}

func (answer *DNSAnswer) Init(s *bytes.Buffer) {
    answer.name  = ReadFQName(s)
    binary.Read(io.Reader(s), binary.BigEndian, &answer.atype)
    binary.Read(io.Reader(s), binary.BigEndian, &answer.class)
    binary.Read(io.Reader(s), binary.BigEndian, &answer.ttl)
    binary.Read(io.Reader(s), binary.BigEndian, &answer.rdlength)
//  answer.rdata =
}

func (authority *DNSAuthority) Init(s *bytes.Buffer) {
    authority.name = ReadFQName(s)
    binary.Read(io.Reader(s), binary.BigEndian, &authority.atype)
    binary.Read(io.Reader(s), binary.BigEndian, &authority.class)
    binary.Read(io.Reader(s), binary.BigEndian, &authority.ttl)
    binary.Read(io.Reader(s), binary.BigEndian, &authority.rdlength)
//  authority.rdata =
}

func (header DNSHeader) GetField(field string) uint16 {
    if field == "ID" {
        return header.id
    }
    if field == "QR" {
        return (header.status & 0x8000) >> 15
    }
    return 0
}


func (dns DNSServer) Run() {
    dns.addr, _  = net.ResolveUDPAddr("udp", ":53")
    sock, _     := net.ListenUDP("udp", dns.addr)

    var buf [max_message_length]byte

    for {
        rlen, remote, err := sock.ReadFromUDP(buf[:])
        fmt.Println(err)
        fmt.Println(remote)

        fmt.Println(rlen)
        fmt.Println(buf)
        r := bytes.NewBuffer(buf[:rlen])
        fmt.Println(r)

        var message Message 
        message.Unpack(r)
        if message.question[0].qtype == A {
            fmt.Println("A Record")
        }
        fmt.Println(message.Pack())
        fmt.Println(message.question[0].qtype)
        fmt.Println(message.question[0].qtype)
        
/*
        dns.header.Init(r)
        if dns.header.qdcount > 0 {  // for now only handle a single question requests 
            dns.question.Init(r)
        }
        if dns.header.ancount > 0 {
            dns.answer.Init(r)
        } 
        if dns.header.arcount > 0 {
            dns.authority.Init(r)
        } 
 
//        fmt.Printf("header : %04X %04X %04X %04X\n", id, status, qdcount, ancount)

        fmt.Println(dns.header.GetField("ID"))
        fmt.Println(dns.header.GetField("QR"))
        fmt.Println(dns.question)
*/
        
//        fmt.Println(dns.header.ancount)
    }
}


func main() {
    var server DNSServer

    server.Run()
}

