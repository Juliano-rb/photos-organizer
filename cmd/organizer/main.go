package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	var (
		sourceDir string
		destDir   string
		mode      string
		port      int
		dryRun    bool
		noBrowser bool
	)

	// defines default value of sourceDir as current working directory
	currentDir, err := os.Getwd()
	if err != nil {
		currentDir = "."
	}

	flag.StringVar(&sourceDir, "source", currentDir, "Diretório de origem das fotos a serem organizadas")
	flag.StringVar(&destDir, "dest", "", "Diretório de destino das fotos organizadas")
	flag.StringVar(&mode, "mode", "copy", "Modo de operação: 'copy' (padrão) ou 'move'")
	flag.IntVar(&port, "port", 8080, "Porta inicial para o servidor Web local")
	flag.BoolVar(&dryRun, "dry-run", false, "Executa em modo simulação sem alterar arquivos em disco")
	flag.BoolVar(&noBrowser, "no-browser", false, "Inicia o servidor sem abrir o navegador automaticamente")

	flag.Parse()

	fmt.Println("==========================================")
	fmt.Println("       PhotoOrganizer - Inicializado      ")
	fmt.Println("==========================================")
	fmt.Printf("Origem:      %s\n", sourceDir)
	fmt.Printf("Destino:     %s\n", destDir)
	fmt.Printf("Modo:        %s\n", mode)
	fmt.Printf("Porta:       %d\n", port)
	fmt.Printf("Dry Run:     %t\n", dryRun)
	fmt.Printf("Sem Browser: %t\n", noBrowser)
	fmt.Println("==========================================")
}
