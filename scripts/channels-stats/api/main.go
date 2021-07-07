package main

import (
	"channels_stats/server"
	"channels_stats/statsfetch"
)

func main() {
	statsfetch.SetupUpdater()
	server.RunServer()
}
