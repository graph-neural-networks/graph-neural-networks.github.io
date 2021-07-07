all: run

run:
	go run main.go

launch-service:
	go build channels_stats
	kill $$(ps aux | grep './[c]hannels_stats' | awk '{print $$2}') || true
	nohup ./channels_stats &> stdout.txt &