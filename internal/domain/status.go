package domain

type ProcessStatus int

const (
	StatusUnprocessed ProcessStatus = iota
	StatusProcessing
	StatusClassified
	StatusCompleted
	StatusError
	StatusDuplicate
)

func (c ProcessStatus) String() string {
	switch c {
	case StatusUnprocessed:
		return "Unprocessed"
	case StatusProcessing:
		return "Processing"
	case StatusClassified:
		return "Classified"
	case StatusCompleted:
		return "Completed"
	case StatusError:
		return "Error"
	case StatusDuplicate:
		return "Duplicate"
	default:
		return "Unknown"
	}
}
