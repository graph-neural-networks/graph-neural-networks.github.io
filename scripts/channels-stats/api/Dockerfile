FROM golang:alpine AS build

WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -tags netgo -ldflags '-w' -o /out/channel_stats.exe channels_stats

FROM alpine AS bin
RUN adduser -S -D -H -h /app appuser
USER appuser
COPY --from=build /out/channel_stats.exe /app/channel_stats.exe
WORKDIR /app/
ENTRYPOINT [ "/app/channel_stats.exe" ]

EXPOSE 8000