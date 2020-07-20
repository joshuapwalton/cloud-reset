"""Delete GCP Compute Node Templates."""
import googleapiclient.discovery
import google.auth
from ..BaseResource import BaseResource


class Resource(BaseResource):
    """Base Resource Class."""
    name = 'gcp_compute_nodetemplates'
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
        scopes = ['https://www.googleapis.com/auth/compute']
        credentials, _ = google.auth.default(scopes=scopes)
        self.client = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
        self.get_regions()


    def get_regions(self):
        """Get zones for project."""
        try:
            request = self.client.regions().list(project=self.project)# pylint: disable=maybe-no-member
            response = request.execute()
            for zone in response['items']:
                self.zones.append(zone['name'])
            print('Found zones: {z}'.format(
                z=','.join(self.zones)))

        except Exception as err: # pylint: disable=broad-except
            print(err)


    def get_resources(self):
        """Get resources for gcp_compute."""
        client = self.client
        for zone in self.zones:
            request = client.nodeTemplates().list(project=self.project, region=zone)# pylint: disable=maybe-no-member
            while request is not None:
                response = request.execute()
                if 'items' in response and response['items']:
                    for instance in response['items']:
                        tags = []
                        self.ids.append(instance['id'])
                        tags.append({
                            "Key": "name",
                            "Value": instance['name']
                        })


                        self.resources.append({
                            "Id": instance['id'],
                            "Zone": zone,
                            "Tags": tags
                        })

                request = client.instances().list_next(# pylint: disable=maybe-no-member
                    previous_request=request, previous_response=response)
        return self.ids


    def list_resources(self):
        """List Resources."""
        self.get_resources()


    def delete_resources(self, resources, options=None):
        """ delete resources specified by ids list"""
        print(options)
        client = self.client
        if self.dry_run:
            print('dry_run flag set, Skip deleting')
            return True
        for resource in resources:
            try:
                response = client.nodeTemplates().delete(# pylint: disable=maybe-no-member
                    project=self.project,
                    region=resource['Zone'],
                    nodeTemplate=resource['Id']
                ).execute()
                print(response)
            except Exception as error:# pylint: disable=broad-except
                print(error)
        return True
