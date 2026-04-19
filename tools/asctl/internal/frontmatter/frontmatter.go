// Package frontmatter parses YAML frontmatter from SKILL.md content.
package frontmatter

import (
	"fmt"
	"strings"

	"gopkg.in/yaml.v3"
)

// Parse extracts YAML frontmatter and body from SKILL.md content.
// Returns the metadata map, the markdown body, and any parse error.
func Parse(content string) (map[string]any, string, error) {
	if !strings.HasPrefix(content, "---") {
		return nil, "", fmt.Errorf("SKILL.md must start with YAML frontmatter (---)")
	}

	parts := strings.SplitN(content, "---", 3)
	if len(parts) < 3 {
		return nil, "", fmt.Errorf("SKILL.md frontmatter not properly closed with ---")
	}

	body := strings.TrimSpace(parts[2])

	var metadata map[string]any
	if err := yaml.Unmarshal([]byte(parts[1]), &metadata); err != nil {
		return nil, "", fmt.Errorf("invalid YAML in frontmatter: %w", err)
	}

	if metadata == nil {
		return nil, "", fmt.Errorf("SKILL.md frontmatter must be a YAML mapping")
	}

	// Normalize metadata sub-map values to string->string, mirroring Python behaviour.
	if meta, ok := metadata["metadata"].(map[string]any); ok {
		normalized := make(map[string]string, len(meta))
		for k, v := range meta {
			normalized[k] = fmt.Sprintf("%v", v)
		}
		metadata["metadata"] = normalized
	}

	return metadata, body, nil
}
