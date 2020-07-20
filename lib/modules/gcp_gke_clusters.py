"""Delete GCP GKE Clusters."""
from google.cloud import container_v1
from ..BaseResource import BaseResource


class Resource(BaseResource):
    """Base Resource Class."""
    name = 'gcp_gke_clusters'
    type = 'gcp'
    client = None
    credentials = None
    zones = []
    project = None
    dry_run = True
    ids = []
    resources = []

    def __init__(self, project=None):
        print('Try to process {p}'.format(
            p=self.name))
        self.project = project
        self.gke = container_v1.ClusterManagerClient()


    def get_resources(self):
        """Get resources for gcp_compute."""
        client = self.gke
        parent = "projects/{p}/locations/-".format(p=self.project)
        request = client.list_clusters(parent=parent)
        if request and request.clusters:
            for cluster in request.clusters:
                found_name = False
                tags = []
                if cluster.resource_labels:
                    for label in cluster.resource_labels:
                        tags.append({
                            "Key": label,
                            "Value": cluster.resource_labels[label]
                        })
                        if label == "name":
                            found_name = True

                target = "projects/{p}/locations/{z}/clusters/{n}".format(
                    p=self.project, n=cluster.name, z=cluster.zone)
                if not found_name:
                    tags.append({
                        "Key": "name",
                        "Value": cluster.name
                    })
                self.resources.append({
                    "Id": target,
                    "Tags": tags
                })
                self.ids.append(target)
        return self.ids


    def list_resources(self):
        """List Resources."""
        self.get_resources()


    def delete_resources(self, resources, options=None):
        """ delete resources specified by ids list"""
        print(options)
        client = self.gke
        if self.dry_run:
            print('dry_run flag set, Skip deleting')
            return True
        for resource in resources:
            try:
                response = client.delete_cluster(
                    name=resource['Id']
                )
                print(response)
            except Exception as error:# pylint: disable=broad-except
                print(error)
        return True
