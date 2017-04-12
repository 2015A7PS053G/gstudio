''' -- imports from python libraries -- '''
import json

''' -- imports from installed packages -- '''
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import GSystemType, Group, Node, GSystem  #, Triple
from gnowsys_ndf.ndf.models import node_collection

from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required
from gnowsys_ndf.ndf.views.methods import get_language_tuple

''' -- common db queries -- '''

@login_required
@get_execution_time
def node_create_edit(request,
                    group_id=None,
                    member_of=None,
                    detail_url_name=None,
                    node_type='GSystem',
                    node_id=None):
    '''
    creation as well as edit of node
    '''
    # check for POST method to node update operation
    if request.method == "POST":

        # put validations
        if node_type not in node_collection.db.connection._registered_documents.keys():
            raise ValueError('Improper node_type passed')

        kwargs={}
        group_name, group_id = Group.get_group_name_id(group_id)

        if node_id: # existing node object
            node_obj = Node.get_node_by_id(node_id)

        else: # create new
            kwargs={
                    'group_set': group_id,
                    'member_of': GSystemType.get_gst_name_id(member_of)[1]
                    }
            node_obj = node_collection.collection[node_type]()

        language = get_language_tuple(request.POST.get('language', None))
        node_obj.fill_gstystem_values(request=request,
                                    language=language,
                                            **kwargs)
        node_obj.save(group_id=group_id)
        node_id = node_obj['_id']

        return HttpResponseRedirect(reverse(detail_url_name, kwargs={'group_id': group_id, 'node_id': node_id}))