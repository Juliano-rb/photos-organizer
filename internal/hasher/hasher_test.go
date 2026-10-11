package hasher

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCalculateSHA256(t *testing.T) {
	t.Run("calculates correct hash for known content", func(t *testing.T) {
		tempDir := t.TempDir()
		testFile := filepath.Join(tempDir, "sample.txt")
		content := []byte("hello world")

		if err := os.WriteFile(testFile, content, 0644); err != nil {
			t.Fatalf("failed to create sample file: %v", err)
		}

		expected := "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
		actual, err := CalculateSHA256(testFile)
		if err != nil {
			t.Fatalf("CalculateSHA256() returned unexpected error: %v", err)
		}

		if actual != expected {
			t.Errorf("CalculateSHA256() = %q; expected %q", actual, expected)
		}
	})

	t.Run("calculates correct hash for empty file", func(t *testing.T) {
		tempDir := t.TempDir()
		testFile := filepath.Join(tempDir, "empty.txt")

		if err := os.WriteFile(testFile, []byte{}, 0644); err != nil {
			t.Fatalf("failed to create empty file: %v", err)
		}

		expected := "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
		actual, err := CalculateSHA256(testFile)
		if err != nil {
			t.Fatalf("CalculateSHA256() returned unexpected error: %v", err)
		}

		if actual != expected {
			t.Errorf("CalculateSHA256() = %q; expected %q", actual, expected)
		}
	})

	t.Run("returns error for non-existent file", func(t *testing.T) {
		nonExistentFile := filepath.Join(t.TempDir(), "does_not_exist.jpg")
		_, err := CalculateSHA256(nonExistentFile)
		if err == nil {
			t.Errorf("CalculateSHA256() expected error for non-existent file, got nil")
		}
	})
}
