package server

import (
	"channels_stats/cache"
	"fmt"
	"net/http"
)

func stats(w http.ResponseWriter, req *http.Request) {
	response := cache.Response().Get().([]byte)
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Write(response)
}

func RunServer() {
	http.HandleFunc("/stats.json", stats)

	fmt.Println("Starting the http server on http://0.0.0.0:8000/stats.json ...")
	http.ListenAndServe(":80", nil)
}
