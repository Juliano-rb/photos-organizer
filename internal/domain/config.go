package domain

import "errors"

type OperationMode string

const (
	ModeCopy OperationMode = "copy"
	ModeMove OperationMode = "move"
)

type Config struct {
	SourceDir            string        `json:"source_dir"`
	DestDir              string        `json:"dest_dir"`
	Mode                 OperationMode `json:"mode"`
	GroupUtilitiesByDate bool          `json:"group_utilities_by_date"`
}

func (c *Config) Validate() error {
	if c.SourceDir == "" {
		return errors.New("o diretório de origem é obrigatório")
	}
	if c.DestDir == "" {
		return errors.New("o diretório de destino é obrigatório")
	}
	if c.Mode != ModeCopy && c.Mode != ModeMove {
		return errors.New("modo de operação deve ser 'copy' ou 'move'")
	}
	return nil
}
