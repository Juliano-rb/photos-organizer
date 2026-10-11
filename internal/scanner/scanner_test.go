package scanner

import (
	"os"
	"path/filepath"
	"slices"
	"testing"
)

func TestScanDirectory(t *testing.T) {
	t.Run("should recursively find all supported image extensions", func(t *testing.T) {
		tempDir := t.TempDir()

		// Criar estrutura de pastas:
		// tempDir/
		// ├── photo1.jpg
		// ├── PHOTO2.PNG (maiúscula para testar case-insensitivity)
		// ├── document.txt (não suportado)
		// └── sub/
		//     ├── photo3.webp
		//     ├── notes.pdf (não suportado)
		//     └── deep/
		//         ├── photo4.dng
		//         └── photo5.heic

		filesToCreate := []string{
			"photo1.jpg",
			"PHOTO2.PNG",
			"document.txt",
			filepath.Join("sub", "photo3.webp"),
			filepath.Join("sub", "notes.pdf"),
			filepath.Join("sub", "deep", "photo4.dng"),
			filepath.Join("sub", "deep", "photo5.heic"),
		}

		for _, relPath := range filesToCreate {
			fullPath := filepath.Join(tempDir, relPath)
			if err := os.MkdirAll(filepath.Dir(fullPath), 0755); err != nil {
				t.Fatalf("failed to create directory: %v", err)
			}
			if err := os.WriteFile(fullPath, []byte("fake image data"), 0644); err != nil {
				t.Fatalf("failed to create file %s: %v", fullPath, err)
			}
		}

		expectedFiles := []string{
			filepath.Join(tempDir, "photo1.jpg"),
			filepath.Join(tempDir, "PHOTO2.PNG"),
			filepath.Join(tempDir, "sub", "photo3.webp"),
			filepath.Join(tempDir, "sub", "deep", "photo4.dng"),
			filepath.Join(tempDir, "sub", "deep", "photo5.heic"),
		}

		results, err := ScanDirectory(tempDir)
		if err != nil {
			t.Fatalf("ScanDirectory() returned unexpected error: %v", err)
		}

		if len(results) != len(expectedFiles) {
			t.Fatalf("ScanDirectory() returned %d files, expected %d. Got: %v", len(results), len(expectedFiles), results)
		}

		// Ordenar ambos para comparação determinística
		slices.Sort(results)
		slices.Sort(expectedFiles)

		for i := range expectedFiles {
			if results[i] != expectedFiles[i] {
				t.Errorf("at index %d: expected %s, got %s", i, expectedFiles[i], results[i])
			}
		}
	})

	t.Run("should return error when directory does not exist", func(t *testing.T) {
		nonExistentPath := filepath.Join(t.TempDir(), "does_not_exist")
		_, err := ScanDirectory(nonExistentPath)
		if err == nil {
			t.Errorf("ScanDirectory() expected error for non-existent path, got nil")
		}
	})

	t.Run("should return error when path is a file, not a directory", func(t *testing.T) {
		tempDir := t.TempDir()
		filePath := filepath.Join(tempDir, "some_file.txt")
		if err := os.WriteFile(filePath, []byte("hello"), 0644); err != nil {
			t.Fatalf("failed to create test file: %v", err)
		}

		_, err := ScanDirectory(filePath)
		if err == nil {
			t.Errorf("ScanDirectory() expected error when root is a file, got nil")
		}
	})
}
