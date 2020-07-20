"""Delete GCP FileStore."""
import os
import json
import subprocess
from subprocess import PIPE
import googleapiclient.discovery
import google.auth
from ..BaseResource import BaseResource


class Resource(BaseResource):
    """Base Resource Class."""
    name = 'gcp_filestore'
    type = 'gcp'
    client = None
    credentials = None
    project = None
    dry_run = True
    ids = []
    resources = []
    zones = []


    def __init__(self, project=None):
        print('Try to process {p}'.format(
            p=self.name))
        self.project = project
        scopes = ['https://www.googleapis.com/auth/compute']
        credentials, _ = google.auth.default(scopes=scopes)
        self.client = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)


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
            "gcloud", "filestore", "instances", "list",
            "--project", self.project, "--format", "json",
            "--quiet"]
        data = {}
        try:
            process = subprocess.run(
                cmd,
                check=True,
                stdout=PIPE,
                stderr=PIPE
                )
            data = json.loads(process.stdout.decode('utf-8'))
        except Exception as err:# pylint: disable=broad-except
            search = 'has not been used in project'
            if search in str(err.stderr):# pylint: disable=maybe-no-member
                print('API has not been used before, skipping')
            else:
                print(err.stderr)# pylint: disable=maybe-no-member
            return self.ids
        for filestore in data:
            tags = []
            found_name = False
            if 'labels' in filestore:
                for label in filestore['labels']:
                    tags.append({
                        "Key": label,
                        "Value": filestore['labels'][label]
                    })
                    if label == 'name':
                        found_name = True

                if not found_name:
                    tags.append({
                        "Key": "name",
                        "Value": filestore['name']
                    })

            self.resources.append({
                "Id": filestore['name'],
                "Tags": tags
            })

            self.ids.append(filestore['name'])
        return self.ids


    def list_resources(self):
        """List Resources."""
        self.get_resources()


    def delete_resources(self, resources, options=None):
        """ delete resources specified by ids list"""
        print(options)
        for instance in resources:
            cmd = [
                "gcloud", "filestore", "instances", "delete", instance['Id'],
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
