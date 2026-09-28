package domain

import (
	"os"
	"time"
)

type ExifData struct {
	DateTimeOriginal time.Time `json:"date_time_original" db:"date_time_original"`
	CameraMake       string    `json:"camera_make" db:"camera_make"`
	CameraModel      string    `json:"camera_model" db:"camera_model"`
	Latitude         *float64  `json:"latitude" db:"latitude"` // Ponteiros para representar valores anuláveis no BD
	Longitude        *float64  `json:"longitude" db:"longitude"`
}

type TagScore struct {
	Tag   string  `json:"tag" db:"tag"`
	Score float64 `json:"score" db:"score"`
}

type FileItem struct {
	ID              string        `json:"id" db:"id"`
	FileHash        string        `json:"file_hash" db:"file_hash"`
	SourcePath      string        `json:"source_path" db:"source_path"`
	DestinationPath string        `json:"destination_path" db:"destination_path"`
	Status          ProcessStatus `json:"status" db:"status"`

	Exif ExifData   `json:"exif" db:"-"`
	Tags []TagScore `json:"tags" db:"-"`
}

func (f *FileItem) IsUtility() bool {
	utilityTags := map[string]bool{
		"screenshot": true,
		"document":   true,
		"meme":       true,
		"receipt":    true,
	}

	for _, t := range f.Tags {
		if utilityTags[t.Tag] && t.Score >= 0.60 {
			return true
		}
	}
	return false
}

func (f *FileItem) ValidatePath() error {
	_, err := os.Stat(f.SourcePath)
	return err
}
