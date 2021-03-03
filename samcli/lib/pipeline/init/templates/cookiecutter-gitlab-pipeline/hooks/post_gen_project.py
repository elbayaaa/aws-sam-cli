import os

# move ".gitlab-ci.yml" to the root of the project
os.rename("./.gitlab-ci.yml", "../.gitlab-ci.yml")