#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

import json
import logging

from dateutil import parser

from .enrich import Enrich, metadata

class PuppetForgeEnrich(Enrich):

    def get_elastic_mappings(self):

        mapping = """
        {
            "properties": {
                "summary_analyzed": {
                  "type": "string",
                  "index":"analyzed"
                  }
           }
        } """

        return {"items":mapping}


    def get_identities(self, item):
        """ Return the identities from an item """
        identities = []

        user = self.get_sh_identity(item, self.get_field_author())
        identities.append(user)

        return identities

    def get_field_author(self):
        return 'owner'

    def get_sh_identity(self, item, identity_field=None):

        entry = item

        if 'data' in item and type(item) == dict:
            entry = item['data']

        identity = {}
        identity['username'] = None
        identity['email'] = None
        identity['name'] = None

        if  identity_field in entry:
            identity['username'] = entry[identity_field]['username']
        return identity


    @metadata
    def get_rich_item(self, item):
        eitem = {}

        for f in self.RAW_FIELDS_COPY:
            if f in item:
                eitem[f] = item[f]
            else:
                eitem[f] = None
        # The real data
        entry = item['data']

        # data fields to copy
        copy_fields = ["downloads", "module_group", "supported",
                       "name", "slug", "issues_url", "superseded_by",
                       "homepage_url", "feedback_score", "deprecated_for",
                       "endorsement"]
        for f in copy_fields:
            if f in entry:
                eitem[f] = entry[f]
            else:
                eitem[f] = None
        # Fields which names are translated
        map_fields = {}
        for f in map_fields:
            if f in entry:
                eitem[map_fields[f]] = entry[f]

        # Enrich dates
        eitem["created_at"] = parser.parse(entry["created_at"]).isoformat()
        eitem["updated_at"] = parser.parse(entry["updated_at"]).isoformat()
        eitem["deprecated_at"] = None
        if entry["deprecated_at"]:
            eitem["deprecated_at"] = parser.parse(entry["deprecated_at"]).isoformat()

        if self.sortinghat:
            eitem.update(self.get_item_sh(item))

        eitem.update(self.get_grimoire_fields(eitem["created_at"], "module"))

        # TODO
        # Releases, probably as events

        return eitem