#
# Copyright (c) 2009 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

# pylint: disable=R0903

"""Module responsible for displaying results of rho report"""

import csv
import os
import json
import sys
# pylint: disable=import-error
from ansible.module_utils.basic import AnsibleModule

EAP_CLASSIFICATIONS = {
    'JBoss_4_0_0': 'JBossAS-4',
    'JBoss_4_0_1_SP1': 'JBossAS-4',
    'JBoss_4_0_2': 'JBossAS-4',
    'JBoss_4_0_3_SP1': 'JBossAS-4',
    'JBoss_4_0_4_GA': 'JBossAS-4',
    'Branch_4_0': 'JBossAS-4',
    'JBoss_4_2_0_GA': 'JBossAS-4',
    'JBoss_4_2_1_GA': 'JBossAS-4',
    'JBoss_4_2_2_GA': 'JBossAS-4',
    'JBoss_4_2_3_GA': 'JBossAS-4',
    'JBoss_5_0_0_GA': 'JBossAS-5',
    'JBoss_5_0_1_GA': 'JBossAS-5',
    'JBoss_5_1_0_GA': 'JBossAS-5',
    'JBoss_6.0.0.Final': 'JBossAS-6',
    'JBoss_6.1.0.Final': 'JBossAS-6',
    '1.0.1.GA': 'JBossAS-7',
    '1.0.2.GA': 'JBossAS-7',
    '1.1.1.GA': 'JBossAS-7',
    '1.2.0.CR1': 'JBossAS-7',
    '1.2.0.Final': 'WildFly-8',
    '1.2.2.Final': 'WildFly-8',
    '1.2.4.Final': 'WildFly-8',
    '1.3.0.Beta3': 'WildFly-8',
    '1.3.0.Final': 'WildFly-8',
    '1.3.3.Final': 'WildFly-8',
    '1.3.4.Final': 'WildFly-9',
    '1.4.2.Final': 'WildFly-9',
    '1.4.3.Final': 'WildFly-9',
    '1.4.4.Final': 'WildFly-10',
    '1.5.0.Final': 'WildFly-10',
    '1.5.1.Final': 'WildFly-10',
    '1.5.2.Final': 'WildFly-10',
    'JBPAPP_4_2_0_GA': 'EAP-4.2',
    'JBPAPP_4_2_0_GA_C': 'EAP-4.2',
    'JBPAPP_4_3_0_GA': 'EAP-4.3',
    'JBPAPP_4_3_0_GA_C': 'EAP-4.3',
    'JBPAPP_5_0_0_GA': 'EAP-5.0.0',
    'JBPAPP_5_0_1': 'EAP-5.0.1',
    'JBPAPP_5_1_0': 'EAP-5.1.0',
    'JBPAPP_5_1_1': 'EAP-5.1.1',
    'JBPAPP_5_1_2': 'EAP-5.1.2',
    'JBPAPP_5_2_0': 'EAP-5.2.0',
    '1.1.2.GA-redhat-1': 'EAP-6.0.0',
    '1.1.3.GA-redhat-1': 'EAP-6.0.1',
    '1.2.0.Final-redhat-1': 'EAP-6.1.0',
    '1.2.2.Final-redhat-1': 'EAP-6.1.1',
    '1.3.0.Final-redhat-2': 'EAP-6.2',
    '1.3.3.Final-redhat-1': 'EAP-6.3',
    '1.3.4.Final-redhat-1': 'EAP-6.3',
    '1.3.5.Final-redhat-1': 'EAP-6.3',
    '1.3.6.Final-redhat-1': 'EAP-6.4',
    '1.3.7.Final-redhat-1': 'EAP-6.4',
    '1.4.4.Final-redhat-1': 'EAP-7.0',
    '1.5.1.Final-redhat-1': 'EAP-7.0'
}

BRMS_CLASSIFICATIONS = {
    '6.4.0.Final-redhat-3': 'BRMS 6.3.0',
    '6.3.0.Final-redhat-5': 'BRMS 6.2.0',
    '6.2.0.Final-redhat-4': 'BRMS 6.1.0',
    '6.0.3-redhat-6': 'BRMS 6.0.3',
    '6.0.3-redhat-4': 'BRMS 6.0.2',
    '6.0.2-redhat-6': 'BRMS 6.0.1',
    '6.0.2-redhat-2': 'BRMS 6.0.0',
    '5.3.1.BRMS': 'BRMS 5.3.1',
    '5.3.0.BRMS': 'BRMS 5.3.0',
    '5.2.0.BRMS': 'BRMS 5.2.0',
    '5.1.0.BRMS': 'BRMS 5.1.0',
    '5.0.2.BRMS': 'BRMS 5.0.2',
    '5.0.1.BRMS': 'BRMS 5.0.1',
    'drools-core-5.0.0': 'BRMS 5.0.0',
    '6.5.0.Final': 'Drools 6.5.0'
}

FUSE_CLASSIFICATIONS = {
    'redhat-630187': 'Fuse-6.3.0',
    'redhat-621084': 'Fuse-6.2.1',
    'redhat-620133': 'Fuse-6.2.0',
    'redhat-611412': 'Fuse-6.1.1',
    'redhat-610379': 'Fuse-6.1.0',
    'redhat-60024': 'Fuse-6.0.0',
}


def iteritems(dictionary):
    """Iterate over a dictionary's (key, value) pairs using Python 2 or 3.

    :param dictionary: the dictionary to iterate over.
    """

    if sys.version_info.major == 2:
        return dictionary.iteritems()

    return dictionary.items()


def safe_next(iterator):
    """Get the next item from an iterator, in Python 2 or 3.

    :param iterator: the iterator.
    """

    if sys.version_info.major == 2:
        return iterator.next()

    return next(iterator)


# JBoss versions are processed separately from other *-ver data
# because they merge data from two input facts and include deploy
# dates as well as version strings.
def process_jboss_versions(host_vars):
    """Get JBoss version information from the host_vars."""

    lines = []

    if 'jboss_jar_ver' in host_vars:
        lines.extend(host_vars['jboss_jar_ver']['stdout_lines'])
    if 'jboss_run_jar_ver' in host_vars:
        lines.extend(host_vars['jboss_run_jar_ver']['stdout_lines'])

    jboss_releases = []
    deploy_dates = []
    for line in lines:
        if line:
            version, deploy_date = line.split('**')
            deploy_dates.append(deploy_date)
            if version in EAP_CLASSIFICATIONS:
                jboss_releases.append(EAP_CLASSIFICATIONS[version])
            elif version.strip():
                jboss_releases.append('Unknown-Release: ' + version)

    if not jboss_releases:
        return {}

    return {
        'installed_versions': '; '.join(jboss_releases),
        'deploy_dates': '; '.join(deploy_dates)
    }


def classify_releases(lines, classifications):
    """Classify release strings using a dictionary."""

    releases = []
    for line in lines:
        if line:
            if line in classifications:
                releases.append(classifications[line])
            else:
                releases.append('Unknown-Release: ' + line)

    return '; '.join(releases)


def process_addon_versions(host_vars):
    """Classify release strings for JBoss BRMS and FUSE."""

    result = {}

    def classify(key, classifications):
        """Classify a particular key."""

        if key in host_vars:
            result[key] = classify_releases(
                host_vars[key]['stdout_lines'],
                classifications)

    classify('brms_kie_api_ver', BRMS_CLASSIFICATIONS)
    classify('brms_drools_core_ver', BRMS_CLASSIFICATIONS)
    classify('brms_kie_war_ver', BRMS_CLASSIFICATIONS)

    classify('activemq-ver', FUSE_CLASSIFICATIONS)
    classify('camel-ver', FUSE_CLASSIFICATIONS)
    classify('cxf-ver', FUSE_CLASSIFICATIONS)

    return result


class Results(object):
    """The class Results contains the functionality to parse
    data passed in from the playbook and to output it in the
    csv format in the file path specified.
    """

    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.file_path = module.params['file_path']
        self.vals = module.params['vals']
        self.all_vars = module.params['all_vars']
        self.desired_facts = module.params['desired_facts']

    def write_to_csv(self):
        """Output report data to file in csv format"""

        # Make sure the controller expanded the default option.
        assert self.desired_facts != ['default']

        keys = set(self.desired_facts)

        # Special processing for JBoss facts.
        for _, host_vars in iteritems(self.all_vars):
            uuid = host_vars['connection.uuid']
            host_vals = safe_next((vals
                                   for vals in self.vals
                                   if vals['connection.uuid'] == uuid))

            host_vals.update(process_jboss_versions(host_vars))
            host_vals.update(process_addon_versions(host_vars))

        normalized_path = os.path.normpath(self.file_path)
        with open(normalized_path, 'w') as write_file:
            # Construct the CSV writer
            writer = csv.DictWriter(
                write_file, sorted(keys), delimiter=',')

            # Write a CSV header if necessary
            file_size = os.path.getsize(normalized_path)
            if file_size == 0:
                writer.writeheader()

            # Write the data
            for data in self.vals:
                writer.writerow(data)


def main():
    """Function to trigger collection of results and write
    them to csv file
    """

    fields = {
        "name": {"required": True, "type": "str"},
        "file_path": {"required": True, "type": "str"},
        "vals": {"required": True, "type": "list"},
        "all_vars": {"required": True, "type": "dict"},
        "desired_facts": {"required": True, "type": "list"}
    }

    module = AnsibleModule(argument_spec=fields)

    results = Results(module=module)
    results.write_to_csv()
    vals = json.dumps(results.vals)
    module.exit_json(changed=False, meta=vals)


if __name__ == '__main__':
    main()
