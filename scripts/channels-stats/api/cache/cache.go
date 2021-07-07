package cache

import "sync"

type SyncVar struct {
	mutex *sync.RWMutex
	val   interface{}
}

func NewSyncVar(v interface{}) *SyncVar {
	return &SyncVar{&sync.RWMutex{}, v}
}

func (t *SyncVar) Set(v interface{}) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.val = v
}

func (t *SyncVar) Get() interface{} {
	t.mutex.RLock()
	defer t.mutex.RUnlock()
	return t.val
}

var response *SyncVar

func Response() *SyncVar {
	if response == nil {
		response = NewSyncVar([]byte{})
	}

	return response
}
