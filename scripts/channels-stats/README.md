# RocketChat Channels Statistics Server
It's a simple Go web app that fetches channels statistics from RocketChat APIs and serves it to users so that it can be used to encourage people to engage more in on-going conversations.

It scores each channel based on the number new messages they have in the last `x` seconds. To make it more realistic, it incorporates the previous score in its calculations. In other words, if some channel was active in the previous `x` seconds but it is not now, we will still show it (You can configure it using the OLD_SCORE_COEFF environment variable, See below).

## How to use
### Step 0: Prepare RocketChat credential
Use the following command
```bash
curl https://emnlp2020.rocket.chat/api/v1/login \
     -d "user=<my_username_or_email>&password=<my_passpowrd>" | python3 -m json.tool
```
It will output something like this:
```
{
    "status": "success",
    "data": {
        "userId": "....",
        "authToken": ".....",
        "me": ...
    }
}
```
Grab `userId` and `authToken` values and export them as environment variables:
```bash
export AUTH_TOKEN=<auth-token-value>
export USER_ID=<user-id-value>
```
*Note: Replace https://emnlp2020.rocket.chat with your rocket.chat server url*
### Step 1: Export required variables
To run the web server, you need specify some configuratins through environment variables:
```bash
export SERVER_URL="https://emnlp2020.rocket.chat/"
export NUM_CHANNEL_TO_SHOW=20   # The API will give you the top N channels. You need to specify N here
export UPDATE_INTERVAL=900        # The delay between each stats update. The unit for this variable is seconds
export OLD_SCORE_COEFF=0.8      # The more this value is close to 1, the more active channels remain 
                                # in the list (even if it is not active anymore)
```
### Step 1.5: Modify the configuration (Optional)
To manage what channels should be included and what channels should be ignored in the statts, you need to edit these two files:
1. `api/config/source_channels.txt`: It specify what channels will be considered. By default it's the following:
```text
*
```
which means we consider all channels.

2. `api/config/blacklist.txt`: It sets the channels we will ignore in the stats. By default it's empty. But the following is an example:
```text
paper-*
workshop-*
paper-xxx
```
### Step 2: Run the web app
**Without Docker (Recommended)**
1. Install Go ([Official Doc](https://golang.org/doc/install))
2. `cd api`
3. `make launch-service`

This method is recommended since it provides a huge performance gain over docker

**With Docker**
1. `docker-compose build`
2. `docker-compose up`

## Performance Benchmark
```
$ wrk -t12 -c2000 -d30s http://localhost:8000/stats.json
Running 30s test @ http://localhost:8000/stats.json
  12 threads and 2000 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.50ms  581.78us  23.33ms   85.41%
    Req/Sec     7.60k     4.83k   37.49k    53.22%
  2042107 requests in 30.10s, 4.07GB read
  Socket errors: connect 1753, read 89, write 0, timeout 0
Requests/sec:  67839.94
Transfer/sec:    138.45MB
```
*On MacBook Pro 2017 15inch*

## API
```bash
$ curl http://localhost:8000/stats.json
{
  "stats": [
    {
      "channel": {
        "_id": "<channel_id>",
        "name": "<channel_name>",
        "msgs": 4,           // number of messages
        "usersCount": 11     // number of users
      },
      "score": 0             // score calculated based on the #message difference (float value)
    },
    ...
  ],
  "last_update": 1604437046  // last update's unix epoch timestamp
}
```
