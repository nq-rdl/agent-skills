// Package prompt generates the <available_skills> XML block for agent system prompts.
package prompt

import (
	"fmt"
	"html"
	"strings"

	"github.com/nq-rdl/agent-skills/tools/asctl/internal/parser"
)

// ToPrompt generates the <available_skills> XML block.
// Output format is byte-for-byte equivalent to the Python prompt.to_prompt() function.
func ToPrompt(skillDirs []string) (string, error) {
	if len(skillDirs) == 0 {
		return "<available_skills>\n</available_skills>", nil
	}

	lines := []string{"<available_skills>"}

	for _, dir := range skillDirs {
		props, err := parser.ReadProperties(dir)
		if err != nil {
			return "", fmt.Errorf("skill %s: %w", dir, err)
		}

		skillMD := parser.FindSkillMD(dir)

		lines = append(lines,
			"<skill>",
			"<name>",
			html.EscapeString(props.Name),
			"</name>",
			"<description>",
			html.EscapeString(props.Description),
			"</description>",
			"<location>",
			skillMD,
			"</location>",
			"</skill>",
		)
	}

	lines = append(lines, "</available_skills>")
	return strings.Join(lines, "\n"), nil
}
