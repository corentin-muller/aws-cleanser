package cmd

import (
	"fmt"
	"time"

	"github.com/rebuy-de/aws-nuke/v2/resources"
)

type ItemState int

// States of Items based on the latest request to AWS.
const (
	ItemStateNew ItemState = iota
	ItemStatePending
	ItemStateWaiting
	ItemStateFailed
	ItemStateFiltered
	ItemStateFinished
)

// An Item describes an actual AWS resource entity with the current state and
// some metadata.
type Item struct {
	Resource resources.Resource

	State  ItemState
	Reason string

	Region *Region
	Type   string
}

func (i *Item) Print() {
	switch i.State {
	case ItemStateNew:
		currentDate := time.Now()
		creationdate, err := i.GetProperty("CreationDate")

		if err != nil {
			ageMessage := "would remove - is older than 30 days"
			Log(i.Region, i.Type, i.Resource, ReasonWaitPending, ageMessage)
		} else {
			creationDate, err1 := parseTime(creationdate)
			fmt.Println(err1)
			daysDifference := currentDate.Sub(creationDate).Hours() / 24
			var ageMessage string
			// Check if the date is older than 30 days
			if daysDifference > 30 {
				ageMessage = "would remove - is older than 30 days"
			} else {
				ageMessage = "would remove - is younger than 30 days"
			}
			Log(i.Region, i.Type, i.Resource, ReasonWaitPending, ageMessage)
		}
	case ItemStatePending:
		Log(i.Region, i.Type, i.Resource, ReasonWaitPending, "triggered remove")
	case ItemStateWaiting:
		Log(i.Region, i.Type, i.Resource, ReasonWaitPending, "waiting")
	case ItemStateFailed:
		Log(i.Region, i.Type, i.Resource, ReasonError, "failed")
	case ItemStateFiltered:
		Log(i.Region, i.Type, i.Resource, ReasonSkip, i.Reason)
	case ItemStateFinished:
		Log(i.Region, i.Type, i.Resource, ReasonSuccess, "removed")
	}
}

func parseTime(input interface{}) (time.Time, error) {
	if t, ok := input.(time.Time); ok {
		// If the input is already a time.Time, return it.
		return t, nil
	}

	// If the input is not a time.Time, try to parse it as a string.
	strInput, ok := input.(string)
	if !ok {
		return time.Time{}, fmt.Errorf("Input is not a time.Time or string")
	}

	layout := time.RFC3339
	parsedTime, err := time.Parse(layout, strInput)
	if err != nil {
		return time.Time{}, err
	}

	return parsedTime, nil
}

// List gets all resource items of the same resource type like the Item.
func (i *Item) List() ([]resources.Resource, error) {
	lister := resources.GetLister(i.Type)
	sess, err := i.Region.Session(i.Type)
	if err != nil {
		return nil, err
	}
	return lister(sess)
}

func (i *Item) GetProperty(key string) (string, error) {
	if key == "" {
		stringer, ok := i.Resource.(resources.LegacyStringer)
		if !ok {
			return "", fmt.Errorf("%T does not support legacy IDs", i.Resource)
		}
		return stringer.String(), nil
	}

	getter, ok := i.Resource.(resources.ResourcePropertyGetter)
	if !ok {
		return "", fmt.Errorf("%T does not support custom properties", i.Resource)
	}

	return getter.Properties().Get(key), nil
}

func (i *Item) Equals(o resources.Resource) bool {
	iType := fmt.Sprintf("%T", i.Resource)
	oType := fmt.Sprintf("%T", o)
	if iType != oType {
		return false
	}

	iStringer, iOK := i.Resource.(resources.LegacyStringer)
	oStringer, oOK := o.(resources.LegacyStringer)
	if iOK != oOK {
		return false
	}
	if iOK && oOK {
		return iStringer.String() == oStringer.String()
	}

	iGetter, iOK := i.Resource.(resources.ResourcePropertyGetter)
	oGetter, oOK := o.(resources.ResourcePropertyGetter)
	if iOK != oOK {
		return false
	}
	if iOK && oOK {
		return iGetter.Properties().Equals(oGetter.Properties())
	}

	return false
}

type Queue []*Item

func (q Queue) CountTotal() int {
	return len(q)
}

func (q Queue) Count(states ...ItemState) int {
	count := 0
	for _, item := range q {
		for _, state := range states {
			if item.State == state {
				count = count + 1
				break
			}
		}
	}
	return count
}
