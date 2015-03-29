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
    var oct_len uint8
    var data    string
    question.qname = nil
    for {
        binary.Read(io.Reader(s), binary.BigEndian, &oct_len)
        if oct_len == 0 {
            binary.Read(io.Reader(s), binary.BigEndian, &question.qtype)
            binary.Read(io.Reader(s), binary.BigEndian, &question.qclass)
            return
        }
        fmt.Printf("oct_len : %d\n",  int64(oct_len))
        data = string(s.Next(int(oct_len)))
        question.qname = append(question.qname, data)
    }
}

func (answer *DNSAnswer) Init(s *bytes.Buffer) {
}

func (answer *DNSAuthority) Init(s *bytes.Buffer) {
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

    var buf [1024]byte

    for {
        rlen, remote, err := sock.ReadFromUDP(buf[:])

        fmt.Println(rlen)
        fmt.Println(buf)
        r := bytes.NewBuffer(buf[:rlen])
        fmt.Println(r)
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
        fmt.Println(remote)
        fmt.Println(err)

        fmt.Println(dns.header.GetField("ID"))
        fmt.Println(dns.header.GetField("QR"))
        fmt.Println(dns.question)
        
        fmt.Println(dns.header.ancount)
    }
}


func main() {
    var server DNSServer

    server.Run()
    
/*
    fmt.Println("Hello World")

    var buf [1024]byte

    addr, err := net.ResolveUDPAddr("udp", ":53")
    sock, err := net.ListenUDP("udp", addr)
    fmt.Println(err)
    for {
        rlen, remote, err := sock.ReadFromUDP(buf[:])
        fmt.Println(buf)
        fmt.Println(remote)
        fmt.Println(err)
        fmt.Println(rlen)
    }
*/
}

