package domain_test

import (
	"testing"

	"photos-organizer/internal/domain"
)

func TestProcessStatus_String(t *testing.T) {
	tests := []struct {
		name   string
		status domain.ProcessStatus
		want   string
	}{
		{
			name:   "Deve retornar Unprocessed",
			status: domain.StatusUnprocessed,
			want:   "Unprocessed",
		},
		{
			name:   "Deve retornar Completed",
			status: domain.StatusCompleted,
			want:   "Completed",
		},
		{
			name:   "Deve retornar Duplicate",
			status: domain.StatusDuplicate,
			want:   "Duplicate",
		},
		{
			name:   "Status desconhecido deve cair no default",
			status: domain.ProcessStatus(999),
			want:   "Unknown",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.status.String()
			if got != tt.want {
				t.Errorf("ProcessStatus.String() = %v, want %v", got, tt.want)
			}
		})
	}
}
