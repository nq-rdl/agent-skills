package frontmatter_test

import (
	"testing"

	"github.com/nq-rdl/agent-skills/tools/asctl/internal/frontmatter"
)

func TestParse_valid(t *testing.T) {
	content := `---
name: my-skill
description: Does something useful
license: MIT
---
# My Skill
`
	meta, body, err := frontmatter.Parse(content)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if meta["name"] != "my-skill" {
		t.Errorf("name = %q, want %q", meta["name"], "my-skill")
	}
	if meta["description"] != "Does something useful" {
		t.Errorf("description = %q, want %q", meta["description"], "Does something useful")
	}
	if body != "# My Skill" {
		t.Errorf("body = %q, want %q", body, "# My Skill")
	}
}

func TestParse_missingOpenDelimiter(t *testing.T) {
	_, _, err := frontmatter.Parse("name: foo\n---\nbody")
	if err == nil {
		t.Fatal("expected error for missing opening ---")
	}
}

func TestParse_unclosedDelimiter(t *testing.T) {
	_, _, err := frontmatter.Parse("---\nname: foo\n")
	if err == nil {
		t.Fatal("expected error for unclosed frontmatter")
	}
}

func TestParse_invalidYAML(t *testing.T) {
	_, _, err := frontmatter.Parse("---\n: invalid: yaml:\n---\n")
	if err == nil {
		t.Fatal("expected error for invalid YAML")
	}
}

func TestParse_metadataSubmap(t *testing.T) {
	content := "---\nname: x\ndescription: y\nmetadata:\n  repo: https://example.com\n  version: \"1\"\n---\n"
	meta, _, err := frontmatter.Parse(content)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	m, ok := meta["metadata"].(map[string]string)
	if !ok {
		t.Fatalf("metadata not normalized to map[string]string, got %T", meta["metadata"])
	}
	if m["repo"] != "https://example.com" {
		t.Errorf("repo = %q, want %q", m["repo"], "https://example.com")
	}
}
