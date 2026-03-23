import json
import tempfile
from pathlib import Path

from backend.skills import registry


def test_parse_frontmatter():
    content = """---
name: Demo Skill
description: Test skill
---

# Body
"""

    metadata, body = registry._parse_frontmatter(content)

    assert metadata["name"] == "Demo Skill"
    assert metadata["description"] == "Test skill"
    assert "# Body" in body


def test_parse_tools_section():
    body = """
## Tools

### create_demo
Create a demo item.

**Script:** scripts/create_demo.py

**Parameters:**
- protocol (string, required): protocol name
- resource_name (string, optional): resource name
"""

    tools = registry._parse_tools_section(body)

    assert len(tools) == 1
    assert tools[0]["name"] == "create_demo"
    assert tools[0]["script"] == "scripts/create_demo.py"
    assert tools[0]["parameters"][0]["name"] == "protocol"
    assert tools[0]["parameters"][0]["required"] is True


def test_scan_skills_schema_and_call_skill():
    base_dir = Path(".test_tmp_runtime")
    base_dir.mkdir(exist_ok=True)
    tmp_path = Path(tempfile.mkdtemp(dir=base_dir))
    skill_dir = tmp_path / "demo-skill"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)

    (skill_dir / "SKILL.md").write_text(
        """---
name: Demo Skill
description: Test skill
---

## Tools

### create_demo
Create a demo item.

**Script:** scripts/create_demo.py

**Parameters:**
- protocol (string, required): protocol name
""",
        encoding="utf-8",
    )

    (scripts_dir / "create_demo.py").write_text(
        "import json, sys\n"
        "data = json.loads(sys.stdin.read())\n"
        'print(json.dumps({"ok": True, "protocol": data.get("protocol")}))\n',
        encoding="utf-8",
    )

    registry.scan_skills(str(tmp_path))
    tools = registry.get_tools_schema()
    result = registry.call_skill("create_demo", protocol="MQS")

    assert registry.list_skills() == ["create_demo"]
    assert tools[0]["function"]["name"] == "create_demo"
    assert tools[0]["function"]["parameters"]["required"] == ["protocol"]
    assert "Demo Skill" in registry.get_skills_context()
    assert result == {"ok": True, "protocol": "MQS"}
