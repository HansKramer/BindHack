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


type DNSServer struct {
    addr *net.UDPAddr
}


func (dns DNSServer) Run() {
    dns.addr, _ = net.ResolveUDPAddr("udp", ":53")
    sock, _ := net.ListenUDP("udp", dns.addr)

    var buf [1024]byte

    for {
        rlen, remote, err := sock.ReadFromUDP(buf[:])
        fmt.Println(buf)
        r := bytes.NewBuffer(buf[:])
        var value int16
        binary.Read(r, binary.BigEndian, &value)   
        fmt.Printf("header : %02X\n", value)
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

