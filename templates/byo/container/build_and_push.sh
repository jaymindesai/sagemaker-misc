#!/bin/zsh

# This script builds the Docker image and pushes it to ECR to be ready for use by SageMaker

# The argument to this script is the directory containing the model files inside models/ directory to be packages inside
# the container. The same will also be used as the image name and will be combined with the account and region to form
# the repository name for ECR
model_files_dir=$1

if [ -z "${model_files_dir}" ]
then
    echo "Usage: $0 <model-files-directory>"
    exit 1
fi

image=${model_files_dir}

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)

if [ $? -ne 0 ]
then
    exit 255
fi

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

full_image_name="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

# If the repository doesn't exist in ECR, create it
aws ecr describe-repositories --repository-names "${image}" --region "${region}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${image}" --region "${region}" > /dev/null
fi

# Get the login command from ECR and execute it directly
aws ecr get-login-password --region "${region}" | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com

# Temporarily copy model files to working directory
byo_root_dir=$0:P:h:h
cp -r "${byo_root_dir}/models/${model_files_dir}" "./${model_files_dir}"

# Build the docker image locally with the image name
docker build -t "${image}" --build-arg model_files_dir="${model_files_dir}" .

# Push the image to ECR with the full name
#docker tag "${image}" "${full_image_name}"
#docker push "${full_image_name}"

# Remove temp files
rm -rf "./${model_files_dir}"