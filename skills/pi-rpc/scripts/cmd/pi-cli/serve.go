package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/spf13/cobra"

	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/gen/pirpc/v1/pirpcv1connect"
	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/handler"
	"github.com/nq-rdl/agent-skills/skills/pi-rpc/scripts/session"
)

func newServeCmd() *cobra.Command {
	var (
		port   string
		binary string
	)

	cmd := &cobra.Command{
		Use:   "serve",
		Short: "Start the pi-server ConnectRPC service",
		Long: `Start the pi-server ConnectRPC service that manages pi.dev sessions.

The server listens for HTTP/JSON requests and spawns pi.dev subprocesses
on demand. Agents communicate with it via the session subcommands.

Environment variables:
  PI_SERVER_PORT   Override the listening port (default: 4097)
  PI_BINARY        Path to the pi binary (default: pi)`,
		RunE: func(cmd *cobra.Command, args []string) error {
			return runServe(port, binary)
		},
	}

	cmd.Flags().StringVar(&port, "port", "", "Listening port (overrides PI_SERVER_PORT, default: 4097)")
	cmd.Flags().StringVar(&binary, "binary", "", "Path to pi binary (overrides PI_BINARY, default: pi)")

	return cmd
}

func runServe(portFlag, binaryFlag string) error {
	port := portFlag
	if port == "" {
		port = os.Getenv("PI_SERVER_PORT")
	}
	if port == "" {
		port = "4097"
	}

	binary := binaryFlag
	if binary == "" {
		binary = os.Getenv("PI_BINARY")
	}
	if binary == "" {
		binary = "pi"
	}

	mgr := session.NewManager(binary)

	mux := http.NewServeMux()
	path, svcHandler := pirpcv1connect.NewSessionServiceHandler(handler.NewSessionHandler(mgr))
	mux.Handle(path, svcHandler)

	addr := fmt.Sprintf(":%s", port)
	srv := &http.Server{Addr: addr, Handler: mux}

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
		return fmt.Errorf("server error: %w", err)
	}
	return nil
}
