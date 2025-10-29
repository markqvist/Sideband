// +build

// based on https://github.com/paypal/gatt/blob/master/examples/server.go

package main

import (
	"fmt"
	"log"
        "time"
	"github.com/paypal/gatt"
        "github.com/paypal/gatt/linux/cmd"
)


var DefaultServerOptions = []gatt.Option{
	gatt.LnxMaxConnections(1),
	gatt.LnxDeviceID(-1, false),
	gatt.LnxSetAdvertisingParameters(&cmd.LESetAdvertisingParameters{
		AdvertisingIntervalMin: 0x04ff,
		AdvertisingIntervalMax: 0x04ff,
		AdvertisingChannelMap:  0x7,
	}),
}


func NewTestPythonService() *gatt.Service {
	n := 0
	s := gatt.NewService(gatt.MustParseUUID("16fe0d00-c111-11e3-b8c8-0002a5d5c51b"))

	s.AddCharacteristic(gatt.MustParseUUID("16fe0d01-c111-11e3-b8c8-0002a5d5c51b")).HandleReadFunc(
		func(rsp gatt.ResponseWriter, req *gatt.ReadRequest) {
			n = 0
			log.Println("Echo")
			fmt.Fprintf(rsp, "test")
		})
	s.AddCharacteristic(gatt.MustParseUUID("16fe0d02-c111-11e3-b8c8-0002a5d5c51b")).HandleWriteFunc(
		func(r gatt.Request, data []byte) (status byte) {
			n = 0
			log.Println("Reset counter")
			return gatt.StatusSuccess
		})
	s.AddCharacteristic(gatt.MustParseUUID("16fe0d03-c111-11e3-b8c8-0002a5d5c51b")).HandleWriteFunc(
		func(r gatt.Request, data []byte) (status byte) {
			n++
			log.Println("Increment counter")
			return gatt.StatusSuccess
		})
	s.AddCharacteristic(gatt.MustParseUUID("16fe0d04-c111-11e3-b8c8-0002a5d5c51b")).HandleReadFunc(
		func(rsp gatt.ResponseWriter, req *gatt.ReadRequest) {
			log.Println("Response counter: ", n)
			fmt.Fprintf(rsp, "%d", n)
		})

	s.AddCharacteristic(gatt.MustParseUUID("16fe0d05-c111-11e3-b8c8-0002a5d5c51b")).HandleNotifyFunc(
		func(r gatt.Request, n gatt.Notifier) {
			log.Println("Notifications enabled")
			cnt := 1
			for !n.Done() {
				fmt.Fprintf(n, "%d", cnt)
				cnt++
				time.Sleep(100 * time.Millisecond)
			}
                        log.Println("Notifications disabled")
		})

	return s
}


func main() {
	d, err := gatt.NewDevice(DefaultServerOptions...)
        if err != nil {
		log.Fatalf("Failed to open device, err: %s", err)
	}

	d.Handle(
		gatt.CentralConnected(func(c gatt.Central) { fmt.Println("Connect: ", c.ID()) }),
		gatt.CentralDisconnected(func(c gatt.Central) { fmt.Println("Disconnect: ", c.ID()) }),
	)

	onStateChanged := func(d gatt.Device, s gatt.State) {
		fmt.Printf("State: %s\n", s)
		switch s {
		case gatt.StatePoweredOn:
			s1 := NewTestPythonService()
			d.AddService(s1)
			d.AdvertiseNameAndServices("KivyBLETest", []gatt.UUID{s1.UUID()})
		default:
		}
	}

	d.Init(onStateChanged)
	select {}
}
