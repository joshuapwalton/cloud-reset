"""Delete GCP SQL Instances."""
import os
import json
import subprocess
from ..BaseResource import BaseResource


class Resource(BaseResource):
    """Base Resource Class."""
    name = 'gcp_sql_instances'
    type = 'gcp'
    client = None
    credentials = None
    project = None
    dry_run = True
    ids = []
    resources = []


    def __init__(self, project=None):
        print('Try to process {p}'.format(
            p=self.name))
        self.project = project


    def login_cli(self):
        """Python sdk does not support TPU's yet."""
        cmd = [
            "gcloud", "auth", "activate-service-account", "--key-file",
            os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            ]
        print("CMD: "+" ".join(cmd))
        try:
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                check=False)
        except Exception as err:# pylint: disable=broad-except
            print('Error logging in')
            print(str(err))
            print('end error')


    def get_resources(self):
        """Get resources for gcp_compute."""
        self.login_cli()
        cmd = [
            "gcloud", "sql", "instances", "list",
            "--project", self.project, "--format", "json", "--quiet"]
        print(' '.join(cmd))
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                check=False)
            data = json.loads(process.stdout.decode('utf-8'))
        except Exception as err:# pylint: disable=broad-except
            print(err)
        for instance in data:
            found_name = False
            tags = []
            if 'userLabels' in instance['settings'] and instance['settings']['userLabels']:
                for label in instance['settings']['userLabels']:
                    tags.append({
                        "Key": label,
                        "Value": instance['settings']['userLabels'][label]
                    })
                    if label == "name":
                        found_name = True

            if not found_name:
                tags.append({
                    "Key": "name",
                    "Value": instance['name']
                })
            self.resources.append({
                "Id": instance['name'],
                "Tags": tags
            })

            self.ids.append(instance['name'])
        return self.ids


    def list_resources(self):
        """List Resources."""
        self.get_resources()


    def delete_resources(self, resources, options=None):
        """ delete resources specified by ids list"""
        print(options)
        for instance in resources:
            cmd = [
                "gcloud", "sql", "instances", "delete", instance['Id'],
                "--project", self.project, "--format", "json", "--quiet"]
            print(' '.join(cmd))
            try:
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    check=False
                )
                print(process.stdout.decode('utf-8'))
            except Exception as err:# pylint: disable=broad-except
                print(err)
        return True
