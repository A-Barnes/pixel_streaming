#!/usr/bin/env bash

set -aeuxo pipefail

main() {
    
    Parameters="Environment=${Environment} PixelStreamingAMIID=${PixelStreamingAMIID}"

    zip -r deploy_asg_hook.zip ../code/pixel_streaming_asg_hook.py
    zip -r deploy_check_unused.zip ../code/pixel_streaming_check_unused.py
    zip -r deploy_get_streaming.zip ../code/pixel_streaming_get_streaming.py
    zip -r deploy_make_available.zip ../code/pixel_streaming_make_available.py 


    #Build the CloudFormation template¬
    aws cloudformation --region ap-southeast-2 package --template-file cfn.yml \
    --output-template-file cfn_packaged.yml \
    --s3-bucket ${S3_BUCKET} \
    --s3-prefix pixel-streaming


    aws cloudformation --region ap-southeast-2 deploy --template-file cfn_packaged.yml \
      --stack-name PixelStreaming \
      --capabilities CAPABILITY_IAM \
      --parameter-override $Parameters #\
      #--no-fail-no-empty-changeset
}

Environment=${1:?Specify an environment for argument 1}
S3_BUCKET=${2:?Specify an S3 Bucket for argument 2}
PixelStreamingAMIID=${3:?Specify an AMI ID for argument 3}

main "$@"
#
#¬
#  #Build the CloudFormation template¬
#  aws cloudformation package --template-file sftp.yml \¬
#    --output-template-file sftp_packaged.yml \¬
#    --s3-bucket idp-api-code-${Environment} \¬
#    --s3-prefix sftp¬
#¬
#  #If a third parameter is not supplied, also deploy the application¬
#  #The third param can be considered to be 'Build only' flag¬
#  #this is used by ansible only¬
#  if [[ -z $3 ]];¬
#  then¬
#    aws cloudformation deploy --template-file sftp_packaged.yml \¬
#      --stack-name SFTP-${ClientId} \¬
#      --capabilities CAPABILITY_IAM \¬
#      --parameter-override $Parameters \¬
#      --no-fail-on-empty-changeset¬
#  fi ¬
#} ¬
#¬
#Environment=${1:?Specify an environment for argument 1}¬
#ClientId=${2:?Specify the name of the client for argument 2}¬
#Parameters="Environment=${Environment} ClientId=${ClientId}"¬
#¬
#main "$@"¬
