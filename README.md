# skills

Public repository for Agent Skills

```sh

# If ~/.claude Doesn't Exist

# Create it first:

mkdir -p ~/.claude


# If a skills Folder Already Exists There

# You must remove or rename it first:

rm -rf ~/.claude/skills



# (macOS / Linux / Windows WSL)
ln -sf ~/github/skills/skills ~/.claude/skills

# Windows (PowerShell Native, Not WSL)
# You may need to run PowerShell as Administrator unless Developer Mode is enabled
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills" -Target "$HOME\github\skills\skills"




```

## Skills Hub

- <https://skills.sh/>


