# Cloud-Reset

Deletes resources from a Cloud provider account.
Resources to be deleted are specified in a YAML file, like

```
- aws_ec2:
- aws_s3:
    exclude:
        - Name: /-terraform-/ # regular expression
        - Name: /-xxx-/
    options:
        force: true           # deletes bucket contents
- aws_kms:
```

## Getting Started

Clone the repo
```
git clone git@github.com:siran/cloud-reset.git
```

### Prerequisites

Install dependencies (virtual environment recommended)
```
pip3 install -r requirements.txt
```

### Installing

After cloning the repo and installing dependencies there is nothing else to do.


## Running the tests

No tests yet.


## Built With

* Boto3

### GCP

  1. Create a service account dedicated to this process which only has access to projects you want to "reset"
  2. Export path to Service Account credentials: export GOOGLE_APPLICATION_CREDENTIALS=myserviceaccountcredentals.json
  3. Install gcloud CLI if needed for your desired services. Currently, this is needed for GCP SQL Instances, GCP FileStore, and GCP Compute TPU Nodes
  4. Specify Project ID when running instead of boto3 profile: python3 delete_resources.py -f gcp_resources.yml --gcp_project ${ProjectId} 

#### GCP Supported Resources

 - gcp_compute_disks
 - gcp_compute_images
 - gcp_compute_instancegroups
 - gcp_compute_instances
 - gcp_compute_instancetemplates
 - gcp_compute_nodegroups
 - gcp_compute_nodetemplates
 - gcp_compute_snapshots
 - gcp_compute_tpunodes
 - gcp_filestore
 - gcp_gke_clusters
 - gcp_sql_instances

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Similar project

Some similar projects:

- cloud-sweeper: https://github.com/getify/cloud-sweeper
- cloud-nuke: https://github.com/getify/cloud-sweeper
- aws-auto-cleanup: https://github.com/servian/aws-auto-cleanup
- gcloud-cleanup: https://github.com/travis-ci/gcloud-cleanup

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to Shashi
* Thanks to Annalect for giving me the need to develop this tool

