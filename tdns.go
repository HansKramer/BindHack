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


type DNSServer struct {
    addr *net.UDPAddr
}

type DNSHeader struct {
    id      uint16
    status  uint16
    qdcount uint16
    ancount uint16
    nscount uint16
    arcount uint16
}


func (header DNSHeader) Init(r io.ByteReader) {
    binary.Read(r, binary.BigEndian, &id)   
    binary.Read(r, binary.BigEndian, &status)   
    binary.Read(r, binary.BigEndian, &qdcount)   
    binary.Read(r, binary.BigEndian, &ancount)   
}


func (dns DNSServer) Run() {
    dns.addr, _ = net.ResolveUDPAddr("udp", ":53")
    sock, _ := net.ListenUDP("udp", dns.addr)

    var buf [1024]byte

    for {
        rlen, remote, err := sock.ReadFromUDP(buf[:])
        fmt.Println(buf)
        r := bytes.NewBuffer(buf[0:6])
        var header DNSHeader
        header.Init(&r)
 
//        var id, status, qdcount, ancount uint16
//        binary.Read(r, binary.BigEndian, &id)   
//        binary.Read(r, binary.BigEndian, &status)   
//        binary.Read(r, binary.BigEndian, &qdcount)   
//        binary.Read(r, binary.BigEndian, &ancount)   
//        binary.Read(r, binary.BigEndian, &nscount)   
//        binary.Read(r, binary.BigEndian, &arcount)   
//        fmt.Printf("header : %04X %04X %04X %04X\n", id, status, qdcount, ancount)
        fmt.Println(remote)
        fmt.Println(err)
        fmt.Println(rlen)
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

