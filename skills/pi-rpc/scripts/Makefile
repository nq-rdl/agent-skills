.PHONY: build build-cli test lint generate serve clean cross-compile

SERVER_BIN := bin/pi-server
CLI_BIN    := bin/pi-cli
SERVER_PKG := ./cmd/pi-server/
CLI_PKG    := ./cmd/pi-cli/
PORT       ?= 4097

DESTDIR ?= bin

LDFLAGS := -X main.version=$(shell git describe --tags --always --dirty 2>/dev/null || echo dev) \
           -X main.commit=$(shell git rev-parse --short HEAD 2>/dev/null || echo none)

TARGETS := \
	linux/amd64 \
	linux/arm64 \
	darwin/amd64 \
	darwin/arm64

build: build-server build-cli

build-server:
	CGO_ENABLED=0 go build -ldflags "$(LDFLAGS)" -o $(SERVER_BIN) $(SERVER_PKG)

build-cli:
	CGO_ENABLED=0 go build -ldflags "$(LDFLAGS)" -o $(CLI_BIN) $(CLI_PKG)

# cross-compile builds the pi-server binary for all target platforms.
# Output: $(DESTDIR)/pi-server-<os>-<arch>
# Usage:  make cross-compile DESTDIR=/path/to/out
cross-compile:
	@mkdir -p $(DESTDIR)
	$(foreach target,$(TARGETS), \
		$(eval GOOS=$(word 1,$(subst /, ,$(target)))) \
		$(eval GOARCH=$(word 2,$(subst /, ,$(target)))) \
		CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) go build \
			-trimpath -ldflags "$(LDFLAGS)" \
			-o $(DESTDIR)/pi-server-$(GOOS)-$(GOARCH) \
			$(SERVER_PKG);)

test:
	go test -race ./...

lint:
	go vet ./...

generate:
	buf generate

serve: build-server
	PI_SERVER_PORT=$(PORT) ./$(SERVER_BIN)

clean:
	rm -rf bin/
