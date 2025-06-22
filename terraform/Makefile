.PHONY: init all module modules plan destroy clean

init:
	terraform init

all:
	terraform apply -var-file=terraform.tfvars

infra: init destroy
	terraform apply

module:
	terraform apply -target=module.$(module) -var-file=./modules/$(module)/terraform.tfvars

plan:
	terraform plan -var-file=terraform.tfvars

destroy:
	terraform destroy -auto-approve

clean:
	rm -rf terraform.tfstate* .terraform .terraform.lock.hcl

terraform: infra
	terraform output alb_dns_name
