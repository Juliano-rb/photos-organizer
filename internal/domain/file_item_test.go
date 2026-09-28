package domain

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFileItem_IsUtility(t *testing.T) {
	tests := []struct {
		name     string
		tags     []TagScore
		expected bool
	}{
		{
			name: "No tags",
			tags: []TagScore{},
			expected: false,
		},
		{
			name: "Utility tag with low score",
			tags: []TagScore{
				{Tag: "screenshot", Score: 0.59},
			},
			expected: false,
		},
		{
			name: "Utility tag with high score",
			tags: []TagScore{
				{Tag: "screenshot", Score: 0.60},
			},
			expected: true,
		},
		{
			name: "Multiple tags with one high utility score",
			tags: []TagScore{
				{Tag: "beach", Score: 0.90},
				{Tag: "meme", Score: 0.85},
			},
			expected: true,
		},
		{
			name: "Non-utility tags only",
			tags: []TagScore{
				{Tag: "beach", Score: 0.90},
				{Tag: "family", Score: 0.85},
			},
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			item := &FileItem{
				Tags: tt.tags,
			}
			
			result := item.IsUtility()
			if result != tt.expected {
				t.Errorf("IsUtility() = %v, expected %v", result, tt.expected)
			}
		})
	}
}

func TestFileItem_ValidatePath(t *testing.T) {
	tempDir := t.TempDir()
	tempFile := filepath.Join(tempDir, "test.jpg")
	
	// Create a dummy file
	f, err := os.Create(tempFile)
	if err != nil {
		t.Fatalf("failed to create temp file: %v", err)
	}
	f.Close()

	t.Run("File exists", func(t *testing.T) {
		item := &FileItem{
			SourcePath: tempFile,
		}
		
		if err := item.ValidatePath(); err != nil {
			t.Errorf("ValidatePath() expected no error, got: %v", err)
		}
	})

	t.Run("File does not exist", func(t *testing.T) {
		item := &FileItem{
			SourcePath: filepath.Join(tempDir, "not_exist.jpg"),
		}
		
		if err := item.ValidatePath(); err == nil {
			t.Errorf("ValidatePath() expected error for non-existent file")
		}
	})
}
