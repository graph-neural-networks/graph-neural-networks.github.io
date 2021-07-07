package statsfetch

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/gobwas/glob"

	"channels_stats/cache"
)

type channel struct {
	ID         string `json:"_id"`
	Name       string `json:"name"`
	NumMsgs    int    `json:"msgs"`
	UsersCount int    `json:"usersCount"`
	Diff       int    `json:"diff"`
}

type rocketchatAPIResponse struct {
	Channels []channel `json:"channels"`
	Count    int       `json:"count"`
	Offset   int       `json:"offset"`
	Total    int       `json:"total"`
}

type ChannelScore struct {
	Channel channel `json:"channel"`
	Score   float32 `json:"score"`
}

type ApiResponse struct {
	Stats      []ChannelScore `json:"stats"`
	LastUpdate int64          `json:"last_update"`
}

var id2channel map[string]channel
var id2score map[string]float32
var backlistGlobs []glob.Glob
var sourceGlobs []glob.Glob
var maxNumChannels int
var oldScoreCoeff float32

func getChannelsFromAPI() ([]channel, error) {
	ServerURL := os.Getenv("SERVER_URL")
	AuthToken := os.Getenv("AUTH_TOKEN") // "mfaIuiGG7jl0rCf0Il80KblK-Z0oQQzNYlagO4vwFX1"
	UserID := os.Getenv("USER_ID")       //"iEFTSv3sojYLaqb6r"
	APIURL := ServerURL + "/api/v1/channels.list?count=%d&offset=%d"

	defaultCount, offset := 100, 0

	allChannels := make([]channel, 0)
	for true {
		url := fmt.Sprintf(APIURL, defaultCount, offset)
		req, err := http.NewRequest("GET", url, nil)
		req.Header.Add("X-Auth-Token", AuthToken)
		req.Header.Add("X-User-Id", UserID)

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			return nil, err
		}
		var result rocketchatAPIResponse
		json.NewDecoder(resp.Body).Decode(&result)
		resp.Body.Close()

		allChannels = append(allChannels, result.Channels...)

		if result.Count < defaultCount {
			break
		}
		offset += defaultCount
	}

	return allChannels, nil
}

func readGlobs(filepath string) []glob.Glob {
	globs := make([]glob.Glob, 0)

	bytesRead, err := ioutil.ReadFile(filepath)
	if err != nil {
		return globs
	}

	fileContent := string(bytesRead)
	lines := strings.Split(fileContent, "\n")
	for _, pattern := range lines {
		if len(pattern) == 0 {
			break
		}
		g := glob.MustCompile(strings.TrimSpace(pattern))
		globs = append(globs, g)
	}

	return globs
}

func initialize() {
	sourceGlobs = readGlobs("config/source_channels.txt")
	fmt.Printf("Source Channels[%d]:\n[\n", len(sourceGlobs))
	for _, g := range sourceGlobs {
		fmt.Print("\t")
		fmt.Println(g)
	}
	fmt.Println("]")

	backlistGlobs = readGlobs("config/blacklist.txt")
	fmt.Printf("Blacklist[%d]:\n[\n", len(backlistGlobs))
	for _, g := range backlistGlobs {
		fmt.Print("\t")
		fmt.Println(g)
	}
	fmt.Println("]")
}

func prepareResults(channelScores []ChannelScore) []ChannelScore {
	// Sort based on the channel score
	sort.SliceStable(channelScores, func(i, j int) bool {
		return channelScores[i].Score > channelScores[j].Score
	})

	// Separate zero and non zero scores
	chScrsNonZero := make([]ChannelScore, 0)
	chScrsZero := make([]ChannelScore, 0)
	for _, cs := range channelScores {
		if cs.Score == 0 {
			chScrsZero = append(chScrsZero, cs)
		} else {
			chScrsNonZero = append(chScrsNonZero, cs)
		}
	}

	// Shuffle channels with a zero score
	rand.Shuffle(len(chScrsZero), func(i, j int) {
		chScrsZero[i], chScrsZero[j] = chScrsZero[j], chScrsZero[i]
	})

	channelScores = append(chScrsNonZero, chScrsZero...)

	max := maxNumChannels
	if max > len(channelScores) {
		max = len(channelScores)
	}

	channelScores = channelScores[:max]

	return channelScores
}

func update() {
	if id2channel == nil {
		id2channel = map[string]channel{}
	}
	if id2score == nil {
		id2score = map[string]float32{}
	}

	fmt.Println("U: " + time.Now().String())
	allChannels, err := getChannelsFromAPI()
	if err != nil {
		fmt.Println(err)
		return
	}

	channelScores := make([]ChannelScore, 0)
	for _, channelStat := range allChannels {
		isIncluded := false
		for _, g := range sourceGlobs {
			isIncluded = isIncluded || g.Match(channelStat.Name)
		}
		if !isIncluded {
			continue
		}

		isBlacklisted := false
		for _, g := range backlistGlobs {
			isBlacklisted = isBlacklisted || g.Match(channelStat.Name)
		}
		if isBlacklisted {
			continue
		}

		oldStat, statExists := id2channel[channelStat.ID]
		oldScore, scoreExists := id2score[channelStat.ID]

		// Subtract # of users from # of msgs to have a better approximation
		// since RocketChat counts users joining the channel toward its # of msgs
		if channelStat.NumMsgs >= channelStat.UsersCount {
			channelStat.NumMsgs -= channelStat.UsersCount
		}

		diff := 0
		if statExists {
			diff = channelStat.NumMsgs - oldStat.NumMsgs
		}

		if !scoreExists {
			oldScore = 0
		}

		var score float32 = 0.
		if oldScore < 1. && diff >= 1 {
			score = float32(diff)
		} else {
			score = oldScoreCoeff*oldScore + (1.-oldScoreCoeff)*float32(diff)
		}

		if score < 0.05 {
			score = 0.
		}

		channelStat.Diff = diff
		channelScores = append(channelScores, ChannelScore{channelStat, score})

		id2channel[channelStat.ID] = channelStat
		id2score[channelStat.ID] = score
	}

	channelScores = prepareResults(channelScores)

	apiResponse := ApiResponse{channelScores, time.Now().Unix()}
	response, err := json.Marshal(apiResponse)
	if err != nil {
		fmt.Println(err)
		return
	}

	cache.Response().Set(response)
}

func SetupUpdater() {
	initialize()

	UpdateInterval, err := strconv.Atoi(os.Getenv("UPDATE_INTERVAL"))
	if err != nil {
		panic(err)
	}
	fmt.Printf("UPDATE_INTERVAL = %d\n", UpdateInterval)

	Coeff, err := strconv.ParseFloat(os.Getenv("OLD_SCORE_COEFF"), 64)
	if err != nil {
		oldScoreCoeff = 0.6
	} else {
		oldScoreCoeff = float32(Coeff)
	}
	fmt.Printf("OLD_SCORE_COEFF = %d\n", oldScoreCoeff)

	MaxChannelsToShow, err := strconv.Atoi(os.Getenv("NUM_CHANNEL_TO_SHOW"))
	if err != nil {
		maxNumChannels = 20
	} else {
		maxNumChannels = MaxChannelsToShow
	}
	fmt.Printf("NUM_CHANNEL_TO_SHOW = %d\n", maxNumChannels)

	fmt.Printf("Update the stats every %d seconds\n", UpdateInterval)
	update()
	ticker := time.NewTicker(time.Duration(UpdateInterval) * time.Second)
	go func() {
		for range ticker.C {
			update()
		}
	}()
}
