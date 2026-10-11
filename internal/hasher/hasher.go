package hasher

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
)

func CalculateSHA256(filePath string) (string, error) {
	file, err := os.Open(filePath)

	if err != nil {
		return "", fmt.Errorf("failed to open file %q: %w", filePath, err)
	}

	defer file.Close()

	hasher := sha256.New()

	_, err = io.Copy(hasher, file)
	if err != nil {
		return "", fmt.Errorf("failed to compute hash for %q: %w", filePath, err)
	}

	hash := hasher.Sum(nil)
	return hex.EncodeToString(hash), nil
}
