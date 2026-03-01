package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestLocalIdentityToken(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.GET("/api/identity/token", localIdentityToken())

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/identity/token", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("expected status 200, got %d", w.Code)
	}

	var body map[string]interface{}
	if err := json.NewDecoder(w.Body).Decode(&body); err != nil {
		t.Fatalf("decode json: %v", err)
	}
	if _, ok := body["virtualId"]; !ok {
		t.Error("response missing virtualId")
	}
	if _, ok := body["expiresAtMs"]; !ok {
		t.Error("response missing expiresAtMs")
	}
}
