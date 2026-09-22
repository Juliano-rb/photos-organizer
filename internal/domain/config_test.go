package domain_test

import (
	"testing"

	"photos-organizer/internal/domain"
)

func TestConfig_Validate(t *testing.T) {
	tests := []struct {
		name    string
		config  domain.Config
		wantErr bool
	}{
		{
			name: "Configuração válida (copy)",
			config: domain.Config{
				SourceDir:            "/origem",
				DestDir:              "/destino",
				Mode:                 domain.ModeCopy,
				GroupUtilitiesByDate: true,
			},
			wantErr: false,
		},
		{
			name: "Falta diretório de origem",
			config: domain.Config{
				SourceDir: "",
				DestDir:   "/destino",
				Mode:      domain.ModeMove,
			},
			wantErr: true,
		},
		{
			name: "Modo de operação inválido",
			config: domain.Config{
				SourceDir: "/origem",
				DestDir:   "/destino",
				Mode:      "delete", // Inválido
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()

			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
