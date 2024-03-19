echo *****************************************************************

echo $(date)
project_id=$(gcloud config get project)
echo $project_id

#terraform -chdir=terraform destroy -auto-approve -var project_id=$project_id
#terraform -chdir=terraform init
terraform -chdir=terraform apply -auto-approve -var project_id=$project_id


echo $(date)
echo *****************************************************************