package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"

	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/gen/pirpc/v1/pirpcv1connect"
	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/handler"
	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/session"
)

func autoDetectProvider() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return "openai"
	}

	authFile := filepath.Join(home, ".pi", "agent", "auth.json")
	data, err := os.ReadFile(authFile)
	if err != nil {
		return "openai"
	}

	var authData map[string]interface{}
	if err := json.Unmarshal(data, &authData); err != nil {
		return "openai"
	}

	if _, ok := authData["openai-codex"]; ok {
		return "openai-codex"
	}

	return "openai"
}

func main() {
	port := os.Getenv("PI_SERVER_PORT")
	if port == "" {
		port = "4097"
	}

	defaultProvider := os.Getenv("PI_DEFAULT_PROVIDER")
	if defaultProvider == "" {
		defaultProvider = autoDetectProvider()
	}
	defaultModel := os.Getenv("PI_DEFAULT_MODEL")
	if defaultModel == "" {
		defaultModel = "gpt-4.1"
	}

	mgr := session.NewManager("pi")
	h := handler.NewSessionHandler(mgr, handler.Defaults{
		Provider: defaultProvider,
		Model:    defaultModel,
	})

	mux := http.NewServeMux()
	path, svcHandler := pirpcv1connect.NewSessionServiceHandler(h)
	mux.Handle(path, svcHandler)

	addr := fmt.Sprintf(":%s", port)
	srv := &http.Server{Addr: addr, Handler: mux}

	// Graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGTERM, syscall.SIGINT)

	go func() {
		<-sigCh
		log.Println("shutting down — terminating all sessions")
		mgr.GracefulShutdown()
		srv.Close()
	}()

	log.Printf("pi-server listening on %s", addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server error: %v", err)
	}
}
