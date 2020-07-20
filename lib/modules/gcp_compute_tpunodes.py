"""Delete GCP Compute TPU Nodes."""
import os
import json
import subprocess
from subprocess import PIPE
import googleapiclient.discovery
import google.auth
from ..BaseResource import BaseResource


class Resource(BaseResource):
    """Base Resource Class."""
    name = 'gcp_compute_tpunodes'
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
        self.get_zones()


    def get_zones(self):
        """Get zones for project."""
        try:
            request = self.client.zones().list(project=self.project)# pylint: disable=maybe-no-member
            response = request.execute()
            for zone in response['items']:
                self.zones.append(zone['name'])
            print('Found zones: {z}'.format(
                z=','.join(self.zones)))

        except Exception as err: # pylint: disable=broad-except
            print(err)


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
        for zone in self.zones:
            cmd = [
                "gcloud", "compute", "tpus", "list", "--zone", zone,
                "--project", self.project, "--format", "json", "--quiet"]
            print(' '.join(cmd))
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
                continue

            for tpu in data:
                tags = []
                found_name = False
                if 'labels' in tpu and tpu['labels']:
                    for label in tpu['labels']:
                        tags.append({
                            "Key": label,
                            "Value": tpu['labels'][label]
                        })
                        if label == 'name':
                            found_name = True
                if not found_name:
                    tags.append({
                        "Key": "name",
                        "Value": tpu['name']
                    })
                self.resources.append({
                    "Id": tpu['name'],
                    "Tags": tags,
                    "Zone": zone
                })
                self.ids.append(tpu['name'])
        return self.ids


    def list_resources(self):
        """List Resources."""
        self.get_resources()


    def delete_resources(self, resources, options=None):
        """ delete resources specified by ids list"""
        print(options)
        for instance in resources:
            cmd = [
                "gcloud", "compute", "tpus", "delete", "--zone", instance['Zone'],
                "--project", self.project, "--format", "json", instance['Id'], "--quiet"]
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
