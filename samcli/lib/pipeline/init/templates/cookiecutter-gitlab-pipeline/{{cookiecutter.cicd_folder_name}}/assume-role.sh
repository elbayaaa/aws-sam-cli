REGION=$1
ROLE=$2
SESSION_NAME=$3


cred=$(aws sts assume-role \
           --role-arn $ROLE \
           --role-session-name $SESSION_NAME)

export AWS_DEFAULT_REGION=$REGION
export AWS_ACCESS_KEY_ID=$(echo "${cred}" | jq ".Credentials.AccessKeyId" --raw-output)
export AWS_SECRET_ACCESS_KEY=$(echo "${cred}" | jq ".Credentials.SecretAccessKey" --raw-output)
export AWS_SESSION_TOKEN=$(echo "${cred}" | jq ".Credentials.SessionToken" --raw-output)
