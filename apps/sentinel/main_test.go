package main

import (
	"os"
	"testing"
)

func TestGetEnv(t *testing.T) {
	const key = "SENTINEL_TEST_ENV"
	const def = "default_value"

	if got := getEnv(key, def); got != def {
		t.Errorf("getEnv(%q, %q) = %q, want %q (unset)", key, def, got, def)
	}

	os.Setenv(key, "custom_value")
	defer os.Unsetenv(key)

	if got := getEnv(key, def); got != "custom_value" {
		t.Errorf("getEnv(%q, %q) = %q, want custom_value", key, def, got)
	}
}
