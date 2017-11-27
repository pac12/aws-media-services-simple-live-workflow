"""
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from botocore.vendored import requests
import boto3
import json
import string
import random
import resource_tools


def event_handler(event, context):
    """
    Lambda entry point. Print the event first.
    """
    print("Event Input: %s" % json.dumps(event))
    try:
        medialive = boto3.client('medialive')
        if event["RequestType"] == "Create":
            result = create_input(medialive, event, context)
        elif event["RequestType"] == "Update":
            result = update_input(medialive, event, context)
        elif event["RequestType"] == "Delete":
            result = delete_input(medialive, event, context)
    except Exception as exp:
        print("Exception: %s" % exp)
        result = {
            'Status': 'FAILED',
            'Data': {"Exception": str(exp)},
            'ResourceId': None
        }
    resource_tools.send(event, context, result['Status'],
                        result['Data'], result['ResourceId'])
    return


def create_input(medialive, event, context, auto_id=True):
    """
    Create a MediaLive input
    """

    input_uniq = resource_tools.id_generator()

    if auto_id:
        input_id = "%s-%s-%s" % (resource_tools.stack_name(
            event['StackId']), event["LogicalResourceId"], input_uniq)
    else:
        input_id = event["PhysicalResourceId"]

    try:
        response = medialive.create_input(
            Name=input_id,
            Type='URL_PULL',
            Sources=[
                {'Url': event["ResourceProperties"]["HLSPrimarySource"]},
                {'Url': event["ResourceProperties"]["HLSSecondarySource"]}
            ]
        )

        print(json.dumps(response))

        result = {
            'Status': 'SUCCESS',
            'Data': response,
            'ResourceId': response['Input']['Id']
        }

    except Exception as ex:
        print(ex)
        result = {
            'Status': 'FAILED',
            'Data': {"Exception": str(ex)},
            'ResourceId': response['Input']['Id']
        }

    return result


def update_input(medialive, event, context):
    """
    Update a MediaPackage channel
    Return the channel URL, username and password generated by MediaPackage
    """

    channel_id = event["PhysicalResourceId"]

    try:
        result = delete_input(medialive, event, context)
        if result['Status'] == 'SUCCESS':
            result = create_input(medialive, event, context, False)

    except Exception as ex:
        print(ex)
        result = {
            'Status': 'FAILED',
            'Data': {"Exception": str(ex)},
            'ResourceId': channel_id
        }

    return result


def delete_input(medialive, event, context):
    """
    Delete a MediaLive input source
    Return success/failure
    """

    input_id = event["PhysicalResourceId"]

    try:
        response = medialive.delete_input(InputId=input_id)
        result = {
            'Status': 'SUCCESS',
            'Data': {},
            'ResourceId': input_id
        }

    except Exception as ex:
        print(ex)
        result = {
            'Status': 'FAILED',
            'Data': {"Exception": str(ex)},
            'ResourceId': input_id
        }

    return result
