import json
import logging
import traceback

import numpy as np
import pandas as pd

from datetime import datetime


class FileTransform(object):

    def __init__(self, file_=None, json_=None, df_data=None, output_file=None, *args, **kwargs):
        if file_:
            self.file_ = file_
            self.data = pd.read_csv(self.file_, sep='\t')
        else:
            self.data = df_data
        self.json_ = json_
        self.json_ = json.loads(self.json_)
        self.data_ = self.data.copy()
        self.output_file = output_file
        self._is_valid = True
        self._transform_rules = []
        self._validation_rules = []
        self.validation_errors = []

    def validate(self):
        # unique column validation
        if self.json_.get('unique_column'):
            unique_columns = self.json_.get('unique_column')
            self._unique_column_validation(unique_columns)
        # remove duplicate rows, considering first entry as original
        if self.json_.get('remove_duplicates'):
            self._remove_duplicates()
        # validate incoming data
        if self.json_.get('validation_rules'):
            # compile valid rules
            self._compile_validation_rules()
            # process validation rules
            self._process_validation_rules()
        if self._is_valid:
            self._compile_transform_rules()
            return True
        else:
            return False

    def _unique_column_validation(self, unique_columns):
        data_size = self.data.size
        unique_rows_size = self.data.drop_duplicates(subset=unique_columns).size
        if data_size > unique_rows_size:
            self._is_valid = False
            self.validation_errors.append({"unique_columns": "Duplicate rows found!"})

    def _compile_validation_rules(self):
        self._is_valid = False
        self._validation_rules = self.json_.get('validation_rules')

    def _compile_transform_rules(self):
        # building column rules
        for _dict in self.json_.get('transform_rules'):
            column_name = _dict.get('column')
            for r in _dict.get('rules'):
                self._transform_rules.append({
                    'column_name': column_name,
                    'method_name': r
                })

    def _remove_duplicates(self, keep='first'):
        logging.info("removing duplicate rows, keeping the first row as original")
        self.data.drop_duplicates(keep=keep, inplace=True)

    # method to initiate column wise validation based on _validation_rules.
    def _process_validation_rules(self):
        for rule_ in self._validation_rules:
            if rule_.get('required'):
                self._validate_required(rule_)
            if rule_.get('length'):
                self._validate_length(rule_)
            if rule_.get('type'):
                self._validate_type(rule_)
        if not self.validation_errors:
            self._is_valid = True

    def process(self):
        for rule in self._transform_rules:
            try:
                method_ = '_' + rule.get('method_name')
                self.__getattribute__(method_)(rule.get('column_name'))
            except Exception as e:
                logging.error(traceback.format_exc())
                return 400, "Unable to apply the rule {} on column {}".format(rule.get('method_name'), rule.get('column_name')), None
        date = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename = 'GL_clean_file' + date + '.txt' if not self.output_file else self.output_file
        self.data_.to_csv(filename, sep='\t', encoding='utf-8', index=False)
        return 200, "File processed successfully!!!!", filename

    def _remove_leading_space(self, column_name):
        logging.info("removing leading space from {}".format(column_name))
        self.data_[column_name] = self.data[column_name].str.lstrip()

    def _remove_trailing_space(self, column_name):
        logging.info("removing trailing space from {}".format(column_name))
        self.data_[column_name] = self.data[column_name].str.rstrip()

    def _remove_leading_zero(self, column_name):
        logging.info("removing leading zero from {}".format(column_name))
        self.data_[column_name] = self.data[column_name].str.lstrip('0')

    def _remove_column(self, column_name):
        logging.info("removing {} from data".format(column_name))
        self.data_ = self.data.drop(column_name, axis=1)

    def _empty_to_zero(self, column_name):
        logging.info("Applying empty to zero on {}".format(column_name))
        self.data_[column_name] = self.data[column_name].replace(r'\s+', np.nan, regex=True).fillna(0)

    def _make_to_decimal(self, column_name):
        logging.info("Type conversion to float on {}".format(column_name))
        self.data_[column_name] = self.data[column_name].astype('float')

    def _add_leading_zeros(self, column_name):
        logging.info("Adding leading zeros to {}".format(column_name))
        self.data_[column_name] = self.data[column_name].apply(lambda x: '{0:0>10}'.format(x))

    def _remove_whitespace_between(self, column_name):
        logging.info("Removing spaces in between from {} ".format(column_name))
        self.data_[column_name] = self.data[column_name].str.replace('  ', '')

    def _replace_values(self, column_name):
        logging.info("Replace values in {} ".format(column_name))
        self.data_[column_name] = self.data[column_name].str.replace('-', '')
    
    def _get_abs(self, column_name):
        logging.info("Removing negative from {}".format(column_name))
        self.data_[column_name] = abs(self.data[column_name])

    def _change_date_format(self, column_name):
        logging.info("Changing date format of {}".format(column_name))
        self.data_[column_name] = pd.to_datetime(self.data[column_name], format='%m%d%Y', errors='coerce')

    def _remove_special_characters(self, column_name):
        logging.info("Removing special characters from {}".format(column_name))
        self.data_[column_name] = self.data[column_name].str.replace(r'[^\w\s]+', ' ')

    def _validate_required(self, rule):
        column_name = rule.get('column')
        if not self.data_[column_name].isnull().any():
            if (self.data_[column_name].astype(str).str.len() > 0).all():
                return
            else:
                self.validation_errors.append({column_name: '{} is required.'.format(column_name)})
                self._is_valid = False
        else:
            self.validation_errors.append({column_name: '{} is required.'.format(column_name)})

    def _validate_type(self, rule):
        column_name = rule.get('column')
        column_type = rule.get('type').lower()
        required = rule.get('required')
        method_ = '_' + 'validate_' + column_type
        self.__getattribute__(method_)(column_name, required)

    def _validate_length(self, rule):
        column_name = rule.get('column')
        column_length = rule.get('length')
        if (self.data_[column_name].astype(str).str.strip().str.len() > column_length).any():
            self.validation_errors.append(
                {column_name + '_length': "{} length greater than {}".format(column_name, column_length)})
            self._is_valid = False

    def _validate_currency(self, column_name, required=True):
        try:
            col_data = self.data_[column_name]
            if not required:
                col_data = col_data.dropna()
            col_data.astype(str).str.replace('-', '').astype(float)
        except:
            self.validation_errors.append(
                {column_name + '_': "Invalid type for {} expected float.".format(column_name)})
            self._is_valid = False

    def _validate_string(self, column_name, required=True):
        try:
            col_data = self.data_[column_name]
            if not required:
                col_data = col_data.dropna()
            col_data.astype(str)
        except:
            self.validation_errors.append(
                {column_name + '_': "Invalid type for {} expected string.".format(column_name)})
            self._is_valid = False

    def _validate_numeric(self, column_name, required=True):
        try:
            col_data = self.data_[column_name]
            if not required:
                col_data = col_data.dropna()
            col_data.astype(int)
        except:
            self.validation_errors.append(
                {column_name + '_': "Invalid type for {} expected integer.".format(column_name)})
            self._is_valid = False

    def _validate_date(self, column_name, required=True):
        try:
            col_data = self.data_[column_name]
            if not required:
                col_data = col_data.dropna()
            pd.to_datetime(col_data, format='%m/%d/%Y')
        except ValueError:
            self.validation_errors.append(
                {column_name + '_': "Invalid format for {} expected MM/DD/YYYY.".format(column_name)})
            self._is_valid = False
