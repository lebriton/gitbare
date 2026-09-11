<p align="center">
  <img src="" alt="Logo" width="200" />
</p>

<h1 align="center">Project Template</h1>

<p align="center">
  <strong>Modern project foundation.</strong>
</p>

<p align="center">
  <i>A clean, production-ready template to kickstart new projects.</i>
</p>

<br>

# How to use this template

```bash
PROJECT_NAME="my-project"
# Find your technologies at https://www.toptal.com/developers/gitignore
TECHNOLOGIES="python,docker,go"

# Clone the repository (SSH)
git clone git@github.com:lebriton/project-template.git $PROJECT_NAME

# OR clone the repository (HTTPS)
git clone https://github.com/lebriton/project-template.git $PROJECT_NAME

# Enter the project directory
cd $PROJECT_NAME

# Rename the devpod to match the project name
sed -i "s/project-template/$PROJECT_NAME/g" .devcontainer/devcontainer.json Justfile

# Remove the existing git history
rm -rf .git

# Initialize a new git repository
git init -b main

# Install skills
# Find more at https://www.skills.sh/ and https://github.com/lebriton/skills
npx skills add https://github.com/lebriton/skills --skill bash-scripting -y
npx skills add https://github.com/github/awesome-copilot --skill conventional-commit -y
npx skills add https://github.com/casey/just --skill just -y
npx skills add https://github.com/lebriton/skills --skill justfile-conventions -y

# Generate the .gitignore file
wget https://www.toptal.com/developers/gitignore/api/$TECHNOLOGIES -O .gitignore
```

# Documentation

- [Foo](docs/foo.md)
- [Bar](docs/bar.md)
- [Baz](docs/baz.md)

<br>

<p align="center">
  <sub>Made with determination.</sub>
</p>
