has_resources = {{ cookiecutter.has_aws_resources }}
if has_resources:
    print("Yaaaaay, I have resources")
else:
    print("NOOOOO, I don't have resources")