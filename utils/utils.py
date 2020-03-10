import os
import json
import stat
import fnmatch
import logging
import paramiko

import numpy as np
import pandas as pd

from datetime import datetime

from django.db import connection

from .generic_utils import FileTransform
from masters.models import ClientsTools, ClientExtractSettings, ClientExtractorDetails, DestinationRules, \
    RulesetDetails, ProcessLogs, RulesetMaster

cursor = connection.cursor()


class ProcessFile(object):
    sftp = None
    sftp_host = None
    sftp_user = None
    sftp_password = None
    sftp_port = None
    sftp_in = None
    sftp_out = None
    sftp_key = None

    set_id = None
    rule_set_id = None
    file_type = None
    file_start = None
    delimiter = None

    source_columns = []
    destination_columns = []
    source_columns_wo_blank = []
    source_columns_required = []
    blank_columns = []
    db_rules = []
    mandatory_source_columns = []

    def __init__(self, client_id, tool_id, destination_file_id,  file_data=None, file_name=None):
        """
        :param client_id:
        :param tool_id:
        :param destination_file_id:
        """
        self.sftp = None
        self.sftp_host = None
        self.sftp_user = None
        self.sftp_password = None
        self.sftp_port = None
        self.sftp_in = None
        self.sftp_out = None
        self.sftp_key = None

        self.set_id = None
        self.rule_set_id = None
        self.file_type = None
        self.file_start = None
        self.delimiter = None

        self.source_columns = []
        self.destination_columns = []
        self.source_columns_wo_blank = []
        self.source_columns_required = []
        self.blank_columns = []
        self.db_rules = []

        self.client_id = client_id
        self.tool_id = tool_id
        self.destination_file_id = destination_file_id
        self.file_data = file_data
        self.file_ = file_name

        self.separator = '\t'
        self.config_JSON = {}
        self.source_destination_map = {}

        self.files_to_be_processed = []
        self.messages = []

    def process(self):

        try:
            self.get_sftp_credentials()
        except:
            return ["Unable to fetch SFTP credentials."]
        try:
            self.establish_sftp_connection()
        except:
            return ["Unable to establish a secure SFTP connection."]
        try:
            self.get_current_extractor()
        except:
            return ["Unable to fetch Client Extractor settings."]
        try:
            self.get_required_files()
        except:
            return ["Unable to read the files from SFTP location."]
        try:
            self.get_extractor_details()
        except:
            return ["Unable to fetch Client Extractor Details."]
        if not self.destination_columns:
            return ["Destination columns not configured."]
        self.build_columns_list()
        self.build_configuration()

        if not self.files_to_be_processed:
            return ["Unable to find any files with the given specification. Please check the configurations."]
        for file_ in self.files_to_be_processed:
            local_file = 'TMP_' + file_
            remote_file = self.sftp_in + '/' + file_
            self.sftp.get(remote_file, local_file)
            self.validate_checksum()
            process_log = ProcessLogs(client_id=self.client_id, dest_file_id=self.destination_file_id,rec_file_name=file_,
                                      tool_id=self.tool_id, user=1)

            data = pd.read_csv(local_file, sep=self.separator, dtype={})
            missing_source_columns = [column_name for column_name in self.source_columns_wo_blank if column_name not in list(data.columns)]
            if missing_source_columns:
                data[[str(i) for i in missing_source_columns]] = pd.DataFrame(
                    [[np.nan for i in missing_source_columns]])
                # self.messages.append(
                #     {"message": "One or more missing columns in the source file", "filename": file_, "status": 400})
                # os.remove(local_file)
                # continue

            data = data[self.source_columns_wo_blank]
            data.columns = self.source_columns_required
            data = data.reindex(columns=[*data.columns.tolist(), *self.blank_columns])
            # missing columns
            missing_columns = list(set(self.destination_columns) - set(data.columns))
            if missing_columns:
                data[missing_columns] = pd.DataFrame([['' for i in range(len(missing_columns))]], index=data.index)
            data = data[self.destination_columns]

            local_processed_file = 'processed_' + file_

            f = FileTransform(json_=json.dumps(self.config_JSON), df_data=data, output_file=local_processed_file)
            if f.validate():
                status_code, message, cleaned_file_name = f.process()
                if status_code == 200:
                    self.sftp.put(cleaned_file_name, self.sftp_out + '/' + file_)
                    self.messages.append({"message": message, "filename": file_, "status": status_code})
                    os.remove(cleaned_file_name)
                else:
                    self.messages.append({"message": message, "filename": file_, "status": status_code})
            else:
                errors = f.validation_errors
                self.messages.append({"message": errors, "filename": file_, "status": 400})
            os.remove(local_file)
            process_log.save()
        return self.messages

    def api_process(self):
        try:
            self.get_sftp_credentials()
        except:
            return "Unable to fetch SFTP credentials."
        try:
            self.establish_sftp_connection()
        except:
            return "Unable to establish a secure SFTP connection."
        try:
            self.get_current_extractor()
        except:
            return {"message": "Unable to fetch Client Extractor settings.", "status": 400}
        try:
            self.get_extractor_details()
        except:
            return {"message": "Unable to fetch Client Extractor Details.", "status": 400}
        if not self.destination_columns:
            return {"message": "Destination columns not configured.", "status": 400}
        self.build_columns_list()
        self.build_configuration()

        # Things to be done just for API call
        data = pd.DataFrame.from_dict(self.file_data)
        missing_source_columns = [column_name for column_name in self.source_columns_wo_blank if
                                  column_name not in list(data.columns)]
        if missing_source_columns:
            data[[str(i) for i in missing_source_columns]] = pd.DataFrame([[np.nan for i in missing_source_columns]])
            # return {"message": "One or more missing columns in the source file", "filename": "######", "status": 400}

        data = data[self.source_columns_wo_blank]
        data.columns = self.source_columns_required
        data = data.reindex(columns=[*data.columns.tolist(), *self.blank_columns])
        # missing columns
        missing_columns = list(set(self.destination_columns) - set(data.columns))
        if missing_columns:
            data[missing_columns] = pd.DataFrame([['' for i in range(len(missing_columns))]], index=data.index)
        data = data[self.destination_columns]

        f = FileTransform(json_=json.dumps(self.config_JSON), df_data=data)
        if f.validate():
            date = datetime.now().strftime("%Y%m%dT%H%M%S")
            self.file_ += '_' + date + '.txt'
            status_code, message, cleaned_file_name = f.process()
            if status_code == 200:
                self.sftp.put(cleaned_file_name, self.sftp_out + '/' + self.file_)
                os.remove(cleaned_file_name)
                return {"message": message, "filename": self.file_, "status": status_code}
            else:
                return {"message": message, "filename": self.file_, "status": status_code}
        else:
            errors = f.validation_errors
            return {"message": errors, "filename": self.file_, "status": 400}

    def get_sftp_credentials(self):
        sftp_details = ClientsTools.objects.get(client_id=self.client_id, tool_id=self.tool_id)
        self.sftp_host = sftp_details.sftp_server
        self.sftp_user = sftp_details.sftp_user
        self.sftp_password = sftp_details.sftp_pwd
        self.sftp_port = int(sftp_details.sftp_port)
        self.sftp_in = sftp_details.sftp_in
        self.sftp_out = sftp_details.sftp_out

    def establish_sftp_connection(self):
        try:
            transport = paramiko.Transport((self.sftp_host, self.sftp_port))
            transport.connect(None, self.sftp_user, self.sftp_password, self.sftp_key)
            self.sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            print("SFTP Connection Error Occurred : " + str(e))

    @staticmethod
    def rules_lookup(rules, _ids):
        rules_id = [x[0] for x in rules]
        rules_name = [x[1] for x in rules]
        s = []
        for _id in _ids:
            s.append(rules_name[rules_id.index(int(_id))])
        return s

    def get_current_extractor(self):
        current_extractor = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id,
                                                              dest_file_id=self.destination_file_id)
        self.set_id = current_extractor.settings_id
        self.rule_set_id = current_extractor.ruleset_id
        self.file_type = current_extractor.data_format
        self.file_start = current_extractor.file_name_start
        delimiter = current_extractor.column_delimiter
        self.separator = "|" if delimiter == "pipe" else "," if delimiter == "comma" else '\t'

    def get_extractor_details(self):
        extractor_details = ClientExtractorDetails.objects.filter(settings_id=self.set_id).order_by('ordinal')
        required_list = [(x.detail_id, x.source_column, x.dest_column) for x in extractor_details]
        self.source_columns = [x[1] for x in required_list]
        self.destination_columns = [x[2] for x in required_list]

    def get_required_files(self):
        """
        get files to be processed from the SFTP server.
        """
        file_match = self.file_start + '*.' + self.file_type
        for file_ in self.sftp.listdir_attr(self.sftp_in):
            # checks for whether folder/regular file
            if stat.S_ISREG(file_.st_mode):
                if fnmatch.fnmatch(file_.filename, file_match):
                    self.files_to_be_processed.append(file_.filename)

    def build_columns_list(self):
        """
        build column list to be included in the output file.
        """
        for i, x in enumerate(self.source_columns):
            if x != '[BLANK]':
                self.source_destination_map[x] = self.destination_columns[i]
                self.source_columns_wo_blank.append(x)
                self.source_columns_required.append(self.destination_columns[i])
            else:
                self.blank_columns.append(self.destination_columns[i])

    def validate_checksum(self):
        '''local_file_data = open(local_file, "rb").read()
                remote_file_data = sftp.open(in_folder +'/'+ Extractor).read()
                md1 = hashlib.md5(local_file_data).hexdigest()
                md2 = hashlib.md5(remote_file_data).hexdigest()
                valid_checksum = False
                if md1 == md2:
                    valid_checksum = True
                    print(md1)'''
        return True

    def build_configuration(self):
        rules = self.get_rules()
        rule_set = self.get_required_rule_set()
        unique_columns = self.get_unique_columns()
        transformation_rules = []
        for rule_ in rule_set:
            if rule_[1]:
                transformation_rules.append(
                    {'column': rule_[0], 'rules': self.rules_lookup(rules, rule_[1].split(','))})

        self.config_JSON['transform_rules'] = transformation_rules

        validation_rules = []
        for rule_ in rule_set:
            if rule_[0] not in [i.get('column') for i in validation_rules]:
                validation_rules.append(
                    {'column': rule_[0], 'type': rule_[2], 'length': rule_[3], 'required': True if rule_[4] else False})

        self.config_JSON['validation_rules'] = validation_rules

        if unique_columns:
            self.config_JSON['unique_column'] = unique_columns

    @staticmethod
    def get_rules():
        return [(i.rule_id, i.rule_name) for i in DestinationRules.objects.all()]

    def get_required_rule_set(self):
        return [(i.column_name, i.rules, i.column_type, i.column_length, i.required) for i in
                RulesetDetails.objects.filter(ruleset_id=self.rule_set_id)]

    def get_unique_columns(self):
        unique_columns = []
        columns = RulesetMaster.objects.get(ruleset_id=self.rule_set_id).uniq_flds
        if columns:
            unique_columns = [i.strip() for i in columns.split(',')]
        return unique_columns
